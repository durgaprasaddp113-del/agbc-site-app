#!/usr/bin/env python3
"""
MINIMAL NOC filter fix - only changes filter logic, no JSX rewriting
Run from: C:\Apps\agbc-site-app\
Command:  python fix_noc_minimal.py
"""
import os, shutil, re
from datetime import datetime

APP = r"src\App.js"
if not os.path.exists(APP):
    print("ERROR: src\\App.js not found"); input(); exit(1)

bk = APP + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(APP, bk)
print(f"Backup: {bk}")

with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

changes = 0

# Find NOCModule position
noc_start = app.find("const NOCModule = (")
if noc_start == -1:
    noc_start = app.find("const NOCModule=(")
if noc_start == -1:
    print("ERROR: NOCModule not found"); input(); exit(1)

noc_section = app[noc_start:]

# ── Fix 1: Rewrite ONLY the filter block using regex ─────────────────────────
filter_pattern = re.compile(
    r'const filtered = nocs\.filter\(n => \{[\s\S]*?\n  \}\);',
    re.MULTILINE
)
match = filter_pattern.search(noc_section)
if match:
    NEW_FILTER = '''const filtered = nocs.filter(n => {
    const pid1 = String(n.pid || "").toLowerCase();
    const pid2 = String(fProject || "").toLowerCase();
    if (fProject !== "All" && pid1 !== pid2) return false;
    if (fAuth !== "All" && (n.authority || "") !== fAuth) return false;
    if (fStatus !== "All" && (n.status || "") !== fStatus) return false;
    if (fExpiry === "expiring" && !isExpiringSoon(n.expiryDate, n.status)) return false;
    if (fExpiry === "expired"  && !isExpired(n.expiryDate, n.status)) return false;
    if (search) {
      const q = search.toLowerCase();
      const hay = [n.nocNum,n.authority,n.nocType,n.responsible,n.desc].filter(Boolean).join(" ").toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });'''
    noc_section = noc_section[:match.start()] + NEW_FILTER + noc_section[match.end():]
    app = app[:noc_start] + noc_section
    changes += 1
    print("Fix 1: Filter logic updated")
else:
    print("WARN: Filter block not found")

# ── Fix 2: Fix n.pid to be lowercase in useNOCs ──────────────────────────────
hook_start = app.find("function useNOCs()")
if hook_start != -1:
    hook_end = hook_start + 3000
    chunk = app[hook_start:hook_end]
    # Replace any pid: mapping
    new_chunk = re.sub(
        r"pid:\s*[(\s]*n\.project_id\s*\|\|\s*\"\"[)\s]*,",
        'pid: String(n.project_id || "").toLowerCase(),',
        chunk
    )
    if new_chunk != chunk:
        app = app[:hook_start] + new_chunk + app[hook_end:]
        changes += 1
        print("Fix 2: n.pid stored as lowercase")
    else:
        print("WARN: pid mapping not matched")

# ── Fix 3: Fix project dropdown value to be lowercase ────────────────────────
# Find the project dropdown INSIDE NOCModule and fix option values
noc_section = app[noc_start:]

# Use regex to find option tags for project inside NOCModule
opt_pattern = re.compile(
    r'\{projects\.map\(p=><option\s+key=\{p\.id\}\s+value=\{[^}]+\}>[^<]+</option>\)\}'
)
# Find all matches in noc_section
for m in opt_pattern.finditer(noc_section):
    old_opt = m.group(0)
    # Replace with lowercase value version
    new_opt = '{(projects||[]).map(p=><option key={p.id} value={String(p.id).toLowerCase()}>{p.number} \u2014 {p.name}</option>)}'
    noc_section = noc_section[:m.start()] + new_opt + noc_section[m.end():]
    app = app[:noc_start] + noc_section
    changes += 1
    print("Fix 3: Project dropdown option values lowercased")
    # Only fix first occurrence in NOC module
    break

# ── Fix 4: Fix fProject onChange to set lowercase value ──────────────────────
noc_section = app[noc_start:]

# Find all onChange handlers for fProject and ensure they lowercase
old_on = 'onChange={e=>setFProject(e.target.value)}'
new_on = 'onChange={e=>setFProject(String(e.target.value).toLowerCase())}'
if old_on in noc_section:
    noc_section = noc_section.replace(old_on, new_on, 1)
    app = app[:noc_start] + noc_section
    changes += 1
    print("Fix 4: fProject onChange lowercases value")

old_on2 = 'onChange={e=>setFProject(e.target.value||"All")}'
new_on2 = 'onChange={e=>setFProject(String(e.target.value||"All").toLowerCase())}'
if old_on2 in noc_section:
    noc_section = noc_section.replace(old_on2, new_on2, 1)
    app = app[:noc_start] + noc_section
    changes += 1
    print("Fix 4b: fProject onChange lowercases value")

old_on3 = 'onChange={e => { const v = e.target.value; setFProject(v); }}'
new_on3 = 'onChange={e => setFProject(String(e.target.value).toLowerCase())}'
if old_on3 in noc_section:
    noc_section = noc_section.replace(old_on3, new_on3, 1)
    app = app[:noc_start] + noc_section
    changes += 1
    print("Fix 4c: fProject onChange lowercases value")

# ── Fix 5: Fix navFilter useEffect ───────────────────────────────────────────
noc_section = app[noc_start:]
ue_pattern = re.compile(
    r'useEffect\(\(\) => \{[\s\S]*?setFProject[\s\S]*?\}, \[navFilter\]\);'
)
ue_match = ue_pattern.search(noc_section)
if ue_match:
    NEW_UE = '''useEffect(() => {
    if (navFilter.projectId) setFProject(String(navFilter.projectId).toLowerCase());
    else setFProject("All");
    if (navFilter.status) setFStatus(navFilter.status);
    else setFStatus("All");
    setFExpiry("All");
  }, [navFilter]);'''
    noc_section = noc_section[:ue_match.start()] + NEW_UE + noc_section[ue_match.end():]
    app = app[:noc_start] + noc_section
    changes += 1
    print("Fix 5: navFilter useEffect updated")
else:
    print("WARN: navFilter useEffect not found")

# ── Write ─────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 50)
print(f"Done! {changes} fixes applied.")
print(f"Backup: {bk}")
print()
print("Now run: set CI=false && npm run build")
print("Then:    npx vercel --prod")
print("=" * 50)
input("Press Enter to exit...")
