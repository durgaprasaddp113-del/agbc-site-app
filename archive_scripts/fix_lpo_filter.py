import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# Find LPOModule
lpo = next((i for i,l in enumerate(lines) if "const LPOModule = (" in l), -1)
print(f"LPOModule at L{lpo+1}")

# Show fProject state and useEffect
print("\n=== LPO fProject state + useEffect ===")
for j in range(lpo, min(lpo+40,len(lines))):
    if "fProject" in lines[j] or "navFilter" in lines[j]:
        print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

# Show LPO dropdown
print("\n=== LPO dropdown ===")
for j in range(lpo, min(lpo+600,len(lines))):
    if "fProject" in lines[j] and "Sel" in lines[j]:
        print(f"L{j+1}: {s(lines[j].rstrip())[:150]}")
        break

# Show LPO filter
print("\n=== LPO filter ===")
for j in range(lpo, min(lpo+400,len(lines))):
    if "const filtered" in lines[j]:
        for k in range(j, min(j+10,len(lines))):
            print(f"L{k+1}: {s(lines[k].rstrip())[:120]}")
        break

# Show useLPOs pid
print("\n=== useLPOs pid ===")
ul = next((i for i,l in enumerate(lines) if "function useLPOs(" in l), -1)
if ul != -1:
    for j in range(ul, min(ul+60,len(lines))):
        if "pid:" in lines[j]:
            print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")
            break

input("Press Enter to apply fixes...")

changes = 0

# Fix 1: navFilter useEffect in LPO - change [navFilter] to [navFilter.projectId]
for j in range(lpo, min(lpo+50,len(lines))):
    if "}, [navFilter]);" in lines[j]:
        ctx = "".join(lines[max(0,j-8):j+1])
        if "setFProject" in ctx:
            lines[j] = lines[j].replace("}, [navFilter]);", "}, [navFilter.projectId]);")
            changes += 1
            print(f"FIX 1: LPO navFilter dep fixed at L{j+1}")

# Fix 2: LPO dropdown option values - ensure lowercase
for j in range(lpo, min(lpo+600,len(lines))):
    if "fProject" in lines[j] and "Sel" in lines[j] and "All Projects" in lines[j]:
        # Check option values in this line or next few lines
        for k in range(j, min(j+5,len(lines))):
            if "value={p.id}" in lines[k] and "toLowerCase" not in lines[k]:
                lines[k] = lines[k].replace("value={p.id}", "value={String(p.id).toLowerCase()}")
                changes += 1
                print(f"FIX 2: LPO option values lowercase at L{k+1}")
        break

# Fix 3: LPO filter - ensure correct filter condition
for j in range(lpo, min(lpo+400,len(lines))):
    if "const filtered" in lines[j]:
        for k in range(j+1, min(j+8,len(lines))):
            if "fProject" in lines[k] and "return false" in lines[k]:
                if '"All"' in lines[k] and "_fpid" not in lines[k]:
                    lines[k] = (
                        "        const _pid  = String(l.pid || \"\").toLowerCase().trim();\n"
                        "        const _fpid = String(fProject || \"\").toLowerCase().trim();\n"
                        "        if (_fpid && _fpid !== \"all\" && _pid !== _fpid) return false;\n"
                    )
                    changes += 1
                    print(f"FIX 3: LPO filter condition fixed at L{k+1}")
        break

with open(APP,"w",encoding="utf-8") as f:
    f.writelines(lines)

print(f"\nSaved. Changes: {changes}")
print("RUN: set CI=false && npm run build")
print("     git add src/App.js && git commit -m 'fix: LPO project filter' && git push")
input("\nPress Enter...")
