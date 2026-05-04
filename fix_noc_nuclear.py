#!/usr/bin/env python3
"""
NUCLEAR NOC filter fix — rewrites state declarations + toolbar completely
Run from: C:\Apps\agbc-site-app\
Command:  python fix_noc_nuclear.py
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

# ── Find NOCModule ────────────────────────────────────────────────────────────
noc_start = app.find("const NOCModule = (")
if noc_start == -1:
    noc_start = app.find("const NOCModule=(")
if noc_start == -1:
    print("ERROR: NOCModule not found"); input(); exit(1)
print(f"✅ Found NOCModule at {noc_start}")

changes = 0

# ─────────────────────────────────────────────────────────────────────────────
# FIX 1 — Replace ALL useState declarations for NOC filters
# Find the block that has fProject, fAuth, fStatus, fExpiry, search states
# Replace with clean versions using plain "All" defaults
# ─────────────────────────────────────────────────────────────────────────────

# Pattern: find any line with fProject useState inside NOCModule
lines = app.split('\n')
noc_line = None
for i, line in enumerate(lines):
    if 'const NOCModule' in line:
        noc_line = i
        break

if noc_line is None:
    print("ERROR: NOCModule line not found"); input(); exit(1)

# Find and fix state lines within NOCModule (within 50 lines of start)
fixed_states = []
for i in range(noc_line, min(noc_line + 80, len(lines))):
    line = lines[i]
    # Fix fProject initial state
    if 'fProject' in line and 'useState' in line:
        lines[i] = '  const [fProject,  setFProject]  = useState("All");'
        fixed_states.append('fProject')
    # Fix fAuth initial state  
    elif 'fAuth' in line and 'useState' in line and 'fProject' not in line:
        lines[i] = '  const [fAuth,      setFAuth]      = useState("All");'
        fixed_states.append('fAuth')
    # Fix fStatus initial state
    elif 'fStatus' in line and 'useState' in line and 'fProject' not in line:
        lines[i] = '  const [fStatus,    setFStatus]    = useState("All");'
        fixed_states.append('fStatus')
    # Fix fExpiry initial state
    elif 'fExpiry' in line and 'useState' in line:
        lines[i] = '  const [fExpiry,    setFExpiry]    = useState("All");'
        fixed_states.append('fExpiry')
    # Fix search initial state
    elif '"search"' not in line and 'setSearch' in line and 'useState' in line and '[search' in line:
        lines[i] = '  const [search,     setSearch]     = useState("");'

if fixed_states:
    print(f"✅ Fix 1: Reset states: {', '.join(fixed_states)}")
    changes += 1

app = '\n'.join(lines)

# ─────────────────────────────────────────────────────────────────────────────
# FIX 2 — Replace navFilter useEffect inside NOCModule
# ─────────────────────────────────────────────────────────────────────────────
# Find the useEffect that reads navFilter inside NOCModule
noc_section = app[noc_start:]

# Multiple possible patterns for the useEffect
ue_patterns = [
    # Pattern 1
    """  useEffect(() => {
    setFProject(navFilter.projectId ? String(navFilter.projectId) : "All");
    setFStatus(navFilter.status || "All");
    setFExpiry(navFilter.expiry || "All");
  }, [navFilter]);""",
    # Pattern 2
    """  useEffect(() => {
    setFProject(navFilter.projectId || "All");
    setFStatus(navFilter.status || "All");
    setFExpiry(navFilter.expiry || "All");
  }, [navFilter]);""",
    # Pattern 3
    """  useEffect(() => {
    setFProject(navFilter.projectId || "All");
    setFStatus(navFilter.status || "All");
    setFExpiry("All");
  }, [navFilter]);""",
]

NEW_UE = """  useEffect(() => {
    if (navFilter.projectId) setFProject(String(navFilter.projectId).toLowerCase());
    else setFProject("All");
    if (navFilter.status) setFStatus(navFilter.status);
    else setFStatus("All");
    setFExpiry("All");
  }, [navFilter]);"""

replaced_ue = False
for p in ue_patterns:
    if p in noc_section:
        noc_section = noc_section.replace(p, NEW_UE, 1)
        app = app[:noc_start] + noc_section
        replaced_ue = True
        changes += 1
        print("✅ Fix 2: navFilter useEffect rewritten")
        break
if not replaced_ue:
    print("⚠️  Fix 2: useEffect pattern not found")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 3 — Completely rewrite the NOC filter toolbar
# Find the toolbar div by looking for the All Projects select
# ─────────────────────────────────────────────────────────────────────────────
noc_section = app[noc_start:]

# Find the toolbar - look for the div that contains fProject Sel
# Strategy: find "All Projects" option and replace the whole toolbar block

# Find the outer flex div that contains the filter dropdowns
toolbar_start_marker = '      {/* Toolbar */}\n      <div className="flex flex-wrap items-center justify-between gap-3 mb-3">'
toolbar_start_marker2 = '      <div className="flex flex-wrap items-center justify-between gap-3 mb-3">'

# Find all the filter dropdowns by looking for fProject
proj_idx = noc_section.find('<Sel value={fProject}')
if proj_idx == -1:
    proj_idx = noc_section.find('value={fProject}')

if proj_idx != -1:
    # Go back to find the parent div
    search_back = noc_section[max(0, proj_idx-500):proj_idx]
    # Find last <div before proj_idx
    last_div = search_back.rfind('<div')
    outer_div_start = proj_idx - len(search_back) + last_div
    
    # Now find the closing of this toolbar section
    # Look for the next major section after the filter dropdowns
    # The toolbar ends before "Active filters" or before "{/* Status filter pills */}"
    after_toolbar_markers = [
        '      {(fProject !== "All"',
        '      {/* Active filter indicator */}',
        '      {/* Status filter pills */}',
        '      <div className="flex flex-nowrap sm:flex-wrap gap-1.5 mb-3',
    ]
    
    toolbar_end = -1
    for m in after_toolbar_markers:
        idx = noc_section.find(m, proj_idx)
        if idx != -1:
            if toolbar_end == -1 or idx < toolbar_end:
                toolbar_end = idx
    
    if toolbar_end != -1:
        old_toolbar = noc_section[outer_div_start:toolbar_end]
        
        NEW_TOOLBAR = '''      {/* NOC Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
        <div className="flex flex-col gap-2 flex-1 min-w-0">
          <SearchBar value={search} onChange={e=>setSearch(e.target.value)} placeholder="NOC no, authority, type..."/>
          <select
            value={fProject}
            onChange={e => setFProject(e.target.value)}
            style={{width:"100%",padding:"8px 12px",fontSize:"14px",border:"1px solid #e2e8f0",borderRadius:"8px",background:"white",outline:"none"}}>
            <option value="All">All Projects</option>
            {(projects||[]).map(p=>(
              <option key={p.id} value={String(p.id).toLowerCase()}>
                {p.number} — {p.name}
              </option>
            ))}
          </select>
          <select
            value={fAuth}
            onChange={e => setFAuth(e.target.value)}
            style={{width:"100%",padding:"8px 12px",fontSize:"14px",border:"1px solid #e2e8f0",borderRadius:"8px",background:"white",outline:"none"}}>
            <option value="All">All Authorities</option>
            {NOC_AUTHORITIES.map(a=><option key={a} value={a}>{a}</option>)}
          </select>
          <select
            value={fExpiry}
            onChange={e => setFExpiry(e.target.value)}
            style={{width:"100%",padding:"8px 12px",fontSize:"14px",border:"1px solid #e2e8f0",borderRadius:"8px",background:"white",outline:"none"}}>
            <option value="All">All Dates</option>
            <option value="expiring">Expiring Soon (30 days)</option>
            <option value="expired">Already Expired</option>
          </select>
        </div>
        <div className="flex gap-2 shrink-0">
          <button onClick={exportNocExcel} className="text-xs bg-green-50 border border-green-200 text-green-700 font-semibold px-3 py-1.5 rounded-lg hover:bg-green-100">⬇ Excel</button>
          <button onClick={exportNocPDF} className="text-xs bg-red-50 border border-red-200 text-red-700 font-semibold px-3 py-1.5 rounded-lg hover:bg-red-100">⬇ PDF</button>
          <AddBtn onClick={openCreate} label="New NOC"/>
        </div>
      </div>
      {/* Active filter pills */}
      {(fProject !== "All" || fAuth !== "All" || fExpiry !== "All" || fStatus !== "All") && (
        <div className="flex flex-wrap gap-2 mb-3 items-center">
          <span className="text-xs text-slate-500 font-semibold">Active filters:</span>
          {fProject !== "All" && (
            <span className="text-xs bg-blue-100 text-blue-700 border border-blue-200 px-2 py-1 rounded-full font-semibold flex items-center gap-1">
              📁 {(projects||[]).find(p=>String(p.id).toLowerCase()===fProject)?.number || "Project"}
              <button onClick={()=>setFProject("All")} className="ml-1 font-bold hover:text-blue-900">×</button>
            </span>
          )}
          {fAuth !== "All" && (
            <span className="text-xs bg-purple-100 text-purple-700 border border-purple-200 px-2 py-1 rounded-full font-semibold flex items-center gap-1">
              🏛 {fAuth}
              <button onClick={()=>setFAuth("All")} className="ml-1 font-bold hover:text-purple-900">×</button>
            </span>
          )}
          {fExpiry !== "All" && (
            <span className="text-xs bg-orange-100 text-orange-700 border border-orange-200 px-2 py-1 rounded-full font-semibold flex items-center gap-1">
              📅 {fExpiry==="expiring"?"Expiring Soon":"Expired"}
              <button onClick={()=>setFExpiry("All")} className="ml-1 font-bold hover:text-orange-900">×</button>
            </span>
          )}
          {fStatus !== "All" && (
            <span className="text-xs bg-green-100 text-green-700 border border-green-200 px-2 py-1 rounded-full font-semibold flex items-center gap-1">
              ✅ {fStatus}
              <button onClick={()=>setFStatus("All")} className="ml-1 font-bold hover:text-green-900">×</button>
            </span>
          )}
          <button onClick={()=>{setFProject("All");setFAuth("All");setFExpiry("All");setFStatus("All");setSearch("");}}
            className="text-xs text-red-500 hover:text-red-700 font-semibold border border-red-200 px-2 py-1 rounded-full">
            Clear All
          </button>
        </div>
      )}
'''
        noc_section = noc_section[:outer_div_start] + NEW_TOOLBAR + noc_section[toolbar_end:]
        app = app[:noc_start] + noc_section
        changes += 1
        print("✅ Fix 3: Toolbar completely rewritten with native <select> elements")
    else:
        print("⚠️  Fix 3: Could not find toolbar end marker")
else:
    print("⚠️  Fix 3: fProject dropdown not found")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 4 — Rewrite filter logic to match lowercase UUID
# ─────────────────────────────────────────────────────────────────────────────
noc_section = app[noc_start:]

OLD_FILTER_PATTERNS = [
    # My previous rewrite
    """  const filtered = nocs.filter(n => {
    // Project filter — compare both as lowercase strings to handle UUID case differences
    if (fProject !== "All") {
      const pid1 = (n.pid || "").toString().toLowerCase().trim();
      const pid2 = (fProject || "").toString().toLowerCase().trim();
      if (!pid1 || pid1 !== pid2) return false;
    }""",
    # Original
    """  const filtered = nocs.filter(n => {
    if (fProject!=="All" && n.pid!==fProject) return false;""",
    # Previous fix
    """  const filtered = nocs.filter(n => {
    if (fProject && fProject!=="All" && String(n.pid)!==String(fProject)) return false;""",
]

NEW_FILTER = """  const filtered = nocs.filter(n => {
    if (fProject !== "All") {
      const nPid = String(n.pid || "").toLowerCase().trim();
      const fPid = String(fProject || "").toLowerCase().trim();
      if (nPid !== fPid) return false;
    }
    if (fAuth !== "All") {
      if ((n.authority || "") !== fAuth) return false;
    }
    if (fStatus !== "All") {
      if ((n.status || "") !== fStatus) return false;
    }
    if (fExpiry === "expiring" && !isExpiringSoon(n.expiryDate, n.status)) return false;
    if (fExpiry === "expired"  && !isExpired(n.expiryDate, n.status))       return false;
    if (search) {
      const q = search.toLowerCase();
      const hay = [n.nocNum,n.authority,n.nocType,n.responsible,n.desc].filter(Boolean).join(" ").toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });"""

filter_pattern = re.compile(r'const filtered = nocs\.filter\(n => \{[\s\S]*?\}\);', re.MULTILINE)
match = filter_pattern.search(noc_section)
if match:
    noc_section = noc_section[:match.start()] + NEW_FILTER + noc_section[match.end():]
    app = app[:noc_start] + noc_section
    changes += 1
    print("✅ Fix 4: Filter logic rewritten")
else:
    print("⚠️  Fix 4: Filter block not found")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 5 — Ensure n.pid is stored as lowercase in useNOCs hook
# ─────────────────────────────────────────────────────────────────────────────
noc_hook_start = app.find("function useNOCs()")
if noc_hook_start != -1:
    hook_section = app[noc_hook_start:noc_hook_start+2000]
    # Find pid: line
    pid_patterns = [
        "pid: n.project_id || \"\",",
        "pid:          n.project_id           || \"\",",
        "pid: (n.project_id || \"\").toString().toLowerCase(),",
        "pid:        (n.project_id || \"\").toString().toLowerCase(),",
    ]
    for pp in pid_patterns:
        if pp in hook_section:
            new_pp = "pid: (n.project_id || \"\").toString().toLowerCase(),"
            hook_section = hook_section.replace(pp, new_pp, 1)
            app = app[:noc_hook_start] + hook_section + app[noc_hook_start+2000:]
            changes += 1
            print("✅ Fix 5: n.pid stored as lowercase UUID")
            break
    else:
        print("⚠️  Fix 5: pid line not found in useNOCs")
else:
    print("⚠️  Fix 5: useNOCs hook not found")

# ─────────────────────────────────────────────────────────────────────────────
# WRITE
# ─────────────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 55)
print(f"✅ Done! {changes} fixes applied to App.js")
print(f"   Backup: {bk}")
print()
print("Next:")
print("  set CI=false && npm run build")
print("  npx vercel --prod")
print("=" * 55)
input("\nPress Enter to exit...")
