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
dr = find("const DailyReports = ({")

# ── STEP 1: Fix broken Manpower label L3677 ──────────────────────────
print("FIX 1: Manpower label")
print("Before: "+s(lines[3676].rstrip())[:80])
lines[3676] = '      {id:"manpower",label:`Manpower (${(attRowsRef.current||[]).length})`},\n'
changes += 1
print("After:  "+s(lines[3676].rstrip())[:80])

# ── STEP 2: Replace handlePrintDPR with exportDPRtoPDF ───────────────
# Find handlePrintDPR at L4041 area (may have shifted)
hp = find("const handlePrintDPR =")
if hp != -1:
    depth=0; end=hp
    for j in range(hp, min(hp+20, len(lines))):
        depth += lines[j].count('{') - lines[j].count('}')
        if depth<=0 and j>hp: end=j; break

    new_fn = [
        "      const handlePrintDPR = async (rpt) => {\n",
        "        const proj = projects.find(p => p.id === rpt.pid);\n",
        "        const att = await loadAttendance(rpt.id);\n",
        "        // Build CSV content for Excel export\n",
        "        const csvRows = [\n",
        "          ['AL GHAITH BUILDING CONSTRUCTION LLC - SITE DAILY REPORT'],\n",
        "          [],\n",
        "          ['Report No', rpt.reportNum||'', 'Date', rpt.date||'', 'Project', (proj?proj.number+' '+proj.name:'')],\n",
        "          ['Prepared By', rpt.preparedBy||'', 'Weather', rpt.weather||'', 'Work Hours', (rpt.workHours||'8')+'h'],\n",
        "          ['Status', rpt.status||''],\n",
        "          [],\n",
        "          ['MANPOWER ATTENDANCE'],\n",
        "          ['S.No','ID No','Name','Designation','Team','A.M','P.M','O.T Hrs','Description of Work'],\n",
        "          ...att.map((r,i)=>[i+1, r.empId||'', r.name||'', r.designation||'', r.teamNo||'', r.am||'P', r.pm||'P', r.ot||'0', r.description||'']),\n",
        "          [],\n",
        "          ['','','','','TOTAL PRESENT', att.filter(r=>r.am==='P').length, att.filter(r=>r.pm==='P').length],\n",
        "          [],\n",
        "        ];\n",
        "        // Add equipment\n",
        "        if ((rpt.equipment||[]).filter(e=>e.name).length) {\n",
        "          csvRows.push(['EQUIPMENT'],['Equipment','Qty','Status','Operator','Remarks']);\n",
        "          (rpt.equipment||[]).filter(e=>e.name).forEach(e=>csvRows.push([e.name||'',e.qty||'',e.status||'',e.operator||'',e.remarks||'']));\n",
        "          csvRows.push([]);\n",
        "        }\n",
        "        // Add activities\n",
        "        if ((rpt.activities||[]).filter(a=>a.activity).length) {\n",
        "          csvRows.push(['WORK ACTIVITIES'],['Location','Activity','Trade','Progress%','Remarks']);\n",
        "          (rpt.activities||[]).filter(a=>a.activity).forEach(a=>csvRows.push([a.location||'',a.activity||'',a.trade||'',a.progress||'',a.remarks||'']));\n",
        "          csvRows.push([]);\n",
        "        }\n",
        "        csvRows.push(['Signature Site Engineer','','','Signature Site Incharge']);\n",
        "        // Convert to CSV\n",
        "        const csvContent = csvRows.map(row=>row.map(cell=>{\n",
        "          const str = String(cell||'').replace(/\"/g,'\"\"');\n",
        "          return str.includes(',') || str.includes('\"') || str.includes('\\n') ? '\"'+str+'\"' : str;\n",
        "        }).join(',')).join('\\n');\n",
        "        // Download\n",
        "        const blob = new Blob(['\\uFEFF'+csvContent], {type:'text/csv;charset=utf-8;'});\n",
        "        const url = URL.createObjectURL(blob);\n",
        "        const a = document.createElement('a');\n",
        "        a.href = url;\n",
        "        a.download = (rpt.reportNum||'DPR')+'_'+( rpt.date||'')+'_'+(proj?proj.number:'')+'.csv';\n",
        "        document.body.appendChild(a);\n",
        "        a.click();\n",
        "        document.body.removeChild(a);\n",
        "        URL.revokeObjectURL(url);\n",
        "        showToast('DPR exported! Open the CSV file in Excel.');\n",
        "      };\n",
    ]
    lines[hp:end+1] = new_fn
    changes += 1
    print("\nFIX 2: handlePrintDPR replaced with CSV/Excel export at L"+str(hp+1))

# ── STEP 3: Change Print DPR button label to Export to Excel ─────────
for i,l in enumerate(lines):
    if "handlePrintDPR(sel)" in l and "button" in l and "Print DPR" in l:
        lines[i] = lines[i].replace("Print DPR", "Export Excel")
        changes += 1
        print("FIX 3: Button text changed to 'Export Excel' at L"+str(i+1))
        break

# ── STEP 4: Remove print modal and related state to clean up ─────────
# Remove printData and printRptId states + useEffects
# Keep them simple - just remove the modal rendering
for i,l in enumerate(lines):
    if "printData&&(" in l or "{printData&&(" in l:
        # Blank out the modal block
        depth=0; end_i=i
        for j in range(i, min(i+120,len(lines))):
            depth += lines[j].count('{') - lines[j].count('}')
            if depth<=0 and j>i: end_i=j; break
        for j in range(i, end_i+1):
            lines[j] = ""
        changes += 1
        print("FIX 4: Print modal removed")
        break

# ── STEP 5: Fix duplicate useEffect ──────────────────────────────────
# Remove second (duplicate) useEffect for printRptId around L3590
dup_found = False
for i in range(3585, min(3605, len(lines))):
    if "useEffect" in lines[i] and "printRptId" in lines[i]:
        depth=0; end_dup=i
        for j in range(i, min(i+10,len(lines))):
            depth += lines[j].count('{') - lines[j].count('}')
            if depth<=0 and j>i: end_dup=j; break
        for j in range(i, end_dup+1):
            lines[j] = ""
        dup_found = True
        changes += 1
        print("FIX 5: Duplicate useEffect removed at L"+str(i+1))
        break

# WRITE
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","showToast"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL: "+str(failed))
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("\nSaved OK. Lines: "+str(len(lines)))

print("TOTAL CHANGES: "+str(changes))
print("\nRUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
input("\nPress Enter...")
