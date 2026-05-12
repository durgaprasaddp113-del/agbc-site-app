import os, shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup: " + bk)

with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

changes = 0

# FIX 1 ONLY: Add case "manpower-master" to renderPage switch
# Do NOT touch useStore, MaterialStore, or anything else
OLD = 'default: return <div className="p-12 text-center text-slate-400 text-lg font-semibold">Module coming soon</div>;'
NEW = ('case "manpower-master": return <ManpowerMaster subcontractors={subs} projects={projects} showToast={showToast}/>;\n      '
       + OLD)

if OLD in app:
    app = app.replace(OLD, NEW, 1)
    changes += 1
    print("FIXED: case manpower-master added")
else:
    print("WARN: default case not found - showing nearby code:")
    idx = app.find("Module coming soon")
    if idx != -1:
        print(app[max(0,idx-200):idx+100])

with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print("Done - " + str(changes) + " change")
print("Run: set CI=false && npm run build")
print("     npx vercel --prod --force")
input("Press Enter...")
