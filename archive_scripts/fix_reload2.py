import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def find(t):
    for i,l in enumerate(lines): 
        if t in l: return i
    return -1

changes = 0

# FIX 3: Pass reloadR to DailyReports in App renderPage
for i,l in enumerate(lines):
    if 'case "reports"' in l and "DailyReports" in l:
        if "reloadR" not in l and "onReload" not in l:
            lines[i] = l.replace("onDelete={delR}", "onDelete={delR} onReload={reloadR}")
            changes += 1
            print("FIX 3: onReload added to DailyReports case at L" + str(i+1))
        else:
            print("SKIP 3: already has onReload or reloadR")
        break

# FIX 4: DailyReports — accept onReload prop
dr = find("const DailyReports = ({")
if dr != -1:
    if "onReload" not in lines[dr]:
        lines[dr] = lines[dr].replace("subcontractors = []", "subcontractors = [], onReload")
        changes += 1
        print("FIX 4: onReload prop added to DailyReports at L" + str(dr+1))

# FIX 5: handleSave — call onReload after attendance saves
if dr != -1:
    for j in range(dr, min(dr+400, len(lines))):
        if "saveAttendance(_dprId, _attRows).catch(()=>{});" in lines[j]:
            lines[j] = lines[j].replace(
                "saveAttendance(_dprId, _attRows).catch(()=>{});",
                "saveAttendance(_dprId, _attRows).then(()=>{ if(onReload) onReload(); }).catch(()=>{});"
            )
            changes += 1
            print("FIX 5: onReload after attendance save at L" + str(j+1))
            break

# FIX 6: openEdit async + pre-load attendance
if dr != -1:
    for j in range(dr, min(dr+200, len(lines))):
        l = lines[j]
        if "const openEdit" in l and "=>" in l and "rpt" in l:
            if "async" not in l:
                lines[j] = lines[j].replace("const openEdit = rpt =>", "const openEdit = async (rpt) =>")
                lines[j] = lines[j].replace("const openEdit = (rpt) =>", "const openEdit = async (rpt) =>")
                changes += 1
                print("FIX 6a: openEdit async at L" + str(j+1))
            for k in range(j, min(j+15, len(lines))):
                if 'setMode("form")' in lines[k]:
                    if "await loadAttendance" not in "".join(lines[max(0,k-2):k]):
                        lines.insert(k, '      const _preAtt = await loadAttendance(rpt && rpt.id ? rpt.id : ""); if (_preAtt && _preAtt.length) attRowsRef.current = _preAtt;\n')
                        changes += 1
                        print("FIX 6b: pre-load attendance in openEdit at L" + str(k+1))
                    break
            break

# FIX 7: Replace setTimeout print with useEffect
for i,l in enumerate(lines):
    if "setTimeout(() => window.print(), 800)" in l:
        lines[i] = l.replace("setTimeout(() => window.print(), 800);", "// print via useEffect")
        changes += 1
        print("FIX 7a: removed setTimeout print at L" + str(i+1))
        break

for i,l in enumerate(lines):
    if "const [printData, setPrintData] = useState(null);" in l:
        ue = '  useEffect(() => { if (printData) { const t = setTimeout(() => window.print(), 600); return () => clearTimeout(t); } }, [printData]);\n'
        if "useEffect" not in lines[i+1]:
            lines.insert(i+1, ue)
            changes += 1
            print("FIX 7b: useEffect print trigger at L" + str(i+2))
        break

# WRITE
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","attRowsRef","printData","onReload"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL: " + str(failed))
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("Saved OK. Lines: " + str(len(lines)))

print("TOTAL CHANGES: " + str(changes))
print("\nRUN: set CI=false && npm run build")
input("\nPress Enter...")
