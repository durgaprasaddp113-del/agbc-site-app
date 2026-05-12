import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# The problem: report.activities/materials/safety are ARRAYS not strings
# exportDailyReportPDF expects strings and calls .trim()
# Fix: replace the PDF export button call with a helper that converts arrays→strings first

old = '''          <button onClick={()=>exportDailyReportPDF(sel, projects.find(p=>p.id===sel.pid)?.name)} className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-lg border bg-red-50 text-red-700 border-red-300 hover:bg-red-100">📄 Export PDF</button>'''

new = '''          <button onClick={()=>{
            const proj=projects.find(p=>p.id===sel.pid);
            const toStr=(arr,fn)=>Array.isArray(arr)?arr.filter(Boolean).map(fn).join("\\n"):(arr||"");
            const rpt={
              ...sel,
              activities: toStr(sel.activities, a=>`${a.location||""}: ${a.activity||""} (${a.trade||""}) ${a.progress||""}%`),
              materials:  toStr(sel.materials,  m=>`${m.material||""} — ${m.qty||0} ${m.unit||""} | ${m.supplier||""} | DN: ${m.dn||""}`),
              safety:     toStr(sel.safety,     s=>`[${s.severity||""}] ${s.obs||""} → ${s.action||""}`),
              completed:  toStr(sel.equipment,  e=>`${e.name||""} (${e.status||""}) — Op: ${e.operator||""}`),
              issues:     sel.issues||"",
              visitors:   sel.visitors||"",
              remarks:    sel.remarks||"",
            };
            exportDailyReportPDF(rpt, proj?.name||"");
          }} className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-lg border bg-red-50 text-red-700 border-red-300 hover:bg-red-100">📄 Export PDF</button>'''

if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX: DPR PDF export — arrays converted to strings")
else:
    print("WARN: DPR export button pattern not found — checking alternative...")
    # Try to find any exportDailyReportPDF call in view mode and fix it
    if 'exportDailyReportPDF(sel, projects.find(p=>p.id===sel.pid)?.name)' in content:
        content = content.replace(
            'exportDailyReportPDF(sel, projects.find(p=>p.id===sel.pid)?.name)',
            '''(()=>{const proj=projects.find(p=>p.id===sel.pid);const toStr=(arr,fn)=>Array.isArray(arr)?arr.filter(Boolean).map(fn).join("\\n"):(arr||"");const rpt={...sel,activities:toStr(sel.activities,a=>`${a.location||""}: ${a.activity||""} (${a.trade||""}) ${a.progress||""}%`),materials:toStr(sel.materials,m=>`${m.material||""} — ${m.qty||0} ${m.unit||""} | ${m.supplier||""}`),safety:toStr(sel.safety,s=>`[${s.severity||""}] ${s.obs||""} → ${s.action||""}`),completed:toStr(sel.equipment,e=>`${e.name||""} (${e.status||""})`)};exportDailyReportPDF(rpt,proj?.name||"");})()''',
            1
        )
        changes += 1
        print("FIX (alt): DPR PDF export call fixed")

with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print(f"\nSaved. Changes: {changes}")
print("RUN: set CI=false && npm run build")
print("     git add src/App.js && git commit -m 'fix: DPR PDF export array to string' && git push")
input("\nPress Enter...")
