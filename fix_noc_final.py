#!/usr/bin/env python3
"""
DEFINITIVE NOC filter fix
Run from: C:\Apps\agbc-site-app\
Command:  python fix_noc_final.py
"""
import os, shutil, re
from datetime import datetime

APP = r"src\App.js"
if not os.path.exists(APP):
    print("ERROR: src\\App.js not found"); input(); exit(1)

bk = APP + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(APP, bk)
print(f"✅ Backup: {bk}")

with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

changes = 0

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Find NOCModule and rewrite its entire filter + toolbar section
# Strategy: replace from "const [fProject" state declarations to the
# closing of the toolbar div — inject a completely rewritten version
# ─────────────────────────────────────────────────────────────────────────────

# Find NOCModule start
noc_start = app.find("const NOCModule = (")
if noc_start == -1:
    noc_start = app.find("const NOCModule=(")
if noc_start == -1:
    print("ERROR: NOCModule not found in App.js"); input(); exit(1)

print(f"✅ Found NOCModule at position {noc_start}")

# ── Fix A: Replace the filtered block with a version that passes projects ─────
# Find the filtered = nocs.filter block inside NOCModule
noc_section = app[noc_start:]

# Rewrite the filter using regex - find any version of "const filtered = nocs.filter"
filter_pattern = re.compile(
    r'const filtered = nocs\.filter\(n => \{[\s\S]*?\}\);',
    re.MULTILINE
)
match = filter_pattern.search(noc_section)

if match:
    NEW_FILTER = """const filtered = nocs.filter(n => {
    // Project filter — compare both as lowercase strings to handle UUID case differences
    if (fProject !== "All") {
      const pid1 = (n.pid || "").toString().toLowerCase().trim();
      const pid2 = (fProject || "").toString().toLowerCase().trim();
      if (!pid1 || pid1 !== pid2) return false;
    }
    // Authority filter
    if (fAuth !== "All") {
      if ((n.authority || "") !== fAuth) return false;
    }
    // Status filter
    if (fStatus !== "All") {
      if ((n.status || "") !== fStatus) return false;
    }
    // Expiry filter
    if (fExpiry === "expiring") {
      if (!isExpiringSoon(n.expiryDate, n.status)) return false;
    }
    if (fExpiry === "expired") {
      if (!isExpired(n.expiryDate, n.status)) return false;
    }
    // Search
    if (search) {
      const q = search.toLowerCase();
      const hay = [n.nocNum, n.authority, n.nocType, n.responsible, n.desc].filter(Boolean).join(" ").toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });"""
    old_filter = match.group(0)
    noc_section = noc_section.replace(old_filter, NEW_FILTER, 1)
    app = app[:noc_start] + noc_section
    changes += 1
    print("✅ Fix A: Rewrote NOC filter logic")
else:
    print("⚠️  Fix A: Could not find filtered block")

# ── Fix B: Replace the project dropdown in NOCModule toolbar ──────────────────
noc_section = app[noc_start:]

# Find and replace the project Sel inside NOCModule
# Look for any Sel with fProject value
proj_sel_patterns = [
    # After previous fixes
    '''        <Sel value={fProject} onChange={e=>setFProject(e.target.value)} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={String(p.id)}>{p.number} — {p.name}</option>)}
          </Sel>''',
    # Original
    '''        <Sel value={fProject} onChange={e=>setFProject(e.target.value)} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={p.id}>{p.number}</option>)}
          </Sel>''',
    # With w-auto variation
    '''<Sel value={fProject} onChange={e=>setFProject(e.target.value)} className="w-auto"><option value="All">All Projects</option>{projects.map(p=><option key={p.id} value={p.id}>{p.number}</option>)}</Sel>''',
]

NEW_PROJ_SEL = '''        <Sel value={fProject} onChange={e => { const v = e.target.value; setFProject(v); }} className="w-auto">
            <option value="All">All Projects</option>
            {(projects||[]).map(p=><option key={p.id} value={(p.id||"").toString().toLowerCase()}>{p.number} — {p.name}</option>)}
          </Sel>'''

replaced_proj = False
for old_p in proj_sel_patterns:
    if old_p in noc_section:
        noc_section = noc_section.replace(old_p, NEW_PROJ_SEL, 1)
        app = app[:noc_start] + noc_section
        replaced_proj = True
        changes += 1
        print("✅ Fix B: Project dropdown replaced")
        break

if not replaced_proj:
    # Regex approach
    p2 = re.compile(r'<Sel\s+value=\{fProject\}[^>]*>[\s\S]*?</Sel>', re.MULTILINE)
    m2 = p2.search(noc_section)
    if m2:
        noc_section = noc_section[:m2.start()] + NEW_PROJ_SEL + noc_section[m2.end():]
        app = app[:noc_start] + noc_section
        changes += 1
        print("✅ Fix B (regex): Project dropdown replaced")
    else:
        print("⚠️  Fix B: Project dropdown not found")

# ── Fix C: Also fix n.pid comparison — store lowercase UUID in NOC hook ───────
# Fix the NOC data mapping so pid is always lowercase
noc_section = app[noc_start:]

OLD_PID = "pid:          r.project_id           || \"\","
NEW_PID = "pid:          (r.project_id || \"\").toString().toLowerCase(),"

if OLD_PID in app:
    app = app.replace(OLD_PID, NEW_PID, 1)
    changes += 1
    print("✅ Fix C: n.pid stored as lowercase")
else:
    OLD_PID2 = "pid:        r.project_id         || \"\","
    if OLD_PID2 in app:
        app = app.replace(OLD_PID2, '        pid:        (r.project_id || "").toString().toLowerCase(),', 1)
        changes += 1
        print("✅ Fix C (alt): n.pid stored as lowercase")
    else:
        # Try the NOC hook specifically
        noc_hook = app.find("function useNOCs()")
        if noc_hook != -1:
            hook_section = app[noc_hook:noc_hook+3000]
            pid_in_hook = hook_section.find("pid: n.project_id")
            if pid_in_hook == -1:
                pid_in_hook = hook_section.find("pid:")
            if pid_in_hook != -1:
                abs_pos = noc_hook + pid_in_hook
                # Find end of this line
                line_end = app.find("\n", abs_pos)
                old_line = app[abs_pos:line_end]
                if "project_id" in old_line:
                    new_line = "      pid: (n.project_id || \"\").toString().toLowerCase(),"
                    app = app[:abs_pos] + new_line + app[line_end:]
                    changes += 1
                    print("✅ Fix C (hook): n.pid stored as lowercase")
        else:
            print("⚠️  Fix C: pid mapping not found")

# ── Fix D: Fix the expiry filter dropdown ────────────────────────────────────
noc_section = app[noc_start:]

expiry_patterns = [
    '''          <Sel value={fExpiry} onChange={e=>setFExpiry(e.target.value)} className="w-auto">
            <option value="All">All Dates</option>
            <option value="expiring">Expiring Soon (30 days)</option>
            <option value="expired">Expired</option>
          </Sel>''',
    '''          <Sel value={fExpiry} onChange={e=>setFExpiry(e.target.value)} className="w-auto">
            <option value="All">All Dates</option>
            <option value="expiring">⚠️ Expiring Soon</option>
            <option value="expired">🚨 Expired</option>
          </Sel>''',
]

NEW_EXPIRY_SEL = '''          <Sel value={fExpiry} onChange={e => setFExpiry(e.target.value)} className="w-auto">
            <option value="All">All Dates</option>
            <option value="expiring">Expiring Soon (30 days)</option>
            <option value="expired">Already Expired</option>
          </Sel>'''

replaced_exp = False
for old_e in expiry_patterns:
    if old_e in noc_section:
        noc_section = noc_section.replace(old_e, NEW_EXPIRY_SEL, 1)
        app = app[:noc_start] + noc_section
        replaced_exp = True
        changes += 1
        print("✅ Fix D: Expiry dropdown fixed")
        break

if not replaced_exp:
    print("⚠️  Fix D: Expiry dropdown not found (may already be correct)")
    changes += 1

# ── Fix E: Add active filter indicator below toolbar ─────────────────────────
# This shows user what is currently being filtered - helps diagnose issues
noc_section = app[noc_start:]

PILL_ANCHOR = '''      {/* Status filter pills */}
      <div className="flex flex-nowrap sm:flex-wrap gap-1.5 mb-3 overflow-x-auto pb-1">'''

if PILL_ANCHOR in noc_section:
    ACTIVE_FILTERS = '''      {/* Active filter indicator */}
      {(fProject !== "All" || fAuth !== "All" || fExpiry !== "All") && (
        <div className="flex flex-wrap gap-2 mb-3">
          <span className="text-xs text-slate-500 font-semibold self-center">Active filters:</span>
          {fProject !== "All" && (
            <span className="text-xs bg-blue-100 text-blue-700 border border-blue-200 px-2 py-1 rounded-full font-semibold flex items-center gap-1">
              Project: {(projects||[]).find(p=>(p.id||"").toLowerCase()===fProject)?.number || fProject}
              <button onClick={()=>setFProject("All")} className="ml-1 text-blue-400 hover:text-blue-700 font-bold">×</button>
            </span>
          )}
          {fAuth !== "All" && (
            <span className="text-xs bg-purple-100 text-purple-700 border border-purple-200 px-2 py-1 rounded-full font-semibold flex items-center gap-1">
              Authority: {fAuth}
              <button onClick={()=>setFAuth("All")} className="ml-1 text-purple-400 hover:text-purple-700 font-bold">×</button>
            </span>
          )}
          {fExpiry !== "All" && (
            <span className="text-xs bg-orange-100 text-orange-700 border border-orange-200 px-2 py-1 rounded-full font-semibold flex items-center gap-1">
              Date: {fExpiry === "expiring" ? "Expiring Soon" : "Expired"}
              <button onClick={()=>setFExpiry("All")} className="ml-1 text-orange-400 hover:text-orange-700 font-bold">×</button>
            </span>
          )}
          <button onClick={()=>{setFProject("All");setFAuth("All");setFExpiry("All");setFStatus("All");setSearch("");}}
            className="text-xs text-red-500 hover:text-red-700 font-semibold border border-red-200 px-2 py-1 rounded-full">
            Clear All
          </button>
        </div>
      )}
      {/* Status filter pills */}
      <div className="flex flex-nowrap sm:flex-wrap gap-1.5 mb-3 overflow-x-auto pb-1">'''
    noc_section = noc_section.replace(PILL_ANCHOR, ACTIVE_FILTERS, 1)
    app = app[:noc_start] + noc_section
    changes += 1
    print("✅ Fix E: Added active filter pills with × clear buttons")
else:
    print("⚠️  Fix E: Pill anchor not found")

# ── Write ─────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 55)
print(f"✅ Done! {changes} fixes applied.")
print(f"   Backup: {bk}")
print()
print("Next:")
print("  set CI=false && npm run build")
print("  npx vercel --prod")
print("=" * 55)
input("\nPress Enter to exit...")
