#!/usr/bin/env python3
"""
Find duplicate states and fix NOC filters definitively
Run from: C:\Apps\agbc-site-app\
Command:  python fix_noc_states.py
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
    content = f.read()

# ── Find NOCModule boundaries ─────────────────────────────────────────────────
noc_start = content.find("const NOCModule = (")
if noc_start == -1:
    noc_start = content.find("const NOCModule=(")
if noc_start == -1:
    print("ERROR: NOCModule not found"); input(); exit(1)

# Find end of NOCModule (next top-level const/function after it)
noc_end = len(content)
for marker in ["\nconst NOCModule", "\nexport default function", "\nfunction useNOCs"]:
    idx = content.find(marker, noc_start + 100)
    if idx != -1 and idx < noc_end:
        noc_end = idx

noc_body = content[noc_start:noc_end]
print(f"NOCModule: chars {noc_start} to {noc_end}")

# ── Check for duplicate state declarations ────────────────────────────────────
print("\n--- Checking for duplicate states ---")
for varname in ["fProject", "fAuth", "fStatus", "fExpiry", "search"]:
    count = noc_body.count(f"[{varname},")
    print(f"  [{varname}, set...] useState declarations: {count}")
    if count > 1:
        print(f"  *** DUPLICATE FOUND for {varname}! This is the bug. ***")

# ── Fix: Extract NOCModule, remove duplicate states, rewrite ─────────────────
lines = noc_body.split('\n')
new_lines = []
seen_states = set()

for line in lines:
    stripped = line.strip()
    # Check if this is a useState declaration for filter states
    is_filter_state = False
    for v in ["fProject", "fAuth", "fStatus", "fExpiry"]:
        if f"[{v}," in line and "useState" in line:
            if v in seen_states:
                print(f"  Removed duplicate: {stripped[:60]}")
                is_filter_state = True
                break
            else:
                seen_states.add(v)
                # Normalize the state declaration
                if v == "fProject":
                    line = '  const [fProject,  setFProject]  = useState("All");'
                elif v == "fAuth":
                    line = '  const [fAuth,      setFAuth]      = useState("All");'
                elif v == "fStatus":
                    line = '  const [fStatus,    setFStatus]    = useState("All");'
                elif v == "fExpiry":
                    line = '  const [fExpiry,    setFExpiry]    = useState("All");'
                print(f"  Normalized: {line.strip()}")
                is_filter_state = True
                break
    if not is_filter_state:
        new_lines.append(line)
    else:
        if is_filter_state and not (f"[{v}," in line and seen_states and v not in [s for s in seen_states if s != v]):
            new_lines.append(line)

# Actually let's redo this more carefully
lines = noc_body.split('\n')
new_lines = []
seen_states = {}

for i, line in enumerate(lines):
    skip = False
    for v in ["fProject", "fAuth", "fStatus", "fExpiry"]:
        if f"[{v}," in line and "useState" in line:
            if v in seen_states:
                print(f"  REMOVED duplicate line {i}: {line.strip()[:70]}")
                skip = True
            else:
                seen_states[v] = i
                # Normalize
                indent = len(line) - len(line.lstrip())
                spaces = " " * indent
                if v == "fProject":
                    line = spaces + 'const [fProject,  setFProject]  = useState("All");'
                elif v == "fAuth":
                    line = spaces + 'const [fAuth,      setFAuth]      = useState("All");'
                elif v == "fStatus":
                    line = spaces + 'const [fStatus,    setFStatus]    = useState("All");'
                elif v == "fExpiry":
                    line = spaces + 'const [fExpiry,    setFExpiry]    = useState("All");'
            break
    if not skip:
        new_lines.append(line)

new_noc_body = '\n'.join(new_lines)

# ── Fix filter logic ──────────────────────────────────────────────────────────
filter_pattern = re.compile(
    r'const filtered = nocs\.filter\(n => \{[\s\S]*?\n  \}\);',
    re.MULTILINE
)
match = filter_pattern.search(new_noc_body)
if match:
    NEW_FILTER = '''const filtered = nocs.filter(n => {
    const pid = String(n.pid || "").toLowerCase();
    const fpid = String(fProject || "").toLowerCase();
    if (fProject !== "All" && fpid && pid !== fpid) return false;
    if (fAuth !== "All" && (n.authority || "") !== fAuth) return false;
    if (fStatus !== "All" && (n.status || "") !== fStatus) return false;
    if (fExpiry === "expiring" && !isExpiringSoon(n.expiryDate, n.status)) return false;
    if (fExpiry === "expired" && !isExpired(n.expiryDate, n.status)) return false;
    if (search) {
      const q = search.toLowerCase();
      const hay = [n.nocNum, n.authority, n.nocType, n.responsible, n.desc]
        .filter(Boolean).join(" ").toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });'''
    new_noc_body = new_noc_body[:match.start()] + NEW_FILTER + new_noc_body[match.end():]
    print("Fixed: filter logic rewritten")

# ── Fix useEffect for navFilter ───────────────────────────────────────────────
ue_pat = re.compile(
    r'useEffect\(\(\) => \{[\s\n]*(?:if \(navFilter|setF)[\s\S]*?\}, \[navFilter\]\);'
)
ue_match = ue_pat.search(new_noc_body)
if ue_match:
    NEW_UE = '''useEffect(() => {
    setFProject(navFilter.projectId ? String(navFilter.projectId).toLowerCase() : "All");
    setFStatus(navFilter.status || "All");
    setFExpiry("All");
  }, [navFilter]);'''
    new_noc_body = new_noc_body[:ue_match.start()] + NEW_UE + new_noc_body[ue_match.end():]
    print("Fixed: navFilter useEffect")

# ── Fix n.pid to be lowercase in useNOCs hook ─────────────────────────────────
hook_start = content.find("function useNOCs()")
if hook_start != -1:
    chunk = content[hook_start:hook_start+3000]
    new_chunk = re.sub(
        r"pid:\s*\(?n\.project_id\s*\|\|\s*['\"]['\"][\s)]*,",
        'pid: String(n.project_id || "").toLowerCase(),',
        chunk
    )
    if new_chunk != chunk:
        content = content[:hook_start] + new_chunk + content[hook_start+3000:]
        print("Fixed: n.pid stored as lowercase in useNOCs")

# ── Fix project dropdown option values ───────────────────────────────────────
# Inside NOCModule, replace option values for projects
old_opt1 = '{projects.map(p=><option key={p.id} value={p.id}>{p.number}</option>)}'
new_opt  = '{(projects||[]).map(p=><option key={p.id} value={String(p.id).toLowerCase()}>{p.number} — {p.name}</option>)}'
if old_opt1 in new_noc_body:
    new_noc_body = new_noc_body.replace(old_opt1, new_opt, 1)
    print("Fixed: project option values lowercased")

old_opt2 = '{projects.map(p=><option key={p.id} value={String(p.id).toLowerCase()}>{p.number} — {p.name}</option>)}'
if old_opt2 in new_noc_body:
    new_noc_body = new_noc_body.replace(old_opt2, new_opt, 1)
    print("Fixed: project option values normalized")

# ── Fix fProject onChange to lowercase ───────────────────────────────────────
for old_on in [
    'onChange={e=>setFProject(e.target.value)}',
    'onChange={e=>setFProject(e.target.value||"All")}',
    'onChange={e => setFProject(String(e.target.value).toLowerCase())}',
    'onChange={e => { const v = e.target.value; setFProject(v); }}',
]:
    if old_on in new_noc_body:
        new_noc_body = new_noc_body.replace(old_on,
            'onChange={e=>setFProject(String(e.target.value).toLowerCase())}', 1)
        print(f"Fixed: fProject onChange → lowercase")
        break

# ── Rebuild content ───────────────────────────────────────────────────────────
content = content[:noc_start] + new_noc_body + content[noc_end:]

# ── Write ─────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 55)
print("Done! App.js updated.")
print(f"Backup: {bk}")
print()
print("Now run:")
print("  set CI=false && npm run build")
print("  (if OK) npx vercel --prod")
print("=" * 55)
input("Press Enter to exit...")
