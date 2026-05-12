import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# Exact pattern from pct_out.txt
OLD = 'pct: Number(p.progress_percentage) || 0,'
NEW = 'pct: (()=>{ const u=p.unit||"NOS"; const a=Number(p.actual_qty)||0; const d=Number(p.work_done_qty)||0; return (u!=="Lumpsum"&&a>0) ? Math.min(100,Math.round((d/a)*100)) : Number(p.progress_percentage)||0; })(),'

count = content.count(OLD)
print(f"Found '{OLD}' — {count} occurrence(s)")

if count == 1:
    content = content.replace(OLD, NEW, 1)
    changes += 1
    print("FIX: pct auto-calc from qty in map ✅")
elif count > 1:
    # Only replace inside useProjectProgress (first occurrence)
    content = content.replace(OLD, NEW, 1)
    changes += 1
    print(f"FIX: replaced first of {count} occurrences ✅")
else:
    print("WARN: pattern not found")

with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print(f"\nSaved. Changes: {changes}")
if changes:
    print("\nRUN:")
    print("  set CI=false && npm run build")
    print("  git add src/App.js && git commit -m 'fix: pct auto-calc from qty in progress map' && git push")
input("\nPress Enter...")
