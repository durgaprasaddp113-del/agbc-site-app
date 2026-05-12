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

# ─────────────────────────────────────────────────────────────────────
# ROOT CAUSE:
#   useEffect([navFilter]) fires on EVERY render when navFilter is a
#   default `{}` parameter (new object reference each call).
#   This resets fProject to "All"/"all" immediately after user selects
#   a project, making the filter appear broken.
#
# FIX 1: Change [navFilter] → [navFilter.projectId] in all 3 modules
#   navFilter.projectId is a stable primitive (string or undefined).
#   Same value every render → effect won't fire unnecessarily.
# ─────────────────────────────────────────────────────────────────────

# Find all useEffect blocks that reset fProject based on navFilter
# Pattern: }, [navFilter]);  near a setFProject call

dep_patterns = [
    # LPO and NOC style (just projectId)
    ('}, [navFilter]);', '}, [navFilter.projectId]);'),
]

for old, new in dep_patterns:
    cnt = content.count(old)
    if cnt > 0:
        content = content.replace(old, new)
        changes += cnt
        print("FIX 1: Changed", cnt, "useEffect [navFilter] → [navFilter.projectId]")
    else:
        print("WARN 1: '}, [navFilter]);' not found, trying other patterns...")

# Also handle navFilter.status in MR's useEffect
# MR useEffect sets both fStatus AND fProject
old_mr = '}, [navFilter.projectId]);'
# Check if MR's useEffect also had status - look for adjacent setFStatus
lines2 = content.split('\n')
for i, l in enumerate(lines2):
    if 'navFilter.projectId' in l and '},' in l:
        # Check the preceding ~5 lines for setFStatus and setFProject
        context = '\n'.join(lines2[max(0,i-6):i+1])
        if 'setFStatus' in context and 'setFProject' in context:
            # This useEffect sets both - add status to dependency
            lines2[i] = lines2[i].replace(
                '}, [navFilter.projectId]);',
                '}, [navFilter.projectId, navFilter.status]);'
            )
            changes += 1
            print("FIX 1b: MR useEffect deps → [navFilter.projectId, navFilter.status]")
            break
content = '\n'.join(lines2)

# ─────────────────────────────────────────────────────────────────────
# FIX 2: Add navFilter={navFilter} to NOC case statement in App
# Line 12063: case "noc": return <NOCModule ... showToast={showToast}/>;
# ─────────────────────────────────────────────────────────────────────
old_noc = 'case "noc":   return <NOCModule nocs={nocs} loading={nocLoad} onAdd={addNoc} onUpdate={updNoc} onDelete={delNoc} projects={projects} showToast={showToast}/>;'
new_noc = 'case "noc":   return <NOCModule nocs={nocs} loading={nocLoad} onAdd={addNoc} onUpdate={updNoc} onDelete={delNoc} projects={projects} showToast={showToast} navFilter={navFilter}/>;'

if old_noc in content:
    content = content.replace(old_noc, new_noc)
    changes += 1
    print("FIX 2: navFilter={navFilter} added to NOC case statement")
else:
    print("WARN 2: NOC case exact pattern not found — trying partial match...")
    lines3 = content.split('\n')
    for i, l in enumerate(lines3):
        if 'case "noc"' in l and 'NOCModule' in l and 'navFilter' not in l:
            # Add navFilter before closing />
            lines3[i] = l.replace('showToast={showToast}/>', 'showToast={showToast} navFilter={navFilter}/>')
            if 'showToast={showToast}' not in l:
                # Try other closing
                lines3[i] = l.rstrip().rstrip(';').rstrip('>').rstrip('/') + ' navFilter={navFilter}/>;'
            content = '\n'.join(lines3)
            changes += 1
            print("FIX 2: navFilter added to NOC case (partial match) L"+str(i+1))
            break

# ─────────────────────────────────────────────────────────────────────
# FIX 3: Verify MR and LPO case statements also pass navFilter
# ─────────────────────────────────────────────────────────────────────
print()
print("── Checking MR/LPO case navFilter prop ──")
for i, l in enumerate(content.split('\n')):
    if ('case "mr"' in l or 'case "lpo"' in l) and 'Module' in l or 'MaterialRequests' in l:
        has_nf = 'navFilter' in l
        print("L"+str(i+1)+" navFilter="+str(has_nf)+": "+s(l)[:120])

# ─────────────────────────────────────────────────────────────────────
# WRITE
# ─────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

# ─────────────────────────────────────────────────────────────────────
# VERIFY
# ─────────────────────────────────────────────────────────────────────
print()
print("── VERIFY: useEffect dependencies ──")
with open(APP, "r", encoding="utf-8", errors="replace") as f:
    vlines = f.readlines()

for i, l in enumerate(vlines):
    if 'navFilter' in l and ('[navFilter' in l or 'navFilter.projectId' in l):
        if 'useEffect' in l or '},' in l:
            print("L"+str(i+1)+": "+s(l.rstrip()))

print()
print("── VERIFY: NOC case statement ──")
for i, l in enumerate(vlines):
    if 'case "noc"' in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:160])

print()
print("── VERIFY: MR useEffect block ──")
mr = next((i for i,l in enumerate(vlines) if "const MaterialRequests = (" in l), -1)
if mr != -1:
    for j in range(mr, min(mr+15,len(vlines))):
        print(str(j+1)+"\t"+s(vlines[j].rstrip()))

print()
print("="*60)
print("TOTAL FIXES:", changes)
print()
print("RUN NOW:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js')
print('  git commit -m "Fix: navFilter dependency bug causing project filter reset"')
print('  git push')
print("="*60)
input("Press Enter...")
