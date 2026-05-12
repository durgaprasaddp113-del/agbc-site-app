import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
changes = 0

# The fix: change useEffect dependency from [navFilter] to [navFilter.projectId]
# This prevents the effect from firing on every render

# Find all useEffect with navFilter dependency in MR/LPO/NOC
for i,l in enumerate(lines):
    if "}, [navFilter]);" in l:
        # Check context - near setFProject
        ctx = "".join(lines[max(0,i-8):i+1])
        if "setFProject" in ctx:
            lines[i] = lines[i].replace("}, [navFilter]);", "}, [navFilter.projectId]);")
            changes += 1
            print(f"FIX: navFilter dep fixed at L{i+1}")

# Also fix MR dropdown option values to use lowercase UUID
# MR dropdown at L5618 - check option values
for i,l in enumerate(lines):
    if i > 5610 and i < 5630:
        if "option" in l and "p.id" in l and "value={p.id}" in l:
            lines[i] = l.replace("value={p.id}", "value={String(p.id).toLowerCase()}")
            changes += 1
            print(f"FIX: MR option value lowercase at L{i+1}")

# LPO dropdown at L5964 area
for i,l in enumerate(lines):
    if i > 5956 and i < 5976:
        if "option" in l and "p.id" in l and "value={p.id}" in l:
            lines[i] = l.replace("value={p.id}", "value={String(p.id).toLowerCase()}")
            changes += 1
            print(f"FIX: LPO option value lowercase at L{i+1}")

# NOC dropdown at L11424 area - find option values
for i,l in enumerate(lines):
    if i > 11420 and i < 11435:
        if "option" in l and "p.id" in l and "value={p.id}" in l:
            lines[i] = l.replace("value={p.id}", "value={String(p.id).toLowerCase()}")
            changes += 1
            print(f"FIX: NOC option value lowercase at L{i+1}")

# Verify
print("\n=== useEffect dependencies after fix ===")
for i,l in enumerate(lines):
    if "navFilter" in l and "}," in l and "useEffect" in "".join(lines[max(0,i-5):i+1]):
        print(f"L{i+1}: {s(l.rstrip())[:100]}")

with open(APP,"w",encoding="utf-8") as f:
    f.writelines(lines)

print(f"\nSaved. Changes: {changes}")
print("RUN: set CI=false && npm run build")
print("     git add src/App.js && git commit -m 'fix: navFilter dep + filter options' && git push")
input("\nPress Enter...")
