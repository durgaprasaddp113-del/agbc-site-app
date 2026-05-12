#!/usr/bin/env python3
import os, shutil
from datetime import datetime

APP = r"src\App.js"
if not os.path.exists(APP):
    print("ERROR: src\\App.js not found"); input(); exit(1)

bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup: " + bk)

with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

changes = 0

# FIX 1: Add case manpower-master
OLD_DEF = 'default: return <div className="p-12 text-center text-slate-400 text-lg font-semibold">Module coming soon</div>;'
NEW_DEF = 'case "manpower-master": return <ManpowerMaster subcontractors={subs} projects={projects} showToast={showToast}/>;\n      ' + OLD_DEF

if OLD_DEF in app:
    app = app.replace(OLD_DEF, NEW_DEF, 1)
    changes += 1
    print("FIX 1 OK: case manpower-master added to renderPage")
else:
    print("WARN FIX 1: default case not found")

# FIX 2a: useStore destructuring
old2a = 'const { stock, receipts, issues, loading: stLoad, addStock, updateStock, removeStock, addReceipt, approveReceipt, removeReceipt, addIssue, removeIssue } = useStore();'
new2a = 'const { stock, receipts, issues, loading: stLoad, addStock, updateStock, removeStock, addReceipt, updateReceipt, removeReceipt, addIssue, removeIssue } = useStore();'
if old2a in app:
    app = app.replace(old2a, new2a, 1)
    changes += 1
    print("FIX 2a OK: useStore destructuring updated")
else:
    print("WARN FIX 2a: not matched")

# FIX 2b: case store prop
if 'onApproveReceipt={approveReceipt}' in app:
    app = app.replace('onApproveReceipt={approveReceipt}', 'onUpdateReceipt={updateReceipt}')
    changes += 1
    print("FIX 2b OK: prop replaced in case store")

# FIX 2c: MaterialStore component prop
if 'onApproveReceipt,' in app:
    app = app.replace('onApproveReceipt,', 'onUpdateReceipt,')
    changes += 1
    print("FIX 2c OK: MaterialStore prop renamed")

# FIX 2d: rename in useStore function body
us = app.find("function useStore() {")
if us != -1:
    chunk = app[us:us+9000]
    if 'approveReceipt' in chunk:
        app = app[:us] + chunk.replace('approveReceipt', 'updateReceipt') + app[us+9000:]
        changes += 1
        print("FIX 2d OK: renamed in useStore body")

# FIX 3: LPO Others
lpo_s = app.find("const LPOModule = (")
if lpo_s == -1:
    lpo_s = app.find("const LPO = (")

if lpo_s != -1:
    lpo = app[lpo_s:lpo_s+25000]

    found_field = None
    for field in ['category', 'lpoType', 'scope', 'itemType', 'type']:
        if ('onChange={set("' + field + '")}') in lpo or ("onChange={set('" + field + "')}") in lpo:
            found_field = field
            print("LPO field found: " + field)
            break

    if found_field:
        cap = found_field[0].upper() + found_field[1:]
        on_str = 'onChange={set("' + found_field + '")}'
        if on_str not in lpo:
            on_str = "onChange={set('" + found_field + "')}"

        p = lpo.find(on_str)
        sel_s = lpo.rfind('<Sel', 0, p)
        sel_e = lpo.find('</Sel>', p)

        if sel_s != -1 and sel_e != -1:
            old_sel = lpo[sel_s:sel_e+6]
            if 'Others' not in old_sel:
                last_o = old_sel.rfind('</option>')
                new_sel = (old_sel[:last_o+9]
                           + '\n                <option>Others</option>'
                           + old_sel[last_o+9:])
                custom_input = (
                    '\n              {form.' + found_field + '==="Others" && (\n'
                    '                <Inp value={form.custom' + cap + '||""} '
                    'onChange={e=>setForm(p=>({...p,custom' + cap + ':e.target.value}))} '
                    'placeholder="Specify..." className="mt-2 border-amber-300"/>\n'
                    '              )}'
                )
                replacement = new_sel + custom_input
                lpo = lpo[:sel_s] + replacement + lpo[sel_e+6:]
                app = app[:lpo_s] + lpo + app[lpo_s+25000:]
                changes += 1
                print("FIX 3 OK: Others + custom input added to LPO field: " + found_field)
            else:
                print("FIX 3: Others already exists in LPO")
    else:
        print("WARN FIX 3: LPO field not found - showing LPO form:")
        fi = lpo.find('mode === "form"')
        if fi == -1:
            fi = lpo.find('mode==="form"')
        if fi != -1:
            for ln in lpo[fi:fi+600].split('\n')[:20]:
                print("  " + ln)
        else:
            print("  LPO form section not found either")
else:
    print("WARN FIX 3: LPOModule not found")

# Write
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 55)
print("Done - " + str(changes) + " fixes applied")
print("Backup: " + bk)
print()
print("Run: set CI=false && npm run build")
print("     npx vercel --prod")
print("=" * 55)
input("Press Enter...")
