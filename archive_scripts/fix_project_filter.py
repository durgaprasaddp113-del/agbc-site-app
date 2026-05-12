import shutil, re
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

total = len(lines)
print("Total lines:", total)

def s(x): return x.encode('ascii', errors='replace').decode('ascii')

# ── STEP 1: SHOW CURRENT STATE ──────────────────────────────────────
print("\n── CURRENT FILTER CONDITIONS ──")
for i, l in enumerate(lines):
    if '_fpid' in l and 'return false' in l:
        print("L"+str(i+1)+": "+s(l.rstrip()))

print("\n── CURRENT fProject INITIAL STATES ──")
for i, l in enumerate(lines):
    if 'fProject' in l and 'useState' in l:
        print("L"+str(i+1)+": "+s(l.rstrip()))

print("\n── CURRENT DROPDOWN onChange ──")
for i, l in enumerate(lines):
    if 'setFProject' in l and 'onChange' in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:160])

print("\n── useMatReqs pid line ──")
for i, l in enumerate(lines):
    if 'pid:' in l and 'project_id' in l and i < 6000:
        print("L"+str(i+1)+": "+s(l.rstrip()))

# ── STEP 2: APPLY FIXES ─────────────────────────────────────────────
print("\n── APPLYING FIXES ──")
content = "".join(lines)
changes = 0

# FIX A: The core bug - "All" vs "all" case mismatch
# onChange does toLowerCase("All") = "all"
# but filter checks fProject !== "All" (capital)
# SOLUTION: Change the filter condition to use _fpid !== "all"

patterns = [
    # Exact match variant 1
    ('if (fProject !== "All" && _fpid && _pid !== _fpid) return false;',
     'if (_fpid && _fpid !== "all" && _pid !== _fpid) return false;'),
    # Exact match variant 2 (with spaces)
    ('if (fProject !== "All" && _fpid && _pid !== _fpid)  return false;',
     'if (_fpid && _fpid !== "all" && _pid !== _fpid) return false;'),
]

for old, new in patterns:
    cnt = content.count(old)
    if cnt > 0:
        content = content.replace(old, new)
        changes += cnt
        print("FIX A: Replaced", cnt, "instance(s) of filter condition")

if changes == 0:
    print("WARN A: Standard pattern not found - trying line-by-line fix...")
    new_lines = []
    for l in content.split('\n'):
        if '_fpid' in l and 'fProject' in l and '"All"' in l and 'return false' in l:
            # Replace the condition
            fixed = re.sub(
                r'if\s*\(fProject\s*!==\s*"All"\s*&&\s*_fpid\s*&&\s*_pid\s*!==\s*_fpid\)',
                'if (_fpid && _fpid !== "all" && _pid !== _fpid)',
                l
            )
            new_lines.append(fixed)
            changes += 1
            print("  Fixed line:", s(fixed.strip()))
        else:
            new_lines.append(l)
    content = '\n'.join(new_lines)

# FIX B: useMatReqs pid - store as lowercase
for old, new in [
    ('pid: r.project_id || "",',   'pid: String(r.project_id||"").toLowerCase(),'),
    ("pid: r.project_id || '',",   "pid: String(r.project_id||'').toLowerCase(),"),
    ('pid: r.project_id||"",',     'pid: String(r.project_id||"").toLowerCase(),'),
]:
    if old in content:
        content = content.replace(old, new, 1)
        changes += 1
        print("FIX B: useMatReqs pid now lowercase")
        break
else:
    if 'String(r.project_id' in content:
        print("INFO B: useMatReqs pid already fixed")
    else:
        print("WARN B: useMatReqs pid pattern not found")

# FIX C: Ensure fProject "All" default is safe
# MR uses navFilter.projectId || "All" - this is fine, "All" won't become "all" until user interacts
# But let's also lowercase the navFilter.projectId to be safe
for old, new in [
    ('useState(navFilter.projectId || "All")',
     'useState(String(navFilter.projectId||"").toLowerCase() || "all")'),
]:
    cnt = content.count(old)
    if cnt > 0:
        content = content.replace(old, new)
        changes += cnt
        print("FIX C: navFilter.projectId initial state now lowercase, default='all'")

# FIX D: Ensure setFProject in navFilter effect uses lowercase
for old, new in [
    ('setFProject(navFilter.projectId || "All")',
     'setFProject(String(navFilter.projectId||"").toLowerCase() || "all")'),
]:
    cnt = content.count(old)
    if cnt > 0:
        content = content.replace(old, new)
        changes += cnt
        print("FIX D: navFilter useEffect setFProject now lowercase")

# FIX E: Ensure the All Projects option value is lowercase "all" to match
for old, new in [
    ('<option value="All">All Projects</option>',
     '<option value="all">All Projects</option>'),
]:
    cnt = content.count(old)
    if cnt > 0:
        content = content.replace(old, new)
        changes += cnt
        print("FIX E: 'All Projects' option value changed to lowercase 'all' (", cnt, "places)")

# ── STEP 3: WRITE ───────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

# ── STEP 4: VERIFY ──────────────────────────────────────────────────
print("\n── VERIFY: FILTER CONDITIONS AFTER FIX ──")
with open(APP, "r", encoding="utf-8", errors="replace") as f:
    new_lines = f.readlines()

found = 0
for i, l in enumerate(new_lines):
    if '_fpid' in l and 'return false' in l:
        print("L"+str(i+1)+": "+s(l.rstrip()))
        found += 1
print("Total filter conditions:", found, "(expected 3)")

print("\n── VERIFY: fProject initial states ──")
for i, l in enumerate(new_lines):
    if 'fProject' in l and 'useState' in l:
        print("L"+str(i+1)+": "+s(l.rstrip()))

print("\n── VERIFY: useMatReqs pid ──")
for i, l in enumerate(new_lines):
    if 'pid:' in l and 'project_id' in l and i < 6000:
        print("L"+str(i+1)+": "+s(l.rstrip()))

print()
print("="*60)
print("TOTAL FIXES APPLIED:", changes)
print("Backup:", bk)
print()
print("NOW RUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js')
print('  git commit -m "Fix: project filter MR LPO NOC case mismatch"')
print('  git push')
print("="*60)
input("Press Enter...")
