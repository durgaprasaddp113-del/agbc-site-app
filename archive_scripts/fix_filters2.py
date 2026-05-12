import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

changes = 0

# From diagnostic:
# MR filter at L5476: if (fProject!=="All" && m.pid!==fProject) return false;
# LPO filter at L5745: if (fProject!=="All" && l.pid!==fProject) return false;  
# NOC filter at L11108: if (fProject!=="All" && n.pid!==fProject) return false;

# Fix each filter line directly
fixes = [
    (5475, 'm.pid', 'm'),   # MR L5476 (0-based 5475)
    (5744, 'l.pid', 'l'),   # LPO L5745 (0-based 5744)
    (11107, 'n.pid', 'n'),  # NOC L11108 (0-based 11107)
]

for line_0based, pid_ref, var in fixes:
    l = lines[line_0based]
    if 'fProject!=="All"' in l or 'fProject !== "All"' in l:
        lines[line_0based] = (
            f'        const _pid  = String({var}.pid || "").toLowerCase().trim();\n'
            f'        const _fpid = String(fProject || "").toLowerCase().trim();\n'
            f'        if (_fpid && _fpid !== "all" && _pid !== _fpid) return false;\n'
        )
        changes += 1
        print(f"FIX L{line_0based+1}: {var} filter fixed")

# Also fix the dropdown onChange for MR/LPO/NOC to use toLowerCase
# Find setFProject onChange in MR/LPO/NOC dropdowns
for mod, sig in [("MR","const MaterialRequests = ("), ("LPO","const LPOModule = ("), ("NOC","const NOCModule = (")]:
    start = -1
    for i,l in enumerate(lines):
        if sig in l: start=i; break
    if start == -1: continue
    for j in range(start, min(start+600, len(lines))):
        l = lines[j]
        if "setFProject(e.target.value)" in l and "onChange" in l:
            lines[j] = l.replace(
                "setFProject(e.target.value)",
                "setFProject(String(e.target.value).toLowerCase())"
            )
            changes += 1
            print(f"FIX {mod} dropdown onChange at L{j+1}")
            break

# Fix All Projects option value in MR/LPO/NOC dropdowns
for mod, sig in [("MR","const MaterialRequests = ("), ("LPO","const LPOModule = ("), ("NOC","const NOCModule = (")]:
    start = -1
    for i,l in enumerate(lines):
        if sig in l: start=i; break
    if start == -1: continue
    for j in range(start, min(start+600, len(lines))):
        l = lines[j]
        if 'value="All">All Projects' in l and "Sel" in l:
            lines[j] = l.replace('value="All">All Projects', 'value="all">All Projects')
            changes += 1
            print(f"FIX {mod} All Projects value at L{j+1}")
            break

with open(APP,"w",encoding="utf-8") as f:
    f.writelines(lines)

print(f"\nSaved. Changes: {changes}")
print("RUN: set CI=false && npm run build")
print("     git add src/App.js && git commit -m 'fix: project filters MR LPO NOC' && git push")
input("\nPress Enter...")
