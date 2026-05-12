import shutil, re
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

content = "".join(lines)
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
changes = 0

# ─── FIX 1: LPO useEffect [navFilter, prefillMr] → [navFilter.projectId, prefillMr] ───
old = '}, [navFilter, prefillMr]);'
new = '}, [navFilter.projectId, prefillMr]);'
if old in content:
    content = content.replace(old, new)
    changes += 1
    print("FIX 1: LPO useEffect [navFilter, prefillMr] → [navFilter.projectId, prefillMr]")
else:
    print("SKIP 1: pattern not found")

# ─── FIX 2: MR useEffect - add navFilter.status to deps ──────────────────────────────
# L5739 shows [navFilter.projectId] but effect also sets fStatus (uses navFilter.status)
# We need [navFilter.projectId, navFilter.status] for completeness
# Find the MR useEffect that sets BOTH fStatus and fProject
lines2 = content.split('\n')
for i, l in enumerate(lines2):
    if 'navFilter.projectId]);' in l and i > 5700 and i < 5800:
        # Check context for setFStatus
        ctx = '\n'.join(lines2[max(0,i-5):i+1])
        if 'setFStatus' in ctx and 'setFProject' in ctx:
            lines2[i] = l.replace('[navFilter.projectId]);', '[navFilter.projectId, navFilter.status]);')
            content = '\n'.join(lines2)
            changes += 1
            print("FIX 2: MR useEffect deps → [navFilter.projectId, navFilter.status] at L"+str(i+1))
            break

# ─── FIX 3: Add navFilter={navFilter} to MR case statement ───────────────────────────
lines3 = content.split('\n')
for i, l in enumerate(lines3):
    if 'case "mr"' in l and 'MaterialRequests' in l and 'navFilter' not in l:
        # Insert navFilter before closing />; or last prop
        # Find the closing /> or end of line
        if '/>; ' in l or '/>;' in l:
            lines3[i] = l.replace('/>;', ' navFilter={navFilter}/>;', 1)
        elif l.rstrip().endswith('/>'):
            lines3[i] = l.rstrip()[:-2] + ' navFilter={navFilter}/>'
        else:
            lines3[i] = l.rstrip() + ' navFilter={navFilter}'
        content = '\n'.join(lines3)
        changes += 1
        print("FIX 3: navFilter={navFilter} added to MR case at L"+str(i+1))
        break

# ─── FIX 4: Add navFilter={navFilter} to LPO case statement ──────────────────────────
lines4 = content.split('\n')
for i, l in enumerate(lines4):
    if 'case "lpo"' in l and 'LPOModule' in l and 'navFilter' not in l:
        if '/>; ' in l or '/>;' in l:
            lines4[i] = l.replace('/>;', ' navFilter={navFilter}/>;', 1)
        elif l.rstrip().endswith('/>'):
            lines4[i] = l.rstrip()[:-2] + ' navFilter={navFilter}/>'
        else:
            lines4[i] = l.rstrip() + ' navFilter={navFilter}'
        content = '\n'.join(lines4)
        changes += 1
        print("FIX 4: navFilter={navFilter} added to LPO case at L"+str(i+1))
        break

# ─── Write ────────────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

# ─── Verify ───────────────────────────────────────────────────────────────────────────
print()
print("── VERIFY: All navFilter useEffect dependencies ──")
with open(APP, "r", encoding="utf-8", errors="replace") as f:
    vlines = f.readlines()

for i, l in enumerate(vlines):
    if 'navFilter' in l and ('[navFilter' in l) and '},' in l:
        flag = "✓" if 'navFilter.projectId' in l else "✗ STILL OBJECT REF"
        print(flag+" L"+str(i+1)+": "+s(l.rstrip()))

print()
print("── VERIFY: MR/LPO/NOC case statements ──")
for i, l in enumerate(vlines):
    if ('case "mr"' in l or 'case "lpo"' in l or 'case "noc"' in l) and 'Module' in l or 'MaterialRequests' in l:
        has_nf = 'navFilter={navFilter}' in l
        sym = "✓" if has_nf else "✗ MISSING"
        print(sym+" L"+str(i+1)+": "+s(l)[:150])

print()
print("="*60)
print("TOTAL FIXES:", changes)
print()
print("NOW RUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js')
print('  git commit -m "Fix: navFilter dep bug - project filter MR LPO NOC"')
print('  git push')
print("="*60)
input("Press Enter...")
