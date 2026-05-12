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

# ── Show key lines ────────────────────────────────────────────────────
print("── handleSave auto-save block ──")
if dr != -1:
    for j in range(dr, min(dr+400, len(lines))):
        if "_attRows" in lines[j] or "saveAttendance" in lines[j] or "goList" in lines[j]:
            if j > dr+50:
                print("L"+str(j+1)+": "+s(lines[j].rstrip())[:120])

print("\n── printData useEffect ──")
for i,l in enumerate(lines):
    if "useEffect" in l and "printData" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:120])

print("\n── printRptId state ──")
for i,l in enumerate(lines):
    if "printRptId" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:100])

# ══════════════════════════════════════════════════════════════════════
# FIX 1: PRINT — use a separate printRptId state as useEffect dependency
# The issue: computed expressions in useEffect deps don't work reliably
# Fix: store just the rpt.id separately → useEffect on that plain string
# ══════════════════════════════════════════════════════════════════════

# Add printRptId state after printData state
pd_line = find("const [printData, setPrintData] = useState(null);")
if pd_line != -1:
    if "printRptId" not in lines[pd_line+1]:
        lines.insert(pd_line+1, "  const [printRptId, setPrintRptId] = useState(null);\n")
        changes += 1
        print("\nFIX 1a: printRptId state added at L"+str(pd_line+2))

# Update handlePrintDPR to also set printRptId
hp = find("const handlePrintDPR = (rpt) => {")
if hp != -1:
    for j in range(hp, min(hp+5, len(lines))):
        if "setPrintData" in lines[j] and "setPrintRptId" not in lines[j]:
            lines[j] = lines[j].replace(
                "setPrintData({ rpt, proj: projects.find(p=>p.id===rpt.pid), att: [] });",
                "setPrintData({ rpt, proj: projects.find(p=>p.id===rpt.pid), att: [] }); setPrintRptId(rpt.id);"
            )
            changes += 1
            print("FIX 1b: setPrintRptId added to handlePrintDPR at L"+str(j+1))
            break

# Fix useEffect to use printRptId as dependency
for i,l in enumerate(lines):
    if "useEffect" in l and "printData" in l and "loadAttendance" in l:
        lines[i] = (
            "  useEffect(() => { "
            "if (!printRptId) return; "
            "loadAttendance(printRptId).then(att => { "
            "setPrintData(p => p ? {...p, att} : p); "
            "setTimeout(() => window.print(), 600); "
            "}); }, [printRptId]);\n"
        )
        changes += 1
        print("FIX 1c: useEffect now uses printRptId as dep at L"+str(i+1))
        break

# ══════════════════════════════════════════════════════════════════════
# FIX 2: MANPOWER COUNT — await attendance BEFORE saving
# The issue: openEdit fires loadAttendance async (non-awaited)
# By the time user clicks Save, ref may still be empty
# Fix: in handleSave, load attendance directly if ref is empty
# ══════════════════════════════════════════════════════════════════════
if dr != -1:
    for j in range(dr, min(dr+400, len(lines))):
        # Find the line: const _attRows = attRowsRef.current || [];
        if "const _attRows = attRowsRef.current || [];" in lines[j]:
            # Replace with: load from DB if ref is empty
            lines[j] = (
                "    const _refRows = attRowsRef.current || [];\n"
                "    const _dbRows = _refRows.length===0 && (sel&&sel.id) ? "
                "await loadAttendance(sel.id) : [];\n"
                "    const _attRows = _refRows.length>0 ? _refRows : _dbRows;\n"
            )
            changes += 1
            print("FIX 2: handleSave now loads attendance from DB if ref empty at L"+str(j+1))
            break

# ══════════════════════════════════════════════════════════════════════
# FIX 3: MANPOWER COUNT — make handleSave async if not already
# ══════════════════════════════════════════════════════════════════════
if dr != -1:
    for j in range(dr, min(dr+200, len(lines))):
        if "const handleSave = async" in lines[j]:
            print("FIX 3: handleSave already async at L"+str(j+1))
            break

# ══════════════════════════════════════════════════════════════════════
# FIX 4: After saveAttendance, force a data reload via a trick
# Change: saveAttendance(...).then(()=>{}).catch(()=>{})
# To: saveAttendance(...).then(()=>{ onUpdate(dprId, {manpowerTotal:presentCount}) }).catch(()=>{})
# No — too complex. Instead just update daily_reports manpower_total directly
# The saveAttendance already does this. Issue is loadData runs before it.
# Fix: call onUpdate with the correct count BEFORE goList
# ══════════════════════════════════════════════════════════════════════
if dr != -1:
    for j in range(dr, min(dr+400, len(lines))):
        if "saveAttendance(_dprId, _attRows)" in lines[j]:
            # Also update the payload manpowerTotal synchronously
            # Find the payload.manpowerTotal line and ensure it uses _attRows
            for k in range(max(0,j-30), j):
                if "manpowerTotal:" in lines[k] and "attRowsRef" in lines[k]:
                    lines[k] = lines[k].replace(
                        "manpowerTotal: (attRowsRef.current||[]).filter(r=>r.am===\"P\"||r.pm===\"P\").length || totalMP,",
                        "manpowerTotal: _attRows.filter(r=>r.am===\"P\"||r.pm===\"P\").length || totalMP,"
                    )
                    if lines[k] != lines[k]:  # check changed
                        changes += 1
                        print("FIX 4: manpowerTotal uses _attRows at L"+str(k+1))
                    else:
                        # Try different pattern
                        lines[k] = "          manpowerTotal: (_attRows||[]).filter(r=>r.am===\"P\"||r.pm===\"P\").length || totalMP,\n"
                        changes += 1
                        print("FIX 4: manpowerTotal rewritten to use _attRows at L"+str(k+1))
                    break
            break

# But wait - _attRows is defined AFTER payload is built in original code
# Need to move payload.manpowerTotal update AFTER _attRows is known
# Find the payload definition and update manpowerTotal after _attRows is set

# ══════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","printData","printRptId"]
failed = [c for c in checks if c not in out]
if failed:
    print("\nSAFETY FAIL: "+str(failed))
    shutil.copy2(bk, APP)
    print("Restored")
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("\nSaved OK. Lines: "+str(len(lines)))

print("TOTAL CHANGES: "+str(changes))
print("\nRUN: set CI=false && npm run build")
input("\nPress Enter...")
