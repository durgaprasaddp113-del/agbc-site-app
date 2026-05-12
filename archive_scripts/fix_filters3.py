import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
changes = 0

# FIX 1: useMatReqs pid at L5186 (0-based 5185) - make lowercase
print("L5186 before:", s(lines[5185].rstrip())[:100])
lines[5185] = lines[5185].replace(
    'pid: r.project_id || ""',
    'pid: String(r.project_id||"").toLowerCase()'
)
changes += 1
print("L5186 after: ", s(lines[5185].rstrip())[:100])

# FIX 2: NOC dropdown at L11425 - change value="All" to value="all"
print("\nL11425 before:", s(lines[11424].rstrip())[:100])
lines[11424] = lines[11424].replace('value="All">All Projects', 'value="all">All Projects')
changes += 1
print("L11425 after: ", s(lines[11424].rstrip())[:100])

# FIX 3: Check MR filter at L5478 area - show context
print("\nMR filter context:")
for j in range(5473, 5483):
    print(f"L{j+1}: {s(lines[j].rstrip())[:110]}")

print("\nLPO filter context:")
for j in range(5744, 5754):
    print(f"L{j+1}: {s(lines[j].rstrip())[:110]}")

print("\nNOC filter context:")
for j in range(11109, 11119):
    print(f"L{j+1}: {s(lines[j].rstrip())[:110]}")

# FIX 4: The navFilter useEffect issue
# Check if fProject defaults are causing reset
print("\n=== fProject useState in MR/LPO/NOC ===")
for mod, sig in [("MR","const MaterialRequests = ("), ("LPO","const LPOModule = ("), ("NOC","const NOCModule = (")]:
    for i,l in enumerate(lines):
        if sig in l:
            for j in range(i, min(i+20,len(lines))):
                if "fProject" in lines[j] and "useState" in lines[j]:
                    print(f"{mod} L{j+1}: {s(lines[j].rstrip())[:100]}")
            break

# FIX 5: navFilter useEffect - check if it resets fProject
print("\n=== navFilter useEffect in MR/LPO/NOC ===")
for mod, sig in [("MR","const MaterialRequests = ("), ("LPO","const LPOModule = ("), ("NOC","const NOCModule = (")]:
    for i,l in enumerate(lines):
        if sig in l:
            for j in range(i, min(i+30,len(lines))):
                if "navFilter" in lines[j] and ("setFProject" in lines[j] or "useEffect" in lines[j]):
                    print(f"{mod} L{j+1}: {s(lines[j].rstrip())[:100]}")
            break

with open(APP,"w",encoding="utf-8") as f:
    f.writelines(lines)

print(f"\nSaved. Changes: {changes}")
print("RUN: set CI=false && npm run build")
print("     git add src/App.js && git commit -m 'fix: filters' && git push")
input("\nPress Enter...")
