import shutil
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

# Show current state
print("DprAttendancePanel in DPR form?")
dr = find("const DailyReports = ({")
found_panel = False
if dr != -1:
    for j in range(dr, min(dr+1500,len(lines))):
        if "DprAttendancePanel" in lines[j]:
            print("  L"+str(j+1)+": "+s(lines[j].rstrip())[:80])
            found_panel = True
if not found_panel:
    print("  NOT FOUND in DailyReports")

print("\nManpower section in DPR form:")
if dr != -1:
    for j in range(dr, min(dr+1500,len(lines))):
        if 'activeSection==="manpower"' in lines[j]:
            print("  L"+str(j+1)+": "+s(lines[j].rstrip())[:100])

print("\nManpower Master in sidebar:")
for i,l in enumerate(lines):
    if "manpower-master" in l:
        print("  L"+str(i+1)+": "+s(l.rstrip())[:80])

print("\nManpower Master case in renderPage:")
for i,l in enumerate(lines):
    if '"manpower-master"' in l and "case" in l:
        print("  L"+str(i+1)+": "+s(l.rstrip())[:80])

# ── FIX 1: Add DprAttendancePanel to DPR manpower section ────────────
if dr != -1 and not found_panel:
    for j in range(dr, min(dr+1500,len(lines))):
        if 'activeSection==="manpower"' in lines[j] and "<div" in lines[j]:
            # Insert DprAttendancePanel before this line
            panel_line = '      {activeSection==="manpower"&&<DprAttendancePanel dprId={sel?sel.id:null} subcontractors={subcontractors||[]} masters={mpMasters||[]} loadAttendance={loadAttendance} saveAttendance={saveAttendance} showToast={showToast} allReports={reports}/>}\n'
            lines.insert(j, panel_line)
            changes += 1
            print("\nFIX 1: DprAttendancePanel added at L"+str(j+1))
            break

# ── FIX 2: Add Manpower Master to sidebar ────────────────────────────
has_mm_sidebar = any("manpower-master" in l and ("label" in l or "icon" in l) for l in lines)
if not has_mm_sidebar:
    for i,l in enumerate(lines):
        if '"noc"' in l and ("label" in l or "NOC" in l) and "id:" in l:
            lines.insert(i, '          { id: "manpower-master", label: "Manpower Master", icon: "users" },\n')
            changes += 1
            print("FIX 2: Manpower Master added to sidebar at L"+str(i+1))
            break

# ── FIX 3: Add case "manpower-master" to renderPage ──────────────────
has_mm_case = any('"manpower-master"' in l and "case" in l for l in lines)
if not has_mm_case:
    for i,l in enumerate(lines):
        if 'case "noc"' in l and "NOCModule" in l:
            lines.insert(i, '        case "manpower-master": return <ManpowerMaster subcontractors={subs} showToast={showToast}/>;\n')
            changes += 1
            print("FIX 3: manpower-master case added at L"+str(i+1))
            break

# WRITE
with open(APP,"w",encoding="utf-8") as f:
    f.writelines(lines)

print("\nSaved. Changes:", changes)
print("RUN: set CI=false && npm run build")
print("     git add src/App.js && git commit -m 'fix: connect manpower panel' && git push")
input("\nPress Enter...")
