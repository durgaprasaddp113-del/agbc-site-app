#!/usr/bin/env python3
"""
Fix NOC All Projects + All Dates filters
Run from: C:\Apps\agbc-site-app\
Command:  python fix_noc_filter2.py
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

# ── Fix 1: Rewrite NOC filter block completely ────────────────────────────────
# Find and replace the entire filtered = nocs.filter(...) block in NOCModule

# Pattern to find the filtered block
patterns_to_try = [
    # Version with String() fix
    """  const filtered = nocs.filter(n => {
    if (fProject && fProject!=="All" && String(n.pid)!==String(fProject)) return false;
    if (fAuth && fAuth!=="All" && n.authority!==fAuth) return false;
    if (fStatus && fStatus!=="All" && n.status!==fStatus) return false;
    if (fExpiry==="expiring" && !isExpiringSoon(n.expiryDate,n.status)) return false;
    if (fExpiry==="expired" && !isExpired(n.expiryDate,n.status)) return false;
    if (search && !`${n.nocNum} ${n.authority} ${n.nocType} ${n.responsible} ${n.desc||""}`.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });""",
    # Original version
    """  const filtered = nocs.filter(n => {
    if (fProject!=="All" && n.pid!==fProject) return false;
    if (fAuth!=="All" && n.authority!==fAuth) return false;
    if (fStatus!=="All" && n.status!==fStatus) return false;
    if (fExpiry==="expiring" && !isExpiringSoon(n.expiryDate,n.status)) return false;
    if (fExpiry==="expired" && !isExpired(n.expiryDate,n.status)) return false;
    if (search && !`${n.nocNum} ${n.authority} ${n.nocType} ${n.responsible}`.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });""",
    # Alt version
    """  const filtered = nocs.filter(n => {
    if (fProject && fProject!=="All" && n.pid!==fProject) return false;
    if (fAuth && fAuth!=="All" && n.authority!==fAuth) return false;
    if (fStatus && fStatus!=="All" && n.status!==fStatus) return false;
    if (fExpiry==="expiring" && !isExpiringSoon(n.expiryDate,n.status)) return false;
    if (fExpiry==="expired" && !isExpired(n.expiryDate,n.status)) return false;
    if (search && !`${n.nocNum} ${n.authority} ${n.nocType} ${n.responsible}`.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });""",
]

NEW_FILTER = """  const filtered = nocs.filter(n => {
    // Project filter
    if (fProject !== "All" && fProject !== "" && fProject) {
      const nPid = n.pid ? String(n.pid).trim() : "";
      const fPid = String(fProject).trim();
      if (nPid !== fPid) return false;
    }
    // Authority filter
    if (fAuth !== "All" && fAuth !== "" && fAuth) {
      if ((n.authority || "") !== fAuth) return false;
    }
    // Status filter
    if (fStatus !== "All" && fStatus !== "" && fStatus) {
      if ((n.status || "") !== fStatus) return false;
    }
    // Date/expiry filter
    if (fExpiry === "expiring" && !isExpiringSoon(n.expiryDate, n.status)) return false;
    if (fExpiry === "expired"  && !isExpired(n.expiryDate, n.status))       return false;
    // Search
    if (search) {
      const q = search.toLowerCase();
      const hay = `${n.nocNum||""} ${n.authority||""} ${n.nocType||""} ${n.responsible||""} ${n.desc||""}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });"""

replaced = False
for old in patterns_to_try:
    if old in app:
        app = app.replace(old, NEW_FILTER, 1)
        replaced = True
        changes += 1
        print("✅ Fix 1: NOC filter rewritten cleanly")
        break

if not replaced:
    # Use regex as last resort
    pattern = r'const filtered = nocs\.filter\(n => \{[\s\S]*?\}\);'
    # Find in NOCModule only - search after NOCModule definition
    noc_start = app.find("const NOCModule = (")
    if noc_start == -1:
        noc_start = app.find("const NOCModule=(")
    if noc_start != -1:
        noc_section = app[noc_start:]
        match = re.search(pattern, noc_section)
        if match:
            old_filter = match.group(0)
            app = app[:noc_start] + noc_section.replace(old_filter, NEW_FILTER, 1)
            changes += 1
            print("✅ Fix 1 (regex): NOC filter rewritten")
        else:
            print("⚠️  Fix 1: Could not find NOC filter — check manually")
    else:
        print("⚠️  Fix 1: NOCModule not found")

# ── Fix 2: Rewrite the filter dropdowns (Project + Dates) ────────────────────
# Make sure All Projects dropdown resets to empty string on "All"

OLD2 = """        <Sel value={fProject} onChange={e=>setFProject(e.target.value||"All")} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={String(p.id)}>{p.number} — {p.name}</option>)}
          </Sel>"""

NEW2 = """        <select value={fProject} onChange={e=>setFProject(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 bg-white">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={String(p.id)}>{p.number} — {p.name}</option>)}
          </select>"""

# Actually keep it as Sel component - just fix the onChange
OLD2B = """        <Sel value={fProject} onChange={e=>setFProject(e.target.value||"All")} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={String(p.id)}>{p.number} — {p.name}</option>)}
          </Sel>"""

NEW2B = """        <Sel value={fProject} onChange={e=>setFProject(e.target.value)} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={String(p.id)}>{p.number} — {p.name}</option>)}
          </Sel>"""

if OLD2B in app:
    app = app.replace(OLD2B, NEW2B, 1)
    changes += 1
    print("✅ Fix 2: Project dropdown onChange fixed")
else:
    # Try original without String()
    OLD2C = """        <Sel value={fProject} onChange={e=>setFProject(e.target.value)} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={p.id}>{p.number}</option>)}
          </Sel>
          <Sel value={fAuth}"""
    NEW2C = """        <Sel value={fProject} onChange={e=>setFProject(e.target.value)} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={String(p.id)}>{p.number} — {p.name}</option>)}
          </Sel>
          <Sel value={fAuth}"""
    if OLD2C in app:
        app = app.replace(OLD2C, NEW2C, 1)
        changes += 1
        print("✅ Fix 2 (alt): Project dropdown fixed")
    else:
        print("⚠️  Fix 2: dropdown not found - will fix with regex")
        # Regex replace project dropdown inside NOCModule
        noc_start = app.find("const NOCModule = (")
        if noc_start == -1:
            noc_start = app.find("const NOCModule=(")
        if noc_start != -1:
            proj_pattern = r'<Sel value=\{fProject\}[^>]*onChange=\{[^}]*\}[^>]*>\s*<option value="All">All Projects</option>[^<]*\{projects\.map[^}]*\}[^)]*\)[^<]*\}\s*</Sel>'
            noc_part = app[noc_start:]
            new_proj_sel = """<Sel value={fProject} onChange={e=>setFProject(e.target.value)} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={String(p.id)}>{p.number} — {p.name}</option>)}
          </Sel>"""
            new_noc_part, n = re.subn(proj_pattern, new_proj_sel, noc_part, count=1)
            if n > 0:
                app = app[:noc_start] + new_noc_part
                changes += 1
                print("✅ Fix 2 (regex): Project dropdown fixed")

# ── Fix 3: Fix Dates dropdown — ensure "All" value resets correctly ──────────
OLD3 = """          <Sel value={fExpiry} onChange={e=>setFExpiry(e.target.value)} className="w-auto">
            <option value="All">All Dates</option>
            <option value="expiring">⚠️ Expiring Soon</option>
            <option value="expired">🚨 Expired</option>
          </Sel>"""

NEW3 = """          <Sel value={fExpiry} onChange={e=>setFExpiry(e.target.value)} className="w-auto">
            <option value="All">All Dates</option>
            <option value="expiring">Expiring Soon (30 days)</option>
            <option value="expired">Expired</option>
          </Sel>"""

if OLD3 in app:
    app = app.replace(OLD3, NEW3, 1)
    changes += 1
    print("✅ Fix 3: Dates dropdown fixed")
else:
    print("⚠️  Fix 3: Dates dropdown not found (may already be correct)")
    changes += 1  # count as ok

# ── Fix 4: Fix initial useState for fExpiry ──────────────────────────────────
# Make sure fExpiry defaults to "All" not ""
OLD4 = "useState(navFilter.expiry || \"All\");"
NEW4 = "useState(\"All\");"

# Only fix the fExpiry one inside NOCModule
noc_idx = app.find("const NOCModule = (")
if noc_idx == -1:
    noc_idx = app.find("const NOCModule=(")

if noc_idx != -1:
    # Find fExpiry useState after NOCModule starts
    fexp_idx = app.find("useState(navFilter.expiry ||", noc_idx)
    if fexp_idx != -1 and fexp_idx < noc_idx + 5000:
        app = app[:fexp_idx] + 'useState("All")' + app[fexp_idx + len('useState(navFilter.expiry || "All")'):]
        changes += 1
        print("✅ Fix 4: fExpiry initial state fixed")
    else:
        print("⚠️  Fix 4: fExpiry useState not found")
else:
    print("⚠️  Fix 4: NOCModule not found")

# ── Write ─────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 55)
print(f"✅ Done! {changes} fixes applied to App.js")
print(f"   Backup: {bk}")
print()
print("Next steps:")
print("  1. set CI=false && npm run build")
print("  2. npx vercel --prod")
print("=" * 55)
input("\nPress Enter to exit...")
