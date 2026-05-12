import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
changes = 0

# FIX 1: L3671 broken label (0-based: 3670)
print("L3671 current: "+s(lines[3670].rstrip()))
lines[3670] = lines[3670].replace(
    '`? Manpower (${(attRowsRef.current||[]).length}).length})`',
    '`? Manpower (${(attRowsRef.current||[]).length})`'
)
changes += 1
print("FIX 1: Manpower label fixed")
print("L3671 new:     "+s(lines[3670].rstrip())[:100])

# FIX 2: L4038 duplicate setPrintRptId (0-based: 4037)
print("\nL4038 current: "+s(lines[4037].rstrip()))
if "setPrintRptId" in lines[4037] and "setPrintData" not in lines[4037]:
    lines[4037] = "\n"
    changes += 1
    print("FIX 2: Duplicate setPrintRptId removed")

# FIX 3: Add useEffect after L3583 (printRptId state)
print("\nFIX 3: Adding useEffect for printRptId...")
# L3583 is 0-based 3582
ue = (
    "  useEffect(() => {\n"
    "    if (!printRptId || !printData) return;\n"
    "    loadAttendance(printData.rpt.id).then(att => {\n"
    "      setPrintData(p => p ? {...p, att: att||[]} : p);\n"
    "    });\n"
    "  }, [printRptId]);\n"
)
lines.insert(3583, ue)
changes += 1
print("FIX 3: useEffect inserted at L3584")

# WRITE
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","printRptId","loadAttendance"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL: "+str(failed))
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("\nSaved OK")

print("TOTAL CHANGES: "+str(changes))
print("\nRUN: set CI=false && npm run build && npx vercel --prod --force")
input("\nPress Enter...")
