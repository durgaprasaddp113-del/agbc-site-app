import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
changes = 0

# L3955 (0-based: 3954) — handlePrintDPR async function
# Find its end
start = 3954
depth = 0
end = -1
for j in range(start, min(start+15, len(lines))):
    depth += lines[j].count('{') - lines[j].count('}')
    if depth <= 0 and j > start:
        end = j; break

print("Function L"+str(start+1)+" to L"+str(end+1))
for j in range(start, end+1):
    print("  "+s(lines[j].rstrip())[:100])

if end != -1:
    new_fn = [
        "      const handlePrintDPR = (rpt) => {\n",
        "        const proj = projects.find(p => p.id === rpt.pid);\n",
        "        setPrintData({ rpt, proj, att: [] });\n",
        "        setPrintRptId(rpt.id + '_' + Date.now());\n",
        "      };\n"
    ]
    lines[start:end+1] = new_fn
    changes += 1
    print("\nFIX: handlePrintDPR replaced with sync version")

# Also add goList delay for manpower count
dr = next((i for i,l in enumerate(lines) if "const DailyReports = ({" in l), -1)
if dr != -1:
    for j in range(dr, min(dr+450, len(lines))):
        if 'showToast(sel?"Report updated!":"Report created: "+res.reportNum); goList();' in lines[j]:
            lines[j] = lines[j].replace(
                'showToast(sel?"Report updated!":"Report created: "+res.reportNum); goList();',
                'showToast(sel?"Report updated!":"Report created: "+res.reportNum); setTimeout(()=>goList(),1200);'
            )
            changes += 1
            print("FIX: goList delayed 1.2s at L"+str(j+1))
            break

# Verify
print("\n── New handlePrintDPR ──")
hp = next((i for i,l in enumerate(lines) if "handlePrintDPR = " in l and "button" not in l), -1)
if hp != -1:
    for j in range(hp, min(hp+7, len(lines))):
        print("L"+str(j+1)+": "+s(lines[j].rstrip())[:100])

with open(APP,"w",encoding="utf-8") as f:
    f.writelines(lines)
print("\nSaved. Changes: "+str(changes))
print("RUN: set CI=false && npm run build")
input("Press Enter...")
