# fix_req1.py — Priority fixes:
# 1. DPR Export PDF + Excel buttons in list & view
# 2. Project Number clickable in all modules (Tasks, Snags, MR, LPO, Reports, NOC, Inspections)
# 3. Progress Module date field
# 4. onNavigate passed to all modules

import shutil, re
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print(f"Backup: {bk}")

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# ══════════════════════════════════════════════════════════
# FIX 1: Pass onNavigate to all modules via pp object
# ══════════════════════════════════════════════════════════
old = 'const pp = { projects, showToast, userProfile, userCanEdit, userIsAdmin, permReqs, onAddPermReq: addPermReq, navFilter };'
new = 'const pp = { projects, showToast, userProfile, userCanEdit, userIsAdmin, permReqs, onAddPermReq: addPermReq, navFilter, onNavigate: navigate };'
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 1: onNavigate added to pp")
else:
    print("WARN FIX 1: pp object pattern not found")

# ══════════════════════════════════════════════════════════
# FIX 2: Accept onNavigate in Tasks, Snags, MR, LPO, NOC,
#         Inspections, DailyReports, Drawings
# ══════════════════════════════════════════════════════════
modules_sigs = [
    ('const Tasks = ({ projects, tasks, loading, onAdd, onUpdate, onDelete, showToast, navFilter = {} })',
     'const Tasks = ({ projects, tasks, loading, onAdd, onUpdate, onDelete, showToast, navFilter = {}, onNavigate })'),
    ('const Snags = ({ projects, snags, loading, onAdd, onUpdate, onDelete, showToast, navFilter = {} })',
     'const Snags = ({ projects, snags, loading, onAdd, onUpdate, onDelete, showToast, navFilter = {}, onNavigate })'),
    ('const DailyReports = ({ projects, reports, loading, onAdd, onUpdate, onDelete, showToast, navFilter = {}, subcontractors',
     'const DailyReports = ({ projects, reports, loading, onAdd, onUpdate, onDelete, showToast, navFilter = {}, onNavigate, subcontractors'),
    ('const Inspections = ({ projects, inspections, loading, onAdd, onUpdate, onDelete, showToast, navFilter = {} })',
     'const Inspections = ({ projects, inspections, loading, onAdd, onUpdate, onDelete, showToast, navFilter = {}, onNavigate })'),
    ('const Drawings = ({ projects, drawings, loading, onAdd, onUpdate, onDelete, showToast })',
     'const Drawings = ({ projects, drawings, loading, onAdd, onUpdate, onDelete, showToast, onNavigate })'),
    ('const MaterialRequests = ({ mrs, loading, onAdd, onUpdate, onDelete, onUpdateStatus, projects, showToast, onNavigateLpo, navFilter = {}, lpos = [] })',
     'const MaterialRequests = ({ mrs, loading, onAdd, onUpdate, onDelete, onUpdateStatus, projects, showToast, onNavigateLpo, navFilter = {}, lpos = [], onNavigate })'),
    ('const LPOModule = ({ lpos, loading, onAdd, onUpdate, onDelete, projects, mrs, showToast, prefillMr, onClearPrefill, navFilter = {} })',
     'const LPOModule = ({ lpos, loading, onAdd, onUpdate, onDelete, projects, mrs, showToast, prefillMr, onClearPrefill, navFilter = {}, onNavigate })'),
    ('const NOCModule = ({ nocs, loading, onAdd, onUpdate, onDelete, projects, showToast, navFilter = {} })',
     'const NOCModule = ({ nocs, loading, onAdd, onUpdate, onDelete, projects, showToast, navFilter = {}, onNavigate })'),
]
for old_s, new_s in modules_sigs:
    if old_s in content:
        content = content.replace(old_s, new_s, 1)
        changes += 1
        print(f"FIX 2: onNavigate added to {old_s[:40]}...")
    else:
        print(f"WARN FIX 2: sig not found: {old_s[:50]}")

# ══════════════════════════════════════════════════════════
# FIX 3: Make project number cells clickable in TASKS list
# ══════════════════════════════════════════════════════════
# In Tasks table: proj?.number cell
old = '''                  <td className="px-4 py-3 text-xs text-slate-600">{projects.find(p => p.id === t.pid)?.number || "—"}</td>'''
new = '''                  <td className="px-4 py-3 text-xs font-bold text-amber-700 cursor-pointer hover:underline" onClick={()=>onNavigate&&onNavigate("projects",{projectId:t.pid})}>{projects.find(p => p.id === t.pid)?.number || "—"}</td>'''
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 3a: Tasks project number clickable")

# In Tasks VIEW mode
old = '["Project", projects.find(p => p.id === sel.pid)?.number]'
new = '["Project", projects.find(p => p.id === sel.pid)?.number]'
# view mode handled differently — skip for now

# ══════════════════════════════════════════════════════════
# FIX 4: Make project number cells clickable in SNAGS list
# ══════════════════════════════════════════════════════════
old = '''                    <span className="text-xs text-slate-400">{projects.find(p => p.id === s.pid)?.number || ""}</span>'''
new = '''                    <span className="text-xs font-bold text-amber-700 cursor-pointer hover:underline" onClick={()=>onNavigate&&onNavigate("projects",{projectId:s.pid})}>{projects.find(p => p.id === s.pid)?.number || ""}</span>'''
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 4a: Snags project number clickable")

# ══════════════════════════════════════════════════════════
# FIX 5: Daily Reports list — project number clickable
# ══════════════════════════════════════════════════════════
old = '''                    <td className="px-4 py-3"><div className="text-xs font-bold text-slate-700">{proj?.number||"—"}</div><div className="text-xs text-slate-400 truncate max-w-[120px]">{proj?.name}</div></td>
                    <td className="px-4 py-3 text-xs font-semibold text-slate-800 whitespace-nowrap">{fmtDate(r.date)}</td>'''
new = '''                    <td className="px-4 py-3"><div className="text-xs font-bold text-amber-700 cursor-pointer hover:underline" onClick={()=>onNavigate&&onNavigate("projects",{projectId:r.pid})}>{proj?.number||"—"}</div><div className="text-xs text-slate-400 truncate max-w-[120px]">{proj?.name}</div></td>
                    <td className="px-4 py-3 text-xs font-semibold text-slate-800 whitespace-nowrap">{fmtDate(r.date)}</td>'''
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 5: Reports project number clickable")

# ══════════════════════════════════════════════════════════
# FIX 6: Material Requests list — project number clickable
# ══════════════════════════════════════════════════════════
old = '''                    <td className="px-4 py-3"><div className="text-xs font-bold text-slate-800">{proj?.number||"—"}</div><div className="text-xs text-slate-400 max-w-[120px] truncate">{proj?.name}</div></td>
                    <td className="px-4 py-3 text-xs"><span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-semibold">{m.dept}</span></td>'''
new = '''                    <td className="px-4 py-3"><div className="text-xs font-bold text-amber-700 cursor-pointer hover:underline" onClick={()=>onNavigate&&onNavigate("projects",{projectId:m.pid})}>{proj?.number||"—"}</div><div className="text-xs text-slate-400 max-w-[120px] truncate">{proj?.name}</div></td>
                    <td className="px-4 py-3 text-xs"><span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-semibold">{m.dept}</span></td>'''
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 6: MR project number clickable")

# ══════════════════════════════════════════════════════════
# FIX 7: LPO list — project number clickable
# ══════════════════════════════════════════════════════════
old = '''                    <td className="px-4 py-3 text-xs font-bold text-slate-700">{proj?.number||"—"}</td>
                    <td className="px-4 py-3"><div className="font-medium text-slate-800 max-w-[140px] truncate">{l.supplierName}</div>'''
new = '''                    <td className="px-4 py-3 text-xs font-bold text-amber-700 cursor-pointer hover:underline" onClick={()=>onNavigate&&onNavigate("projects",{projectId:l.pid})}>{proj?.number||"—"}</td>
                    <td className="px-4 py-3"><div className="font-medium text-slate-800 max-w-[140px] truncate">{l.supplierName}</div>'''
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 7: LPO project number clickable")

# ══════════════════════════════════════════════════════════
# FIX 8: NOC list — project number clickable
# ══════════════════════════════════════════════════════════
old = '                    <td className="px-4 py-3 text-xs font-bold text-slate-700">{proj?.number||"—"}</td>\n                    <td className="px-4 py-3">\n                      <span className={`text-xs font-bold text-white px-2 py-0.5 rounded-full ${authColor}`}>'
new = '                    <td className="px-4 py-3 text-xs font-bold text-amber-700 cursor-pointer hover:underline" onClick={()=>onNavigate&&onNavigate("projects",{projectId:n.pid})}>{proj?.number||"—"}</td>\n                    <td className="px-4 py-3">\n                      <span className={`text-xs font-bold text-white px-2 py-0.5 rounded-full ${authColor}`}>'
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 8: NOC project number clickable")

# ══════════════════════════════════════════════════════════
# FIX 9: Inspections list — project number clickable
# ══════════════════════════════════════════════════════════
old = '                  <td className="px-4 py-3 text-xs text-slate-500">{projects.find(p => p.id === i.pid)?.number || "—"}</td>'
new = '                  <td className="px-4 py-3 text-xs font-bold text-amber-700 cursor-pointer hover:underline" onClick={()=>onNavigate&&onNavigate("projects",{projectId:i.pid})}>{projects.find(p => p.id === i.pid)?.number || "—"}</td>'
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 9: Inspections project number clickable")

# ══════════════════════════════════════════════════════════
# FIX 10: Add DPR Export PDF + Excel to DPR LIST view
# (already has ExportButtons — check)
# ══════════════════════════════════════════════════════════
# DPR VIEW mode: add export buttons alongside Edit/Delete
old = '''      <div className="flex flex-wrap gap-3">
          <Btn onClick={()=>openEdit(sel)} label="Edit Report"/>
          {sel.status==="Draft"&&<button onClick={async()=>{setSaving(true);const r=await onUpdate(sel.id,{...sel,status:"Submitted"});setSaving(false);if(r.ok){setSel(p=>({...p,status:"Submitted"}));showToast("Report submitted!");}}} className="bg-green-600 hover:bg-green-700 text-white font-semibold text-sm px-4 py-2 rounded-lg">Submit Final</button>}
          <Btn onClick={()=>setConfirmId(sel.id)} label="Delete" color="red"/>
        </div>'''
new = '''      <div className="flex flex-wrap gap-3">
          <button onClick={()=>exportDailyReportPDF(sel, projects.find(p=>p.id===sel.pid)?.name)} className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-lg border bg-red-50 text-red-700 border-red-300 hover:bg-red-100">📄 Export PDF</button>
          <button onClick={()=>{const proj=projects.find(p=>p.id===sel.pid);const mp=(sel.manpower||[]);const data=[{Report_No:sel.reportNum,Date:sel.date,Project:proj?.number||"",Project_Name:proj?.name||"",Prepared_By:sel.preparedBy,Weather:sel.weather,Temperature:sel.temp+"°C",Work_Hours:sel.workHours,Total_Manpower:mp.reduce((s,r)=>s+(Number(r.count)||0),0),Issues:sel.issues,Remarks:sel.remarks,Status:sel.status}];exportToExcel(data,[{header:"Report No",key:"Report_No",width:14},{header:"Date",key:"Date",width:14},{header:"Project",key:"Project",width:12},{header:"Project Name",key:"Project_Name",width:30},{header:"Prepared By",key:"Prepared_By",width:20},{header:"Weather",key:"Weather",width:12},{header:"Temp",key:"Temperature",width:10},{header:"Work Hours",key:"Work_Hours",width:12},{header:"Manpower",key:"Total_Manpower",width:12},{header:"Issues",key:"Issues",width:30},{header:"Remarks",key:"Remarks",width:30},{header:"Status",key:"Status",width:12}],"DPR_"+sel.reportNum);}} className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-lg border bg-green-50 text-green-700 border-green-300 hover:bg-green-100">📊 Export Excel</button>
          <Btn onClick={()=>openEdit(sel)} label="Edit Report"/>
          {sel.status==="Draft"&&<button onClick={async()=>{setSaving(true);const r=await onUpdate(sel.id,{...sel,status:"Submitted"});setSaving(false);if(r.ok){setSel(p=>({...p,status:"Submitted"}));showToast("Report submitted!");}}} className="bg-green-600 hover:bg-green-700 text-white font-semibold text-sm px-4 py-2 rounded-lg">Submit Final</button>}
          <Btn onClick={()=>setConfirmId(sel.id)} label="Delete" color="red"/>
        </div>'''
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 10: DPR Export PDF+Excel added to view")
else:
    print("WARN FIX 10: DPR view buttons pattern not found")

# ══════════════════════════════════════════════════════════
# FIX 11: Progress Module — add recordDate field
# ══════════════════════════════════════════════════════════
old = "const EMPTY_PG = { pid:\"\",activity:\"\",plannedStart:\"\",plannedEnd:\"\",actualStart:\"\",actualEnd:\"\",pct:0,status:\"Not Started\",remarks:\"\" };"
new = "const EMPTY_PG = { pid:\"\",activity:\"\",recordDate:\"\",plannedStart:\"\",plannedEnd:\"\",actualStart:\"\",actualEnd:\"\",pct:0,status:\"Not Started\",remarks:\"\" };"
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 11a: EMPTY_PG recordDate added")

# Add recordDate in openEditPg
old = "setSelPg(pg); setPgForm({pid:pg.pid,activity:pg.activity,plannedStart:pg.plannedStart,plannedEnd:pg.plannedEnd,actualStart:pg.actualStart,actualEnd:pg.actualEnd,pct:pg.pct,status:pg.status,remarks:pg.remarks});"
new = "setSelPg(pg); setPgForm({pid:pg.pid,activity:pg.activity,recordDate:pg.recordDate||'',plannedStart:pg.plannedStart,plannedEnd:pg.plannedEnd,actualStart:pg.actualStart,actualEnd:pg.actualEnd,pct:pg.pct,status:pg.status,remarks:pg.remarks});"
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 11b: openEditPg recordDate added")

# Add date field in progress form UI (insert after "Activity Name" row)
old = '''                <div className="grid grid-cols-2 gap-3">
                  <div><Lbl t="Activity Name" req/>
                    <Sel value={pgForm.activity'''
new = '''                <div className="grid grid-cols-2 gap-3">
                  <div><Lbl t="Record / Entry Date"/><Inp type="date" value={pgForm.recordDate||""} onChange={e=>setPgForm(p=>({...p,recordDate:e.target.value}))}/></div>
                  <div></div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div><Lbl t="Activity Name" req/>
                    <Sel value={pgForm.activity'''
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 11c: Progress date field added to form UI")

# ══════════════════════════════════════════════════════════
# FIX 12: useProjectProgress — add recordDate to map + insert
# ══════════════════════════════════════════════════════════
# Map from DB
old = "      activity: p.activity_name || \"\",\n      plannedStart: p.planned_start_date"
new = "      activity: p.activity_name || \"\", recordDate: p.record_date || \"\",\n      plannedStart: p.planned_start_date"
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 12a: useProjectProgress map recordDate")

# Insert
old = "      project_id: f.pid, activity_name: f.activity,\n      planned_start_date: f.plannedStart"
new = "      project_id: f.pid, activity_name: f.activity, record_date: f.recordDate || null,\n      planned_start_date: f.plannedStart"
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 12b: useProjectProgress insert recordDate")

# Update
old = "      activity_name: f.activity,\n      planned_start_date: f.plannedStart"
new = "      activity_name: f.activity, record_date: f.recordDate || null,\n      planned_start_date: f.plannedStart"
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 12c: useProjectProgress update recordDate")

# ══════════════════════════════════════════════════════════
# FIX 13: Drawings list — project number clickable
# ══════════════════════════════════════════════════════════
old = "                  <td className=\"px-4 py-3 text-xs text-slate-500\">{projects.find(p => p.id === d.pid)?.number || \"—\"}</td>"
new = "                  <td className=\"px-4 py-3 text-xs font-bold text-amber-700 cursor-pointer hover:underline\" onClick={()=>onNavigate&&onNavigate(\"projects\",{projectId:d.pid})}>{projects.find(p => p.id === d.pid)?.number || \"—\"}</td>"
if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 13: Drawings project number clickable")

# ══════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════
with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved. Total changes: {changes}")
print("\nRUN:")
print("  set CI=false && npm run build")
print("  git add src/App.js && git commit -m 'feat: project click + DPR export + progress date' && git push")
input("\nPress Enter to exit...")
