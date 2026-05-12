import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def find(t):
    for i,l in enumerate(lines): 
        if t in l: return i
    return -1

changes = 0

# Show current filter conditions
print("── Current filter conditions ──")
for i,l in enumerate(lines):
    if "_fpid" in l and "return false" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:100])

print("\n── Current fProject dropdowns ──")
for i,l in enumerate(lines):
    if "setFProject" in l and "onChange" in l and ("MR\|LPO\|NOC" in s(l) or "toLowerCase" in l):
        print("L"+str(i+1)+": "+s(l.rstrip())[:100])

# Show useMatReqs pid
print("\n── useMatReqs pid ──")
umr = find("function useMatReqs(")
if umr != -1:
    for j in range(umr, min(umr+50,len(lines))):
        if "pid:" in lines[j] and "project_id" in lines[j]:
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:100])
            break

# Show MR/LPO/NOC filter conditions
print("\n── MR/LPO/NOC filter blocks ──")
for mod, sig in [("MR","const MaterialRequests = ("), ("LPO","const LPOModule = ("), ("NOC","const NOCModule = (")]:
    idx = find(sig)
    if idx != -1:
        for j in range(idx, min(idx+400,len(lines))):
            if "const filtered" in lines[j]:
                print(mod+" L"+str(j+1)+": "+s(lines[j].rstrip())[:80])
                for k in range(j+1, min(j+8,len(lines))):
                    if "fProject" in lines[k] or "_fpid" in lines[k]:
                        print("    L"+str(k+1)+": "+s(lines[k].rstrip())[:100])
                break

# FIX: Ensure all 3 modules use correct filter
# The fix: fProject condition should use _fpid !== "all" (lowercase)
# And dropdowns should use toLowerCase()

fixed = 0
for i,l in enumerate(lines):
    # Fix filter condition: change !== "All" to !== "all" with _fpid
    if 'fProject !== "All"' in l and "_pid" in l and "return false" in l:
        old = lines[i]
        # Get the variable name (m, l, n)
        import re
        match = re.search(r'String\((\w+)\.pid', l)
        var = match.group(1) if match else None
        if var:
            lines[i] = (
                f'        const _pid  = String({var}.pid  || "").toLowerCase().trim();\n'
                f'        const _fpid = String(fProject || "").toLowerCase().trim();\n'
                f'        if (_fpid && _fpid !== "all" && _pid !== _fpid) return false;\n'
            )
            # Remove duplicate _pid/_fpid lines if they exist above
            changes += 1
            fixed += 1
            print(f"FIX: Filter fixed at L{i+1}")

# Fix useMatReqs pid to be lowercase
umr2 = find("function useMatReqs(")
if umr2 != -1:
    for j in range(umr2, min(umr2+50,len(lines))):
        if "pid:" in lines[j] and "project_id" in lines[j]:
            if "toLowerCase" not in lines[j]:
                lines[j] = lines[j].replace(
                    'pid: r.project_id || ""',
                    'pid: String(r.project_id||"").toLowerCase()'
                )
                changes += 1
                print("FIX: useMatReqs pid now lowercase at L"+str(j+1))
            break

# Fix dropdowns - ensure onChange uses toLowerCase
for i,l in enumerate(lines):
    if "setFProject(e.target.value)" in l and ("MR\|LPO\|NOC" in s(l) or 
        any(m in "".join(s(lines[max(0,i-200):i])) for m in ["MaterialRequests","LPOModule","NOCModule"])):
        if "toLowerCase" not in l:
            lines[i] = l.replace(
                "setFProject(e.target.value)",
                "setFProject(String(e.target.value).toLowerCase())"
            )
            changes += 1
            print("FIX: Dropdown onChange toLowerCase at L"+str(i+1))

# Fix All Projects option value
for i,l in enumerate(lines):
    if 'value="All">All Projects' in l:
        # Check if this is in MR/LPO/NOC context
        ctx = "".join(s(x) for x in lines[max(0,i-5):i+5])
        if "toLowerCase" in ctx or "setFProject" in ctx:
            lines[i] = l.replace('value="All">All Projects', 'value="all">All Projects')
            changes += 1
            print("FIX: All Projects option value fixed at L"+str(i+1))

with open(APP,"w",encoding="utf-8") as f:
    f.writelines(lines)

print("\nSaved. Changes:", changes)
print("RUN: set CI=false && npm run build")
print("     git add src/App.js && git commit -m 'fix: project filters MR LPO NOC' && git push")
input("\nPress Enter...")
