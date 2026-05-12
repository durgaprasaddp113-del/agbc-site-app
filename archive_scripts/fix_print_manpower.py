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

# ── SHOW CURRENT STATE ────────────────────────────────────────────────
print("── handlePrintDPR current ──")
hp = find("handlePrintDPR = async")
if hp != -1:
    for j in range(hp, min(hp+8, len(lines))):
        print("L"+str(j+1)+": "+s(lines[j].rstrip())[:100])

print("\n── printData useEffect ──")
for i,l in enumerate(lines):
    if "useEffect" in l and "printData" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:120])

print("\n── attRowsRef usage ──")
for i,l in enumerate(lines):
    if "attRowsRef" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:100])

print("\n── manpowerTotal in handleSave ──")
if dr != -1:
    for j in range(dr, min(dr+400, len(lines))):
        if "manpowerTotal" in lines[j] and "payload" in "".join(lines[max(0,j-5):j+1]):
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:100])

# ══════════════════════════════════════════════════════════════════════
# FIX A: PRINT - Change handlePrintDPR from async+setPrintData 
# to just setPrintState(sel) synchronously, and load att separately
# The problem: await inside onClick handler loses browser gesture → print blocked
# Solution: on click → set showPrint=true synchronously → useEffect loads att + prints
# ══════════════════════════════════════════════════════════════════════

# Step A1: Replace handlePrintDPR with sync version
if hp != -1:
    func_end = -1
    depth = 0
    for j in range(hp, min(hp+15, len(lines))):
        depth += lines[j].count('{') - lines[j].count('}')
        if depth <= 0 and j > hp:
            func_end = j; break
    if func_end != -1:
        new_fn = [
            "      const handlePrintDPR = (rpt) => {\n",
            "        setPrintData({ rpt, proj: projects.find(p=>p.id===rpt.pid), att: [] });\n",
            "      };\n"
        ]
        lines[hp:func_end+1] = new_fn
        changes += 1
        print("\nFIX A1: handlePrintDPR now sync (sets printData immediately)")

# Step A2: Add useEffect to load att + print when printData changes
# Find printData useState line
pd_line = find("const [printData, setPrintData] = useState(null);")
if pd_line != -1:
    # Check if useEffect already exists nearby
    nearby = "".join(lines[pd_line:pd_line+5])
    if "useEffect" not in nearby or "printData" not in "".join(lines[pd_line:pd_line+5]):
        ue = (
            "  useEffect(() => {\n"
            "    if (!printData || !printData.rpt) return;\n"
            "    loadAttendance(printData.rpt.id).then(att => {\n"
            "      setPrintData(p => p ? {...p, att} : p);\n"
            "      setTimeout(() => window.print(), 500);\n"
            "    });\n"
            "  }, [printData && printData.rpt && printData.rpt.id]);\n"
        )
        lines.insert(pd_line+1, ue)
        changes += 1
        print("FIX A2: useEffect loads att + prints when printData.rpt.id changes")
    else:
        # Update existing useEffect
        for j in range(pd_line, pd_line+8):
            if "useEffect" in lines[j] and "printData" in lines[j]:
                lines[j] = (
                    "  useEffect(() => { if (!printData||!printData.rpt) return; "
                    "loadAttendance(printData.rpt.id).then(att => { "
                    "setPrintData(p=>p?{...p,att}:p); setTimeout(()=>window.print(),500); }); "
                    "}, [printData&&printData.rpt&&printData.rpt.id]);\n"
                )
                changes += 1
                print("FIX A2: useEffect updated at L"+str(j+1))
                break

# ══════════════════════════════════════════════════════════════════════
# FIX B: MANPOWER COUNT - Load attendance from DB on openEdit
# so attRowsRef has data even if user never visits Manpower tab
# ══════════════════════════════════════════════════════════════════════
if dr != -1:
    for j in range(dr, min(dr+250, len(lines))):
        l = lines[j]
        if "const openEdit" in l and "rpt" in l and "=>" in l:
            print("\nFIX B: Found openEdit at L"+str(j+1)+": "+s(l.rstrip())[:80])
            # Make async
            if "async" not in l:
                lines[j] = lines[j].replace(
                    "const openEdit = rpt =>", "const openEdit = async (rpt) =>"
                ).replace(
                    "const openEdit = (rpt) =>", "const openEdit = async (rpt) =>"
                )
                changes += 1
                print("FIX B1: openEdit made async")
            # Insert pre-load before setMode form
            for k in range(j, min(j+20, len(lines))):
                if 'setMode("form")' in lines[k]:
                    ctx = "".join(lines[max(0,k-4):k])
                    if "_preAtt" not in ctx and "await loadAttendance" not in ctx:
                        lines.insert(k,
                            '      loadAttendance(rpt&&rpt.id?rpt.id:"").then(att=>{ if(att&&att.length) attRowsRef.current=att; });\n'
                        )
                        changes += 1
                        print("FIX B2: attendance preload added before setMode at L"+str(k+1))
                    else:
                        print("SKIP B2: preload already exists")
                    break
            break

# ══════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","attRowsRef","printData"]
failed = [c for c in checks if c not in out]
if failed:
    print("\nSAFETY FAIL: " + str(failed))
    shutil.copy2(bk, APP)
    print("Restored backup")
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("\nFile saved OK. Lines: " + str(len(lines)))

print("TOTAL CHANGES: " + str(changes))
print("\nRUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
input("\nPress Enter...")
