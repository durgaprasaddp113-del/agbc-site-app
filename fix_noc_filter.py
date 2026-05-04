#!/usr/bin/env python3
"""
Fix NOC project filter - Run from C:\Apps\agbc-site-app\
Command: python fix_noc_filter.py
"""
import os, shutil
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

# ── Fix 1: NOC filter — compare String(n.pid) === String(fProject) ────────────
# This ensures UUID vs string comparison works correctly
OLD1 = "if (fProject && fProject!==\"All\" && n.pid!==fProject) return false;"
NEW1 = "if (fProject && fProject!==\"All\" && String(n.pid)!==String(fProject)) return false;"

if OLD1 in app:
    app = app.replace(OLD1, NEW1, 1)
    changes += 1
    print("✅ Fix 1: NOC project filter comparison fixed")
else:
    # Try without the extra fProject check
    OLD1B = 'if (fProject!=="All" && n.pid!==fProject) return false;'
    NEW1B = 'if (fProject!=="All" && String(n.pid)!==String(fProject)) return false;'
    # Only replace inside NOC filtered block (find last occurrence)
    last = app.rfind(OLD1B)
    if last != -1:
        app = app[:last] + NEW1B + app[last+len(OLD1B):]
        changes += 1
        print("✅ Fix 1 (alt): NOC project filter fixed")
    else:
        print("⚠️  Fix 1: filter line not found")

# ── Fix 2: NOC useEffect — add fProject reset when navFilter changes ──────────
# Make sure fProject resets to "All" properly
OLD2 = """  useEffect(() => {
    setFProject(navFilter.projectId || "All");
    setFStatus(navFilter.status || "All");
    setFExpiry(navFilter.expiry || "All");
  }, [navFilter]);"""

NEW2 = """  useEffect(() => {
    setFProject(navFilter.projectId ? String(navFilter.projectId) : "All");
    setFStatus(navFilter.status || "All");
    setFExpiry(navFilter.expiry || "All");
  }, [navFilter]);"""

if OLD2 in app:
    app = app.replace(OLD2, NEW2, 1)
    changes += 1
    print("✅ Fix 2: NOC navFilter projectId cast to string")
else:
    print("⚠️  Fix 2: navFilter useEffect not found — skipping")

# ── Fix 3: NOC project dropdown — show project number + name ─────────────────
# Replace the NOC filter project select options
OLD3 = """        <Sel value={fProject} onChange={e=>setFProject(e.target.value||"All")} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}
          </Sel>"""

NEW3 = """        <Sel value={fProject} onChange={e=>setFProject(e.target.value||"All")} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={String(p.id)}>{p.number} — {p.name}</option>)}
          </Sel>"""

if OLD3 in app:
    app = app.replace(OLD3, NEW3, 1)
    changes += 1
    print("✅ Fix 3: Project dropdown value cast to string")
else:
    # Try original version without p.name
    OLD3B = """        <Sel value={fProject} onChange={e=>setFProject(e.target.value)} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={p.id}>{p.number}</option>)}
          </Sel>
          <Sel value={fAuth}"""
    NEW3B = """        <Sel value={fProject} onChange={e=>setFProject(e.target.value||"All")} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={String(p.id)}>{p.number} — {p.name}</option>)}
          </Sel>
          <Sel value={fAuth}"""
    if OLD3B in app:
        app = app.replace(OLD3B, NEW3B, 1)
        changes += 1
        print("✅ Fix 3 (alt): Project dropdown fixed")
    else:
        print("⚠️  Fix 3: NOC project dropdown not found")

# ── Fix 4: Also fix the NOC initial state filter ─────────────────────────────
OLD4 = '  const [fProject,  setFProject]  = useState(navFilter.projectId || "All");'
NEW4 = '  const [fProject,  setFProject]  = useState(navFilter.projectId ? String(navFilter.projectId) : "All");'

if OLD4 in app:
    app = app.replace(OLD4, NEW4, 1)
    changes += 1
    print("✅ Fix 4: Initial fProject state fixed")
else:
    print("⚠️  Fix 4: initial state not found — skipping")

# ── Write ─────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 50)
print(f"✅ Done! {changes} fixes applied.")
print(f"   Backup: {bk}")
print("\nNext: npx vercel --prod")
print("=" * 50)
input("\nPress Enter to exit...")
