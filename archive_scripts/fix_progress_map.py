import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# FIX: useProjectProgress map — read new columns from DB rows
# Find the map function inside useProjectProgress
targets = [
    # Pattern A — after previous fixes
    (
        "      activity: p.activity_name || \"\", customActivity: p.custom_activity || \"\",\n      unit: p.unit || \"NOS\", actualQty: Number(p.actual_qty)||0,\n      workDoneQty: Number(p.work_done_qty)||0, balanceQty: Number(p.balance_qty)||0,\n      recordDate: p.record_date || \"\",\n      plannedStart: p.planned_start_date",
        None  # already correct
    ),
    # Pattern B — original without qty fields
    (
        "      activity: p.activity_name || \"\",\n      plannedStart: p.planned_start_date",
        "      activity: p.activity_name || \"\", customActivity: p.custom_activity || \"\",\n      unit: p.unit || \"NOS\", actualQty: Number(p.actual_qty)||0,\n      workDoneQty: Number(p.work_done_qty)||0, balanceQty: Number(p.balance_qty)||0,\n      recordDate: p.record_date || \"\",\n      plannedStart: p.planned_start_date"
    ),
    # Pattern C — with only recordDate added
    (
        "      activity: p.activity_name || \"\", recordDate: p.record_date || \"\",\n      plannedStart: p.planned_start_date",
        "      activity: p.activity_name || \"\", customActivity: p.custom_activity || \"\",\n      unit: p.unit || \"NOS\", actualQty: Number(p.actual_qty)||0,\n      workDoneQty: Number(p.work_done_qty)||0, balanceQty: Number(p.balance_qty)||0,\n      recordDate: p.record_date || \"\",\n      plannedStart: p.planned_start_date"
    ),
]

for old, new in targets:
    if new is None:
        if old in content:
            print("FIX 4: Already correct — map has qty fields ✅")
            break
    elif old in content:
        content = content.replace(old, new, 1)
        changes += 1
        print(f"FIX 4: useProjectProgress map updated ✅")
        break
else:
    # Manual search — show context around activity_name
    idx = content.find("activity: p.activity_name")
    if idx > -1:
        print(f"FOUND at char {idx}:")
        print(repr(content[idx:idx+200]))
    else:
        print("WARN: 'activity: p.activity_name' not found at all")

# Also fix pct calculation when work_done/actual exist in map
old_pct = "      pct: Number(p.progress_percentage)||0,"
new_pct = """      pct: (()=>{ const u=p.unit||"NOS"; const a=Number(p.actual_qty)||0; const d=Number(p.work_done_qty)||0; return u!=="Lumpsum"&&a>0 ? Math.min(100,Math.round((d/a)*100)) : Number(p.progress_percentage)||0; })(),"""
if old_pct in content:
    content = content.replace(old_pct, new_pct, 1)
    changes += 1
    print("FIX 4b: pct auto-calc from qty in map ✅")

with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print(f"\nSaved. Changes: {changes}")
if changes > 0:
    print("\nRUN:")
    print("  set CI=false && npm run build")
    print("  git add src/App.js && git commit -m 'fix: progress map qty fields' && git push")
else:
    print("\nNo changes needed — check WARN messages above")
input("\nPress Enter...")
