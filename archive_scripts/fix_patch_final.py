import shutil, re
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
dr = find("const DailyReports = ({")

# Show current state
print("── printRptId useEffect ──")
for i,l in enumerate(lines):
    if "useEffect" in l and "printRptId" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:120])

print("\n── Manpower tab badge ──")
if dr != -1:
    for j in range(dr, min(dr+900,len(lines))):
        if '"manpower"' in lines[j] and 'Manpower' in lines[j] and 'label' in lines[j]:
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:140])
            break

print("\n── handlePrintDPR current ──")
hp = find("const handlePrintDPR =")
if hp != -1:
    for j in range(hp, min(hp+7,len(lines))):
        print("L"+str(j+1)+": "+s(lines[j].rstrip())[:100])

# FIX A: printRptId useEffect - load attendance when print triggered
fixed_ue = False
for i,l in enumerate(lines):
    if "useEffect" in l and "printRptId" in l:
        lines[i] = (
            "  useEffect(() => {\n"
            "    if (!printRptId||!printData) return;\n"
            "    loadAttendance(printData.rpt.id).then(att=>{\n"
            "      setPrintData(p=>p?{...p,att:att||[]}:p);\n"
            "    });\n"
            "  }, [printRptId]);\n"
        )
        changes += 1
        print("\nFIX A: printRptId useEffect fixed at L"+str(i+1))
        fixed_ue = True
        break

if not fixed_ue:
    # Add useEffect after printRptId state
    pid = find("const [printRptId, setPrintRptId] = useState(null);")
    if pid != -1:
        ue = (
            "  useEffect(() => {\n"
            "    if (!printRptId||!printData) return;\n"
            "    loadAttendance(printData.rpt.id).then(att=>{\n"
            "      setPrintData(p=>p?{...p,att:att||[]}:p);\n"
            "    });\n"
            "  }, [printRptId]);\n"
        )
        lines.insert(pid+1, ue)
        changes += 1
        print("\nFIX A: printRptId useEffect added at L"+str(pid+2))
    else:
        # Add after printData state
        pd = find("const [printData, setPrintData] = useState(null);")
        if pd != -1:
            lines.insert(pd+1, "  const [printRptId, setPrintRptId] = useState(null);\n")
            ue = (
                "  useEffect(() => {\n"
                "    if (!printRptId||!printData) return;\n"
                "    loadAttendance(printData.rpt.id).then(att=>{\n"
                "      setPrintData(p=>p?{...p,att:att||[]}:p);\n"
                "    });\n"
                "  }, [printRptId]);\n"
            )
            lines.insert(pd+2, ue)
            changes += 2
            print("\nFIX A: printRptId state + useEffect added at L"+str(pd+2))

# FIX B: Manpower tab badge
if dr != -1:
    for j in range(dr, min(dr+900,len(lines))):
        l = lines[j]
        if '"manpower"' in l and 'Manpower' in l and 'label' in l:
            old = lines[j]
            # Replace any count inside Manpower label
            lines[j] = re.sub(
                r'Manpower \([^)]+\)',
                'Manpower (${(attRowsRef.current||[]).length})',
                lines[j]
            )
            if lines[j] != old:
                changes += 1
                print("FIX B: Manpower tab badge fixed at L"+str(j+1))
            else:
                print("WARN B: badge pattern didn't match - current line:")
                print("  "+s(old.rstrip())[:140])
            break

# FIX C: handlePrintDPR - ensure it sets BOTH printData AND printRptId
if hp != -1:
    for j in range(hp, min(hp+8,len(lines))):
        if "setPrintData" in lines[j] and "setPrintRptId" not in lines[j]:
            lines[j] = lines[j].replace(
                "setPrintData({ rpt, proj, att: [] });",
                "setPrintData({ rpt, proj, att: [] }); setPrintRptId(String(rpt.id||'')+'_'+Date.now());"
            )
            changes += 1
            print("FIX C: setPrintRptId added to handlePrintDPR at L"+str(j+1))
            break

# WRITE
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","setPrintData","printRptId"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL: "+str(failed))
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("\nSaved OK. Lines: "+str(len(lines)))

print("TOTAL CHANGES: "+str(changes))
print("\nRUN: set CI=false && npm run build && npx vercel --prod --force")
input("\nPress Enter...")
