import os, shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup: " + bk)

with open(APP, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Total lines: " + str(len(lines)))
changes = 0

# ─────────────────────────────────────────────────────────────────────────────
# FIX 1: Add missing EMPTY_STOCK_FORM and related constants before MaterialStore
# MaterialStore is at line 6411 — insert constants just before it
# ─────────────────────────────────────────────────────────────────────────────

# Find MaterialStore line
ms_line = -1
for i,l in enumerate(lines):
    if "const MaterialStore = ({" in l:
        ms_line = i
        break

if ms_line == -1:
    print("ERROR: MaterialStore not found")
    input(); exit(1)

print("MaterialStore at line " + str(ms_line+1))

# Check which constants already exist
existing = "".join(lines)
need_empty_stock   = "const EMPTY_STOCK_FORM"   not in existing or "= () =>" not in existing[existing.find("EMPTY_STOCK_FORM"):existing.find("EMPTY_STOCK_FORM")+30] if "EMPTY_STOCK_FORM" in existing else True
need_empty_item    = "const EMPTY_STOCK_ITEM"   not in existing
need_empty_iss     = "const EMPTY_ISS_FORM"     not in existing
need_stock_cats    = "const STOCK_CATS"         not in existing
need_units         = "const UNITS"              not in existing
need_stock_status  = "const STOCK_STATUS"       not in existing
need_st_badge      = "const ST_BADGE"           not in existing
need_dept_list     = "const DEPT_LIST"          not in existing

print("Need EMPTY_STOCK_FORM : " + str(need_empty_stock))
print("Need EMPTY_STOCK_ITEM : " + str(need_empty_item))
print("Need EMPTY_ISS_FORM   : " + str(need_empty_iss))
print("Need STOCK_CATS       : " + str(need_stock_cats))
print("Need UNITS            : " + str(need_units))
print("Need STOCK_STATUS     : " + str(need_stock_status))
print("Need ST_BADGE         : " + str(need_st_badge))
print("Need DEPT_LIST        : " + str(need_dept_list))

# Build the constants block
block = []
block.append("// ── Material Store Constants ──────────────────────────────────────────────────\n")

if need_dept_list:
    block.append('const DEPT_LIST = ["Civil","MEP","Architecture","QAQC","Store","Safety","Admin","Finishing","Steel","Concrete"];\n')

if need_units:
    block.append('const UNITS = ["Nos","m","m²","m³","kg","ton","bag","box","set","roll","ltr","gallon","sheet","length","lot","pair","pcs"];\n')

if need_stock_cats:
    block.append('const STOCK_CATS = ["Cement & Concrete","Steel & Rebar","Sand & Aggregate","Blocks & Masonry","Timber & Formwork","Pipes & Fittings","Electrical","Finishing Materials","Safety Equipment","Tools & Equipment","Chemicals","Others"];\n')

if need_stock_status:
    block.append('const STOCK_STATUS = ["Available","Low Stock","Out of Stock","Inactive"];\n')

if need_st_badge:
    block.append('const ST_BADGE = {"Available":"bg-green-100 text-green-700 border-green-200","Low Stock":"bg-amber-100 text-amber-700 border-amber-200","Out of Stock":"bg-red-100 text-red-700 border-red-200","Inactive":"bg-slate-100 text-slate-500 border-slate-200"};\n')

if need_empty_stock:
    block.append('const EMPTY_STOCK_FORM = () => ({code:"",name:"",category:"Cement & Concrete",unit:"Nos",pid:"",location:"",opening:"0",received:"0",issued:"0",minLevel:"0",supplier:"",rate:"",status:"Available",remarks:""});\n')

if need_empty_item:
    block.append('const EMPTY_STOCK_ITEM = () => ({id:Math.random().toString(36).substr(2,9),stockId:"",name:"",unit:"Nos",qty:0,remarks:""});\n')

if need_empty_iss:
    block.append('const EMPTY_ISS_FORM = () => ({pid:"",issuedTo:"",dept:"Civil",location:"",issueDate:"",issuedBy:"",purpose:"",remarks:"",items:[]});\n')

block.append("\n")

if len(block) > 2:  # more than just comment and newline
    lines = lines[:ms_line] + block + lines[ms_line:]
    changes += 1
    print("FIXED: Added " + str(len(block)) + " constant lines before MaterialStore")
    # Recalculate line numbers after insertion
    offset = len(block)
else:
    offset = 0
    print("SKIP: All constants already defined")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 2: Add Category/Scope to LPO form with "Others" + custom input
# LPO form is at line 5848 (before our insertion offset)
# The Grid2 block starts at line 5856
# We add Category field after Payment Terms (line 5868 + offset = new line)
# ─────────────────────────────────────────────────────────────────────────────

# Find the LPO payment terms custom input line (unique marker)
payment_custom_line = -1
for i,l in enumerate(lines):
    if "customPaymentTerms" in l and "Inp value" in l:
        payment_custom_line = i
        break

if payment_custom_line == -1:
    # Try finding the closing brace of payment terms div
    for i,l in enumerate(lines):
        if "paymentTerms" in l and "Custom..." in l:
            payment_custom_line = i
            break

print("Payment custom input at line " + str(payment_custom_line+1) if payment_custom_line!=-1 else "Payment custom not found")

if payment_custom_line != -1:
    # Find the closing </div> after customPaymentTerms
    close_div = -1
    for i in range(payment_custom_line, min(payment_custom_line+5, len(lines))):
        if "}" in lines[i] and ")" in lines[i] and ("</div>" in lines[i] or lines[i].strip().startswith("}")):
            close_div = i
            break
    if close_div == -1:
        # Try next few lines for </div>
        for i in range(payment_custom_line, min(payment_custom_line+8, len(lines))):
            if "</div>" in lines[i]:
                close_div = i
                break

    print("Close div at line " + str(close_div+1) if close_div!=-1 else "Close div not found")

    if close_div != -1:
        # Check if LPO_SCOPE already exists
        lpo_scope_exists = any("lpoScope" in l or "LPO_SCOPE" in l for l in lines)
        print("LPO Scope already exists: " + str(lpo_scope_exists))

        if not lpo_scope_exists:
            # Add LPO_SCOPE constant at beginning of file (near other LPO constants)
            # Find LPO_PAYMENT definition
            lpo_pay_line = -1
            for i,l in enumerate(lines):
                if "const LPO_PAYMENT" in l or "LPO_PAYMENT =" in l:
                    lpo_pay_line = i
                    break

            scope_const = 'const LPO_SCOPE = ["Civil Works","MEP","Architecture","Steel Works","Finishing","Procurement","IT & Technology","Subcontract","Others"];\n'

            if lpo_pay_line != -1:
                lines.insert(lpo_pay_line + 1, scope_const)
                close_div += 1  # adjust for insertion
                changes += 1
                print("ADDED: LPO_SCOPE constant at line " + str(lpo_pay_line+2))
            else:
                # Add before LPOModule
                for i,l in enumerate(lines):
                    if "const LPOModule = (" in l:
                        lines.insert(i, scope_const)
                        close_div += 1
                        changes += 1
                        print("ADDED: LPO_SCOPE constant before LPOModule")
                        break

            # Now add the Category field after the payment terms div
            # Insert after close_div
            lpo_cat_field = (
                '            <div>\n'
                '              <Lbl t="Scope / Category"/>\n'
                '              <Sel value={form.lpoScope||""} onChange={set("lpoScope")}>\n'
                '                <option value="">Select scope...</option>\n'
                '                {LPO_SCOPE.map(s=><option key={s}>{s}</option>)}\n'
                '              </Sel>\n'
                '              {form.lpoScope==="Others" && (\n'
                '                <Inp value={form.customScope||""} onChange={set("customScope")} placeholder="Specify scope..." className="mt-2 border-amber-300"/>\n'
                '              )}\n'
                '            </div>\n'
            )
            lines.insert(close_div + 1, lpo_cat_field)
            changes += 1
            print("ADDED: LPO Scope/Category field with Others after line " + str(close_div+1))
        else:
            # Others input might be missing
            scope_other_exists = any("lpoScope===\"Others\"" in l or 'lpoScope==="Others"' in l for l in lines)
            if not scope_other_exists:
                print("WARN: lpoScope exists but Others input missing")
            else:
                print("SKIP: LPO scope with Others already exists")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 3: Add lpoScope to EMPTY_LPO_FORM if it exists
# ─────────────────────────────────────────────────────────────────────────────
for i,l in enumerate(lines):
    if "EMPTY_LPO_FORM" in l and "= () =>" in l:
        if "lpoScope" not in l:
            # Add lpoScope to the form object
            if "remarks:\"\"}" in l:
                lines[i] = l.replace('remarks:""})', 'remarks:"",lpoScope:"",customScope:""})')
                changes += 1
                print("ADDED: lpoScope to EMPTY_LPO_FORM")
            elif "remarks:''}" in l:
                lines[i] = l.replace("remarks:''}", "remarks:'',lpoScope:'',customScope:''}")
                changes += 1
                print("ADDED: lpoScope to EMPTY_LPO_FORM")
        break

# Also add to handleSave for LPO
for i,l in enumerate(lines):
    if "scope_of_work" in l or "lpo_scope" in l:
        print("LPO scope already in save: " + l.strip()[:60])
        break

# ─────────────────────────────────────────────────────────────────────────────
# WRITE
# ─────────────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.writelines(lines)

print()
print("=" * 55)
print("Done - " + str(changes) + " changes applied")
print("Backup: " + bk)
print()
print("Run: set CI=false && npm run build")
print("     npx vercel --prod --force")
print("=" * 55)
input("Press Enter...")
