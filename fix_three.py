#!/usr/bin/env python3
"""
Diagnose and fix 3 issues:
1. Manpower Master shows "Module coming soon"
2. Material Store blank page
3. LPO Others not working
Run from: C:\Apps\agbc-site-app\
Command:  python fix_three.py
"""
import os, shutil, re
from datetime import datetime

APP = r"src\App.js"
if not os.path.exists(APP):
    print("ERROR: src\\App.js not found"); input(); exit(1)

bk = APP + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(APP, bk)
print(f"Backup: {bk}")

with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

changes = 0

# ─────────────────────────────────────────────────────────────────────────────
# DIAGNOSTIC
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== DIAGNOSTIC ===")
print(f"ManpowerMaster component exists : {'const ManpowerMaster' in app}")
print(f"useManpowerMaster hook exists   : {'useManpowerMaster' in app}")
print(f"case manpower-master exists     : {'manpower-master' in app}")
print(f"MaterialStore component exists  : {'const MaterialStore' in app}")
print(f"useStore hook exists            : {'function useStore' in app}")
print(f"case store exists               : {'case \"store\"' in app}")
print(f"LPO Others field exists         : {'customLpoType' in app or 'Others' in app}")

# Show current case "manpower-master"
idx = app.find('"manpower-master"')
if idx != -1:
    print(f"\ncase manpower-master context:")
    print(app[max(0,idx-100):idx+200])

# Show current case "store"
idx2 = app.find('case "store"')
if idx2 != -1:
    print(f"\ncase store context:")
    print(app[idx2:idx2+200])

print("\n=== FIXES ===")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 1 — Manpower Master case statement
# The case exists but renders "Module coming soon" instead of ManpowerMaster
# ─────────────────────────────────────────────────────────────────────────────

# Find the renderPage function or switch statement
render_patterns = [
    # Pattern: case "manpower-master": return <div>Module coming soon</div>
    'case "manpower-master": return <div',
    "case 'manpower-master': return <div",
    'case "manpower-master":\n        return <div',
    'case "manpower-master": ',
]

mp_case_found = False
for pat in render_patterns:
    if pat in app:
        # Find full case line
        idx = app.find(pat)
        # Find end of this case (next case or end of switch)
        line_end = app.find('\n', idx)
        old_case_line = app[idx:line_end]
        print(f"Found: {old_case_line[:80]}")
        mp_case_found = True

        # Replace with correct render
        new_case = 'case "manpower-master": return <ManpowerMaster subcontractors={subcontractors} projects={projects} showToast={showToast}/>;'
        app = app[:idx] + new_case + app[line_end:]
        changes += 1
        print("✅ Fix 1: case manpower-master now renders ManpowerMaster component")
        break

if not mp_case_found:
    # Check if ManpowerMaster component exists but case is missing
    if "const ManpowerMaster" in app:
        # Find where other cases are and add manpower-master
        store_case = app.find('case "store":')
        if store_case != -1:
            new_mp_case = 'case "manpower-master": return <ManpowerMaster subcontractors={subcontractors} projects={projects} showToast={showToast}/>;\n      '
            app = app[:store_case] + new_mp_case + app[store_case:]
            changes += 1
            print("✅ Fix 1: Added case manpower-master before case store")
        else:
            print("⚠️  Fix 1: Could not find insertion point for manpower case")
    else:
        print("⚠️  Fix 1: ManpowerMaster component not in App.js — was module injection skipped?")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 2 — Material Store blank page
# Most common cause: props mismatch — component expects prop that isn't passed
# ─────────────────────────────────────────────────────────────────────────────

# Find current case "store" render
store_case_idx = app.find('case "store":')
if store_case_idx != -1:
    store_line_end = app.find('\n', store_case_idx)
    old_store_case = app[store_case_idx:store_line_end]
    print(f"\nCurrent store case: {old_store_case[:120]}")

    # Build correct store case with all required props
    new_store_case = 'case "store": return <MaterialStore stock={stock} receipts={receipts} issues={issues} loading={stLoad} onAddStock={addStock} onUpdateStock={updateStock} onRemoveStock={removeStock} onAddReceipt={addReceipt} onUpdateReceipt={updateReceipt} onRemoveReceipt={removeReceipt} onAddIssue={addIssue} onRemoveIssue={removeIssue} projects={projects} lpos={lpos} showToast={showToast}/>;'

    if old_store_case != new_store_case:
        app = app[:store_case_idx] + new_store_case + app[store_line_end:]
        changes += 1
        print("✅ Fix 2: case store updated with correct props")
    else:
        print("✅ Fix 2: case store already correct")

    # Also ensure useStore destructuring has updateReceipt
    old_d1 = 'const { stock, receipts, issues, loading: stLoad, addStock, updateStock, removeStock, addReceipt, removeReceipt, addIssue, removeIssue } = useStore();'
    new_d  = 'const { stock, receipts, issues, loading: stLoad, addStock, updateStock, removeStock, addReceipt, updateReceipt, removeReceipt, addIssue, removeIssue } = useStore();'
    if old_d1 in app:
        app = app.replace(old_d1, new_d, 1)
        changes += 1
        print("✅ Fix 2b: Added updateReceipt to useStore destructuring")

    # Check if MaterialStore has error boundary protection
    ms_idx = app.find("const MaterialStore = (")
    if ms_idx != -1:
        # Check if stock/receipts/issues have default values in destructuring
        ms_props = app[ms_idx:ms_idx+200]
        if "stock = []" not in ms_props and "stock," in ms_props:
            # Add default values to prevent blank page from undefined props
            old_ms_props_patterns = [
                "const MaterialStore = ({\n  stock, receipts, issues, loading,",
                "const MaterialStore = ({ stock, receipts, issues, loading,",
                "const MaterialStore = ({stock, receipts, issues, loading,",
            ]
            for old_p in old_ms_props_patterns:
                if old_p in app:
                    new_p = old_p.replace(
                        "stock, receipts, issues, loading,",
                        "stock=[], receipts=[], issues=[], loading,"
                    )
                    app = app.replace(old_p, new_p, 1)
                    changes += 1
                    print("✅ Fix 2c: Added default empty arrays to MaterialStore props")
                    break
else:
    print("⚠️  Fix 2: case store not found")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 3 — LPO Others field
# When "Others" is selected in LPO type/category, show manual input
# ─────────────────────────────────────────────────────────────────────────────

# Find LPO module
lpo_start = app.find("const LPOModule = (")
if lpo_start == -1: lpo_start = app.find("const LPO = (")
if lpo_start == -1: lpo_start = app.find("function LPO(")

if lpo_start != -1:
    lpo_body = app[lpo_start:]

    # Check if LPO has category/type field
    has_lpo_type = "lpoType" in lpo_body or "lpo_type" in lpo_body or "category" in lpo_body

    # Find the LPO form and look for "Others" handling
    # Pattern 1: Select with options including "Others"
    others_in_lpo = "Others" in lpo_body[:5000]
    print(f"\nLPO module found: yes")
    print(f"LPO type/category field: {has_lpo_type}")
    print(f"Others option in LPO: {others_in_lpo}")

    # Find LPO supplier or category select
    # Most likely the "Others" is in supplier name or LPO type
    # Look for supplier select pattern
    supplier_sel = lpo_body.find("supplierName")
    if supplier_sel == -1:
        supplier_sel = lpo_body.find("supplier_name")

    print(f"Supplier field exists: {supplier_sel != -1}")

    # Fix: Add "Others" with custom input for supplier if it's a select
    # First check if supplier is a select or free text
    if supplier_sel != -1:
        chunk = lpo_body[supplier_sel:supplier_sel+300]
        is_select = "<Sel" in chunk or "<select" in chunk
        print(f"Supplier is select (not free text): {is_select}")

    # Common fix: if LPO category/type select has Others but no custom input
    # Pattern to find and fix
    lpo_others_patterns = [
        # Category select with Others but no custom field below
        (
            '<option value="Others">Others</option>\n              </Sel>\n            </div>',
            '<option value="Others">Others</option>\n              </Sel>\n              {(form.category==="Others"||form.lpoType==="Others") && (\n                <Inp value={form.customCategory||""} onChange={e=>setForm(p=>({...p,customCategory:e.target.value}))} placeholder="Specify type..." className="mt-2"/>\n              )}\n            </div>'
        ),
        (
            '<option>Others</option>\n              </Sel>\n            </div>',
            '<option>Others</option>\n              </Sel>\n              {form.category==="Others" && (\n                <Inp value={form.customCategory||""} onChange={e=>setForm(p=>({...p,customCategory:e.target.value}))} placeholder="Specify category..." className="mt-2"/>\n              )}\n            </div>'
        ),
    ]

    fixed_lpo = False
    for old, new in lpo_others_patterns:
        if old in lpo_body:
            lpo_body = lpo_body.replace(old, new, 1)
            app = app[:lpo_start] + lpo_body
            changes += 1
            fixed_lpo = True
            print("✅ Fix 3: LPO Others custom input added")
            break

    if not fixed_lpo:
        # Try to find the LPO form's category/type field generically
        # Look for <option>Others</option> or value="Others" in LPO
        others_idx = lpo_body.find('"Others"')
        if others_idx == -1:
            others_idx = lpo_body.find('>Others<')

        if others_idx != -1:
            print(f"Found Others at LPO position {others_idx}")
            ctx = lpo_body[max(0,others_idx-200):others_idx+200]
            print(f"Context: {ctx[:300]}")

            # Find the closing </div> after the Sel containing Others
            sel_end = lpo_body.find('</Sel>', others_idx)
            if sel_end == -1:
                sel_end = lpo_body.find('</select>', others_idx)

            if sel_end != -1:
                # Find next </div> after </Sel>
                div_end = lpo_body.find('</div>', sel_end)
                if div_end != -1:
                    # Check what field name to use
                    # Look backwards for the field key
                    before_sel = lpo_body[max(0,others_idx-400):others_idx]
                    field_key = "category"
                    for fk in ["lpoType","category","type","procurementType"]:
                        if fk in before_sel:
                            field_key = fk
                            break

                    insert_pos = lpo_body.find('\n', sel_end) + 1
                    custom_input = (
                        f'              {{form.{field_key}==="Others" && (\n'
                        f'                <Inp value={{form.custom{field_key.capitalize()}||""}} '
                        f'onChange={{e=>setForm(p=>({{{...p},custom{field_key.capitalize()}:e.target.value}}))}}'
                        f' placeholder="Specify..." className="mt-2"/>\n'
                        f'              )}}\n'
                    )
                    lpo_body = lpo_body[:insert_pos] + custom_input + lpo_body[insert_pos:]
                    app = app[:lpo_start] + lpo_body
                    changes += 1
                    fixed_lpo = True
                    print(f"✅ Fix 3: Added custom input after Others for field: {field_key}")

    if not fixed_lpo:
        print("⚠️  Fix 3: LPO Others field could not be auto-fixed")
        print("   Share the LPO form section and I will fix it manually")
else:
    print("⚠️  Fix 3: LPO module not found")

# ─────────────────────────────────────────────────────────────────────────────
# WRITE
# ─────────────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 60)
print(f"✅ Done — {changes} fixes applied")
print(f"   Backup: {bk}")
print()
print("Run: set CI=false && npm run build")
print("     npx vercel --prod")
print("=" * 60)
input("Press Enter to exit...")
