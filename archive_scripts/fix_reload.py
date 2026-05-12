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

# ══════════════════════════════════════════════════════════════════════
# FIX 1: useDailyReports — expose reload function
# ══════════════════════════════════════════════════════════════════════
udr = find("function useDailyReports()")
if udr != -1:
    for j in range(udr, min(udr+150, len(lines))):
        if "return { reports, loading, add, update" in lines[j]:
            if "reload" not in lines[j]:
                lines[j] = lines[j].replace(
                    "return { reports, loading, add, update",
                    "return { reports, loading, add, update, reload: loadData"
                )
                changes += 1
                print(f"FIX 1: reload exposed from useDailyReports at L{j+1}")
            break

# ══════════════════════════════════════════════════════════════════════
# FIX 2: App() — destructure reload from useDailyReports
# ══════════════════════════════════════════════════════════════════════
for i,l in enumerate(lines):
    if "useDailyReports()" in l and "rlLoad" in l:
        if "reloadR" not in l:
            lines[i] = l.replace(
                "remove: delR } = useDailyReports();",
                "remove: delR, reload: reloadR } = useDailyReports();"
            )
            changes += 1
            print(f"FIX 2: reloadR added to useDailyReports destructure at L{i+1}")
        break

# ══════════════════════════════════════════════════════════════════════
# FIX 3: Pass reloadR to DailyReports in App renderPage
# ══════════════════════════════════════════════════════════════════════
for i,l in enumerate(lines):
    if 'case "reports"' in l and "DailyReports" in l:
        if "reloadR" not in l and "onReload" not in l:
            lines[i] = l.replace(
                "onDelete={delR}",
                "onDelete={delR} onReload={reloadR}"
            )
            changes += 1
            print(f"FIX 3: onReload={reloadR} added to DailyReports case at L{i+1}")
        break

# ══════════════════════════════════════════════════════════════════════
# FIX 4: DailyReports — accept onReload prop
# ══════════════════════════════════════════════════════════════════════
dr = find("const DailyReports = ({")
if dr != -1:
    if "onReload" not in lines[dr]:
        lines[dr] = lines[dr].replace(
            "subcontractors = []",
            "subcontractors = [], onReload"
        )
        changes += 1
        print(f"FIX 4: onReload prop added to DailyReports at L{dr+1}")

# ══════════════════════════════════════════════════════════════════════
# FIX 5: handleSave — call onReload after saveAttendance completes
# Find the auto-save attendance line and make it await + reload
# ══════════════════════════════════════════════════════════════════════
if dr != -1:
    for j in range(dr, min(dr+400, len(lines))):
        if "saveAttendance(_dprId, _attRows).catch(()=>{});" in lines[j]:
            lines[j] = lines[j].replace(
                "if (_dprId && _attRows.length > 0) { saveAttendance(_dprId, _attRows).catch(()=>{}); }",
                "if (_dprId && _attRows.length > 0) { saveAttendance(_dprId, _attRows).then(()=>{ if(onReload) onReload(); }).catch(()=>{}); }"
            )
            changes += 1
            print(f"FIX 5: onReload called after attendance save at L{j+1}")
            break

# ══════════════════════════════════════════════════════════════════════
# FIX 6: openEdit — make async and pre-load attendance into attRowsRef
# ══════════════════════════════════════════════════════════════════════
if dr != -1:
    for j in range(dr, min(dr+200, len(lines))):
        l = lines[j]
        if "const openEdit" in l and "=>" in l and "rpt" in l:
            # Make it async
            if "async" not in l:
                lines[j] = l.replace("const openEdit = rpt =>", "const openEdit = async (rpt) =>")
                lines[j] = lines[j].replace("const openEdit = (rpt) =>", "const openEdit = async (rpt) =>")
                changes += 1
                print(f"FIX 6a: openEdit made async at L{j+1}")
            # Find the setMode("form") inside openEdit
            for k in range(j, min(j+15, len(lines))):
                if 'setMode("form")' in lines[k]:
                    if "await loadAttendance" not in lines[k-1]:
                        preload = '      const _preAtt = await loadAttendance(rpt && rpt.id ? rpt.id : ""); if (_preAtt && _preAtt.length) attRowsRef.current = _preAtt;\n'
                        lines.insert(k, preload)
                        changes += 1
                        print(f"FIX 6b: await attendance pre-load added before setMode at L{k+1}")
                    break
            break

# ══════════════════════════════════════════════════════════════════════
# FIX 7: Print — replace setTimeout+window.print with button-triggered print
# The issue: setTimeout window.print() is blocked by some browsers
# Solution: show print button inside the overlay itself (already there)
# but also add a React useEffect to trigger print when printData changes
# ══════════════════════════════════════════════════════════════════════
# Change: replace setTimeout(() => window.print(), 800) 
# with just calling window.print() directly (sync after state update via useEffect)
for i,l in enumerate(lines):
    if "setTimeout(() => window.print(), 800)" in l:
        lines[i] = l.replace(
            "setTimeout(() => window.print(), 800);",
            "// print triggered by useEffect below"
        )
        changes += 1
        print(f"FIX 7a: removed setTimeout print at L{i+1}")
        break

# Add useEffect for print trigger after printData state (near printData useState)
for i,l in enumerate(lines):
    if "const [printData, setPrintData] = useState(null);" in l:
        useeff = '  useEffect(() => { if (printData) { const t = setTimeout(() => { window.print(); }, 600); return () => clearTimeout(t); } }, [printData]);\n'
        if "useEffect" not in lines[i+1]:
            lines.insert(i+1, useeff)
            changes += 1
            print(f"FIX 7b: useEffect print trigger added at L{i+2}")
        break

# ══════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","attRowsRef","printData","onReload"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL:", failed)
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print(f"\nSaved OK. Lines: {len(lines)}")

print(f"TOTAL CHANGES: {changes}")
print("\nRUN: set CI=false && npm run build")
input("\nPress Enter...")
