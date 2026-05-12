import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# Exact pattern from the FOUND output
OLD = 'activity: p.activity_name || "",\n      plannedStart: p.planned_start_date || "", plannedEnd: p.planned_finish_date || "",\n      actualStart: p.actual_start_date || "", actualEnd: p.actual_finish_date'

NEW = 'activity: p.activity_name || "", customActivity: p.custom_activity || "",\n      unit: p.unit || "NOS",\n      actualQty: Number(p.actual_qty)||0, workDoneQty: Number(p.work_done_qty)||0, balanceQty: Number(p.balance_qty)||0,\n      recordDate: p.record_date || "",\n      plannedStart: p.planned_start_date || "", plannedEnd: p.planned_finish_date || "",\n      actualStart: p.actual_start_date || "", actualEnd: p.actual_finish_date'

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    changes += 1
    print("FIX 4: Map updated ✅")
else:
    print("WARN: Exact pattern still not matched — printing chars around 116102...")
    snippet = content[116050:116350]
    print(repr(snippet))

# Also fix pct auto-calc from qty
old_pct = "      pct: Number(p.progress_percentage)||0,"
new_pct = '      pct: (()=>{ const u=p.unit||"NOS"; const a=Number(p.actual_qty)||0; const d=Number(p.work_done_qty)||0; return u!=="Lumpsum"&&a>0 ? Math.min(100,Math.round((d/a)*100)) : Number(p.progress_percentage)||0; })(),'
if old_pct in content:
    content = content.replace(old_pct, new_pct, 1)
    changes += 1
    print("FIX 4b: pct auto-calc from qty ✅")
else:
    # try without leading spaces
    old_pct2 = "pct: Number(p.progress_percentage)||0,"
    if old_pct2 in content:
        content = content.replace(old_pct2, 'pct: (()=>{ const u=p.unit||"NOS"; const a=Number(p.actual_qty)||0; const d=Number(p.work_done_qty)||0; return u!=="Lumpsum"&&a>0 ? Math.min(100,Math.round((d/a)*100)) : Number(p.progress_percentage)||0; })(),', 1)
        changes += 1
        print("FIX 4b: pct auto-calc (alt pattern) ✅")
    else:
        print("WARN: pct pattern not found")

with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print(f"\nSaved. Changes: {changes}")
if changes > 0:
    print("\nRUN:")
    print("  set CI=false && npm run build")
    print("  git add src/App.js && git commit -m 'fix: progress map qty fields' && git push")
input("\nPress Enter...")
