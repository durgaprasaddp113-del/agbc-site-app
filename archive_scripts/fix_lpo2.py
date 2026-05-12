import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
changes = 0

# FIX 1: L5284 (0-based 5283) - useLPOs pid lowercase
print("Before:", s(lines[5283].rstrip())[:100])
lines[5283] = lines[5283].replace(
    'pid: l.project_id || ""',
    'pid: String(l.project_id||"").toLowerCase()'
)
changes += 1
print("After: ", s(lines[5283].rstrip())[:100])

# FIX 2: L5693 (0-based 5692) - navFilter dep
print("\nBefore:", s(lines[5692].rstrip())[:100])
lines[5692] = lines[5692].replace(
    "}, [navFilter, prefillMr]);",
    "}, [navFilter.projectId, navFilter.status, navFilter.delivery, prefillMr]);"
)
changes += 1
print("After: ", s(lines[5692].rstrip())[:100])

with open(APP,"w",encoding="utf-8") as f:
    f.writelines(lines)

print(f"\nSaved. Changes: {changes}")
print("RUN: set CI=false && npm run build")
print("     git add src/App.js && git commit -m 'fix: LPO filter pid lowercase + navFilter dep' && git push")
input("\nPress Enter...")
