import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# Find L3712 equivalent — the DPR "Edit Report" button
# We know it contains: openEdit(sel) + "Edit Report" + Btn
# and is inside DailyReports (between L3553 and L3900 approx)
target = -1
dr_start = next((i for i,l in enumerate(lines) if "const DailyReports = ({" in l), -1)
dr_end = dr_start + 600  # Edit Report is within first 600 lines of component

for j in range(dr_start, min(dr_end, len(lines))):
    if 'openEdit(sel)' in lines[j] and 'Edit Report' in lines[j] and 'Btn' in lines[j]:
        target = j
        print(f"Found at L{j+1}: {s(lines[j].rstrip())[:100]}")
        break

if target == -1:
    # Fallback: search whole file
    for j,l in enumerate(lines):
        if 'Edit Report' in l and 'openEdit(sel)' in l:
            target = j
            print(f"Found (fallback) at L{j+1}: {s(lines[j].rstrip())[:100]}")
            break

if target != -1:
    # Check print button not already there
    nearby = "".join(lines[max(0,target-3):target+1])
    if "handlePrintDPR" not in nearby:
        indent = "              "
        btn = indent + '<button onClick={()=>handlePrintDPR(sel)} className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-xl text-sm font-semibold transition-colors">Print DPR</button>\n'
        lines.insert(target, btn)
        print(f"FIX: Print button inserted at L{target+1}")
    else:
        print("SKIP: Print button already exists near Edit Report")
else:
    print("ERROR: Edit Report button not found!")

# Safety check before writing
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","Edit Report"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL:", failed, "— restoring backup")
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("File saved. Lines:", len(lines))
    print("\nRUN: set CI=false && npm run build")
    print("     npx vercel --prod --force")
    print('     git add src/App.js && git commit -m "feat: DPR Print button" && git push')

input("\nPress Enter...")
