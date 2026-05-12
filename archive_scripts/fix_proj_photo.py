import shutil, re
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print(f"Backup: {bk}")

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# ══════════════════════════════════════════════════════════════════
# FIX 1: Project number cell clickable → openView(p)
# L2670 exact pattern
# ══════════════════════════════════════════════════════════════════
OLD_NUM = '<td className="px-4 py-3 font-mono text-xs font-bold text-amber-700">{p.number}</td>'
NEW_NUM = '<td className="px-4 py-3 font-mono text-xs font-bold text-amber-700 cursor-pointer hover:underline hover:text-amber-900 select-none" title="Click to open project" onClick={()=>openView(p)}>{p.number}</td>'
if OLD_NUM in content:
    content = content.replace(OLD_NUM, NEW_NUM, 1)
    changes += 1
    print("FIX 1: Project number clickable → openView ✅")
else:
    print("WARN FIX 1: project number td not found")

# ══════════════════════════════════════════════════════════════════
# FIX 2: Project VIEW mode — add Export PDF + Excel buttons
# L2438-2441 exact pattern
# ══════════════════════════════════════════════════════════════════
OLD_BTNS = '''          <div className="flex gap-3 mt-4 pt-4 border-t border-slate-100">
            <Btn onClick={()=>openEdit(sel)} label="Edit Project"/>
            <Btn onClick={()=>setConfirmId(sel.id)} label="Delete" color="red"/>
          </div>'''

NEW_BTNS = '''          <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-100">
            <button onClick={()=>{
              const pgRows = progressItems.filter(pg=>pg.pid===sel.id);
              const data = pgRows.length>0 ? pgRows.map(pg=>({
                Activity: getActivityLabel(pg)||pg.activity,
                Unit: pg.unit||"NOS",
                Actual_Qty: pg.unit==="Lumpsum"?"L/S":(pg.actualQty||0),
                Work_Done: pg.unit==="Lumpsum"?(pg.pct||0)+"%":(pg.workDoneQty||0),
                Balance: pg.unit==="Lumpsum"?(100-(pg.pct||0))+"%":(pg.balanceQty||0),
                Progress_Pct: (pg.pct||0)+"%",
                Status: pg.status,
                Planned_Start: pg.plannedStart||"",
                Planned_End: pg.plannedEnd||"",
                Actual_Start: pg.actualStart||"",
                Actual_End: pg.actualEnd||"",
                Remarks: pg.remarks||"",
              })) : [{Project:sel.number, Name:sel.name, Location:sel.location, Status:sel.status, Progress:"No activities"}];
              const cols = pgRows.length>0 ? [
                {header:"Activity",key:"Activity",width:24},
                {header:"Unit",key:"Unit",width:10},
                {header:"Actual Qty",key:"Actual_Qty",width:12},
                {header:"Work Done",key:"Work_Done",width:12},
                {header:"Balance",key:"Balance",width:12},
                {header:"Progress %",key:"Progress_Pct",width:12},
                {header:"Status",key:"Status",width:14},
                {header:"Planned Start",key:"Planned_Start",width:14},
                {header:"Planned End",key:"Planned_End",width:14},
                {header:"Actual Start",key:"Actual_Start",width:14},
                {header:"Actual End",key:"Actual_End",width:14},
                {header:"Remarks",key:"Remarks",width:24},
              ] : [{header:"Project",key:"Project",width:14},{header:"Name",key:"Name",width:30},{header:"Location",key:"Location",width:20},{header:"Status",key:"Status",width:14},{header:"Progress",key:"Progress",width:20}];
              exportToExcel(data, cols, "Project_"+sel.number+"_Progress");
            }} className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-lg border bg-green-50 text-green-700 border-green-300 hover:bg-green-100">
              📊 Export Excel
            </button>
            <button onClick={()=>{
              const pgRows = progressItems.filter(pg=>pg.pid===sel.id);
              const pdfData = pgRows.length>0 ? pgRows.map(pg=>({
                Activity: getActivityLabel(pg)||pg.activity,
                Unit: pg.unit||"NOS",
                Actual_Qty: pg.unit==="Lumpsum"?"L/S":String(pg.actualQty||0),
                Work_Done: pg.unit==="Lumpsum"?(pg.pct||0)+"%":String(pg.workDoneQty||0),
                Balance: pg.unit==="Lumpsum"?(100-(pg.pct||0))+"%":String(pg.balanceQty||0),
                Progress_Pct: (pg.pct||0)+"%",
                Status: pg.status,
              })) : [{Activity:"No activities recorded",Unit:"",Actual_Qty:"",Work_Done:"",Balance:"",Progress_Pct:"0%",Status:""}];
              const pdfCols = [
                {header:"Activity",key:"Activity",pdfWidth:32},
                {header:"Unit",key:"Unit",pdfWidth:12},
                {header:"Actual Qty",key:"Actual_Qty",pdfWidth:16},
                {header:"Work Done",key:"Work_Done",pdfWidth:16},
                {header:"Balance",key:"Balance",pdfWidth:16},
                {header:"Progress %",key:"Progress_Pct",pdfWidth:16},
                {header:"Status",key:"Status",pdfWidth:16},
              ];
              exportToPDF(pdfData, pdfCols, "Project_"+sel.number+"_Progress", sel.number+" — "+sel.name+" | Progress Report | Overall: "+overallPct+"%", "landscape");
            }} className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-lg border bg-red-50 text-red-700 border-red-300 hover:bg-red-100">
              📄 Export PDF
            </button>
            <Btn onClick={()=>openEdit(sel)} label="Edit Project"/>
            <Btn onClick={()=>setConfirmId(sel.id)} label="Delete" color="red"/>
          </div>'''

if OLD_BTNS in content:
    content = content.replace(OLD_BTNS, NEW_BTNS, 1)
    changes += 1
    print("FIX 2: Project view Export PDF + Excel buttons added ✅")
else:
    print("WARN FIX 2: view buttons pattern not found")

# ══════════════════════════════════════════════════════════════════
# FIX 3a: EMPTY_PHOTO_UPLOAD — add photo_date field
# ══════════════════════════════════════════════════════════════════
OLD_EMPTY_UP = 'const EMPTY_PHOTO_UPLOAD = { pid: "", caption: "", area: "", file: null };'
NEW_EMPTY_UP = 'const EMPTY_PHOTO_UPLOAD = { pid: "", caption: "", area: "", photo_date: "", file: null };'
if OLD_EMPTY_UP in content:
    content = content.replace(OLD_EMPTY_UP, NEW_EMPTY_UP, 1)
    changes += 1
    print("FIX 3a: EMPTY_PHOTO_UPLOAD photo_date added ✅")

# FIX 3b: EMPTY_PHOTO_EDIT — add photo_date field
OLD_EMPTY_ED = 'const EMPTY_PHOTO_EDIT = { pid: "", caption: "", area: "" };'
NEW_EMPTY_ED = 'const EMPTY_PHOTO_EDIT = { pid: "", caption: "", area: "", photo_date: "" };'
if OLD_EMPTY_ED in content:
    content = content.replace(OLD_EMPTY_ED, NEW_EMPTY_ED, 1)
    changes += 1
    print("FIX 3b: EMPTY_PHOTO_EDIT photo_date added ✅")

# ══════════════════════════════════════════════════════════════════
# FIX 3c: handleUpload — require date
# ══════════════════════════════════════════════════════════════════
OLD_VALIDATE = '    if (!uploadForm.file || !uploadForm.pid) { showToast("Please select a project and photo", "error"); return; }'
NEW_VALIDATE = '    if (!uploadForm.file || !uploadForm.pid) { showToast("Please select a project and photo", "error"); return; }\n    if (!uploadForm.photo_date) { showToast("Please enter the photo date", "error"); return; }'
if OLD_VALIDATE in content:
    content = content.replace(OLD_VALIDATE, NEW_VALIDATE, 1)
    changes += 1
    print("FIX 3c: handleUpload date validation added ✅")

# ══════════════════════════════════════════════════════════════════
# FIX 3d: openEdit — include photo_date from existing record
# ══════════════════════════════════════════════════════════════════
OLD_OPEN_ED = '  const openEdit = p => { setSel(p); setEditForm({ pid: p.project_id, caption: p.caption || "", area: p.area || "" }); setMode("edit"); };'
NEW_OPEN_ED = '  const openEdit = p => { setSel(p); setEditForm({ pid: p.project_id, caption: p.caption || "", area: p.area || "", photo_date: p.photo_date || "" }); setMode("edit"); };'
if OLD_OPEN_ED in content:
    content = content.replace(OLD_OPEN_ED, NEW_OPEN_ED, 1)
    changes += 1
    print("FIX 3d: openEdit includes photo_date ✅")

# ══════════════════════════════════════════════════════════════════
# FIX 3e: Upload form UI — add date field before Caption
# ══════════════════════════════════════════════════════════════════
OLD_FORM_CAP = '        <div><Lbl t="Caption" /><Inp value={uploadForm.caption} onChange={e => setUploadForm(p => ({ ...p, caption: e.target.value }))} placeholder="e'
NEW_FORM_CAP = '        <div><Lbl t="Photo Date" req /><Inp type="date" value={uploadForm.photo_date||""} onChange={e => setUploadForm(p => ({ ...p, photo_date: e.target.value }))}/></div>\n        <div><Lbl t="Caption" /><Inp value={uploadForm.caption} onChange={e => setUploadForm(p => ({ ...p, caption: e.target.value }))} placeholder="e'
if OLD_FORM_CAP in content:
    content = content.replace(OLD_FORM_CAP, NEW_FORM_CAP, 1)
    changes += 1
    print("FIX 3e: Upload form date field added ✅")
else:
    print("WARN FIX 3e: caption field pattern not found (truncated match)")
    # Try broader match
    idx = content.find('<div><Lbl t="Caption" /><Inp value={uploadForm.caption}')
    if idx > -1:
        old_frag = content[idx:idx+120]
        new_frag = '<div><Lbl t="Photo Date" req /><Inp type="date" value={uploadForm.photo_date||""} onChange={e => setUploadForm(p => ({ ...p, photo_date: e.target.value }))}/></div>\n        ' + old_frag
        content = content[:idx] + new_frag + content[idx+len(old_frag):]
        changes += 1
        print("FIX 3e (alt): Upload form date field added ✅")

# ══════════════════════════════════════════════════════════════════
# FIX 3f: Edit form UI — add date field
# ══════════════════════════════════════════════════════════════════
OLD_EDIT_CAP = '        <div><Lbl t="Caption" /><Inp value={editForm.caption} onChange={e => setEditForm(p => ({ ...p, caption: e.target.value }))} placeholder="e'
NEW_EDIT_CAP = '        <div><Lbl t="Photo Date" /><Inp type="date" value={editForm.photo_date||""} onChange={e => setEditForm(p => ({ ...p, photo_date: e.target.value }))}/></div>\n        <div><Lbl t="Caption" /><Inp value={editForm.caption} onChange={e => setEditForm(p => ({ ...p, caption: e.target.value }))} placeholder="e'
if OLD_EDIT_CAP in content:
    content = content.replace(OLD_EDIT_CAP, NEW_EDIT_CAP, 1)
    changes += 1
    print("FIX 3f: Edit form date field added ✅")
else:
    idx = content.find('<div><Lbl t="Caption" /><Inp value={editForm.caption}')
    if idx > -1:
        old_frag = content[idx:idx+120]
        new_frag = '<div><Lbl t="Photo Date" /><Inp type="date" value={editForm.photo_date||""} onChange={e => setEditForm(p => ({ ...p, photo_date: e.target.value }))}/></div>\n        ' + old_frag
        content = content[:idx] + new_frag + content[idx+len(old_frag):]
        changes += 1
        print("FIX 3f (alt): Edit form date field added ✅")

# ══════════════════════════════════════════════════════════════════
# FIX 3g: usePhotos add — save photo_date to DB
# ══════════════════════════════════════════════════════════════════
OLD_INSERT = '''    const { error } = await supabase.from("project_photos").insert([{
      project_id: f.pid,
      file_url:   r2Result.url,   // ΓåÉ R2 CDN URL stored here
      caption:    f.caption,
      area:       f.area,
    }]);'''
NEW_INSERT = '''    const { error } = await supabase.from("project_photos").insert([{
      project_id: f.pid,
      file_url:   r2Result.url,
      caption:    f.caption,
      area:       f.area,
      photo_date: f.photo_date || null,
    }]);'''
if OLD_INSERT in content:
    content = content.replace(OLD_INSERT, NEW_INSERT, 1)
    changes += 1
    print("FIX 3g: usePhotos add saves photo_date ✅")
else:
    # Try without the comment
    OLD_INSERT2 = '      project_id: f.pid,\n      file_url:   r2Result.url,\n      caption:    f.caption,\n      area:       f.area,\n    }]);'
    if OLD_INSERT2 in content:
        content = content.replace(OLD_INSERT2,
            '      project_id: f.pid,\n      file_url:   r2Result.url,\n      caption:    f.caption,\n      area:       f.area,\n      photo_date: f.photo_date || null,\n    }]);', 1)
        changes += 1
        print("FIX 3g (alt): usePhotos add saves photo_date ✅")
    else:
        print("WARN FIX 3g: insert pattern not found")

# ══════════════════════════════════════════════════════════════════
# FIX 3h: usePhotos update — save photo_date to DB
# ══════════════════════════════════════════════════════════════════
OLD_UPDATE = '      project_id: f.pid, caption: f.caption, area: f.area,\n    }).eq("id", id);'
NEW_UPDATE = '      project_id: f.pid, caption: f.caption, area: f.area, photo_date: f.photo_date || null,\n    }).eq("id", id);'
if OLD_UPDATE in content:
    content = content.replace(OLD_UPDATE, NEW_UPDATE, 1)
    changes += 1
    print("FIX 3h: usePhotos update saves photo_date ✅")

# ══════════════════════════════════════════════════════════════════
# FIX 3i: Photo grid card — show date below caption
# ══════════════════════════════════════════════════════════════════
OLD_CARD = '<p className="text-slate-400 text-sm">{lightbox.area}'
NEW_CARD = '<p className="text-slate-400 text-sm">{lightbox.photo_date ? "📅 "+lightbox.photo_date+" · " : ""}{lightbox.area}'
if OLD_CARD in content:
    content = content.replace(OLD_CARD, NEW_CARD, 1)
    changes += 1
    print("FIX 3i: Lightbox shows date ✅")

# ══════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════
with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved. Total changes: {changes}")
print("\n⚠️  RUN THIS SQL IN SUPABASE FIRST:")
print("  ALTER TABLE project_photos ADD COLUMN IF NOT EXISTS photo_date DATE;")
print("  NOTIFY pgrst, 'reload schema';")
print("\nTHEN RUN:")
print("  set CI=false && npm run build")
print("  git add src/App.js && git commit -m 'fix: project click+export, photo date field' && git push")
input("\nPress Enter...")
