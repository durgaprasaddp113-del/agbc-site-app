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
dr = find("const DailyReports = ({")

# Show current handlePrintDPR
print("── handlePrintDPR ──")
hp = find("handlePrintDPR")
if hp != -1:
    for j in range(hp, min(hp+8, len(lines))):
        print("L"+str(j+1)+": "+s(lines[j].rstrip())[:100])

# ══════════════════════════════════════════════════════════════════════
# FIX 1: Add printRptId state (separate from printData)
# ══════════════════════════════════════════════════════════════════════
pd = find("const [printData, setPrintData] = useState(null);")
if pd != -1 and "printRptId" not in lines[pd+1]:
    lines.insert(pd+1, "  const [printRptId, setPrintRptId] = useState(null);\n")
    changes += 1
    print("\nFIX 1: printRptId state added")

# ══════════════════════════════════════════════════════════════════════
# FIX 2: handlePrintDPR — set printRptId synchronously, setPrintData sync
# ══════════════════════════════════════════════════════════════════════
hp2 = find("handlePrintDPR")
if hp2 != -1:
    # Find the full function and replace
    for j in range(hp2, min(hp2+10, len(lines))):
        if "async" in lines[j] and "handlePrintDPR" in lines[j]:
            # Find end of function
            depth=0; end=-1
            for k in range(j, min(j+15, len(lines))):
                depth += lines[k].count('{') - lines[k].count('}')
                if depth<=0 and k>j:
                    end=k; break
            if end != -1:
                new_fn = [
                    "      const handlePrintDPR = (rpt) => {\n",
                    "        const proj = projects.find(p => p.id === rpt.pid);\n",
                    "        setPrintData({ rpt, proj, att: [] });\n",
                    "        setPrintRptId(rpt.id + '_' + Date.now());\n",
                    "      };\n"
                ]
                lines[j:end+1] = new_fn
                changes += 1
                print("FIX 2: handlePrintDPR is now sync")
            break

# ══════════════════════════════════════════════════════════════════════
# FIX 3: Add useEffect with printRptId as clean dependency
# ══════════════════════════════════════════════════════════════════════
# Find or update the existing useEffect for printData
existing_ue = -1
for i,l in enumerate(lines):
    if "useEffect" in l and "printData" in l:
        existing_ue = i
        break

if existing_ue != -1:
    # Replace it with clean version using printRptId
    lines[existing_ue] = (
        "  useEffect(() => { "
        "if (!printRptId || !printData) return; "
        "loadAttendance(printData.rpt.id).then(att => { "
        "setPrintData(p => p ? {...p, att} : p); "
        "setTimeout(() => window.print(), 600); "
        "}); }, [printRptId]);\n"
    )
    changes += 1
    print("FIX 3: useEffect updated with printRptId dep at L"+str(existing_ue+1))
else:
    # Insert after printRptId state
    pid2 = find("const [printRptId, setPrintRptId] = useState(null);")
    if pid2 != -1:
        ue = (
            "  useEffect(() => { "
            "if (!printRptId || !printData) return; "
            "loadAttendance(printData.rpt.id).then(att => { "
            "setPrintData(p => p ? {...p, att} : p); "
            "setTimeout(() => window.print(), 600); "
            "}); }, [printRptId]);\n"
        )
        lines.insert(pid2+1, ue)
        changes += 1
        print("FIX 3: useEffect added after printRptId state")

# ══════════════════════════════════════════════════════════════════════
# FIX 4: MANPOWER COUNT — after saveAttendance resolves, force reload
# Find: saveAttendance(_dprId, _attRows).then(...)
# Add a second .then that calls onUpdate to refresh the list count
# ══════════════════════════════════════════════════════════════════════
if dr != -1:
    for j in range(dr, min(dr+400, len(lines))):
        if "saveAttendance(_dprId, _attRows)" in lines[j]:
            if "onUpdate" not in lines[j]:
                lines[j] = lines[j].replace(
                    "saveAttendance(_dprId, _attRows).then(()=>{ if(onReload) onReload(); }).catch(()=>{});",
                    "saveAttendance(_dprId, _attRows).then((r)=>{ if(r&&r.ok&&_dprId){ onUpdate(_dprId,{pid:payload.pid,date:payload.date,reportNum:payload.reportNum,preparedBy:payload.preparedBy,weather:payload.weather,temp:payload.temp,workHours:payload.workHours,manpower:payload.manpower||[],equipment:payload.equipment||[],activities:payload.activities||[],materials:payload.materials||[],inspections:payload.inspections||[],safety:payload.safety||[],manpowerTotal:payload.manpowerTotal,issues:payload.issues,visitors:payload.visitors,remarks:payload.remarks,status:payload.status}); } }).catch(()=>{});"
                )
                # Simpler version - just call a targeted update
                if "saveAttendance(_dprId, _attRows).then((r)" not in lines[j]:
                    lines[j] = lines[j].replace(
                        "saveAttendance(_dprId, _attRows).catch(()=>{});",
                        "saveAttendance(_dprId, _attRows).catch(()=>{});"
                    )
                changes += 1
                print("FIX 4: saveAttendance then-update at L"+str(j+1))
            else:
                print("SKIP 4: onUpdate already in saveAttendance chain")
            break

# Simpler FIX 4: just update manpower_total in Supabase directly after save
# This is already done inside saveAttendance function itself
# The real issue: loadData() in useDailyReports runs when onUpdate/onAdd is called
# and it completes BEFORE saveAttendance updates manpower_total
# Solution: add a small delay before goList so DB has time to update
if dr != -1:
    for j in range(dr, min(dr+400, len(lines))):
        if "goList();" in lines[j] and j > dr+100:
            ctx = "".join(lines[max(0,j-5):j])
            if "showToast" in ctx and ("updated" in ctx or "created" in ctx):
                if "setTimeout" not in lines[j]:
                    lines[j] = lines[j].replace(
                        "showToast(sel?\"Report updated!\":\"Report created: \"+res.reportNum); goList();",
                        "showToast(sel?\"Report updated!\":\"Report created: \"+res.reportNum); setTimeout(()=>goList(), 1200);"
                    )
                    if "setTimeout" in lines[j]:
                        changes += 1
                        print("FIX 4b: goList delayed 1.2s to allow saveAttendance to complete at L"+str(j+1))
                break

# WRITE
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","printRptId","printData"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL: "+str(failed))
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("\nSaved OK. Lines: "+str(len(lines)))

print("TOTAL CHANGES: "+str(changes))
print("\nRUN: set CI=false && npm run build")
input("\nPress Enter...")
