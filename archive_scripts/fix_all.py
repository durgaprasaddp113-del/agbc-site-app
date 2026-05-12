import os, shutil, re
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup: " + bk)

with open(APP, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split('\n')
changes = 0

# ─────────────────────────────────────────────────────────────────────────────
# FIX 1: Material Store — add ALL missing constants before MaterialStore
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- FIX 1: Material Store Constants ---")

CONSTANTS_BLOCK = '''// ── Material Store Constants ─────────────────────────────────────────────────
const DEPT_LIST = ["Civil","MEP","Architecture","QAQC","Store","Safety","Admin","Finishing","Steel","Concrete"];
const UNITS = ["Nos","m","m\u00b2","m\u00b3","kg","ton","bag","box","set","roll","ltr","gallon","sheet","length","lot","pair","pcs"];
const STOCK_CATS = ["Cement & Concrete","Steel & Rebar","Sand & Aggregate","Blocks & Masonry","Timber & Formwork","Pipes & Fittings","Electrical","Finishing Materials","Safety Equipment","Tools & Equipment","Chemicals","Others"];
const STOCK_STATUS = ["Available","Low Stock","Out of Stock","Inactive"];
const ST_BADGE = {"Available":"bg-green-100 text-green-700 border-green-200","Low Stock":"bg-amber-100 text-amber-700 border-amber-200","Out of Stock":"bg-red-100 text-red-700 border-red-200","Inactive":"bg-slate-100 text-slate-500 border-slate-200"};
const EMPTY_STOCK_FORM = () => ({code:"",name:"",category:"Cement & Concrete",unit:"Nos",pid:"",location:"",opening:"0",received:"0",issued:"0",minLevel:"0",supplier:"",rate:"",status:"Available",remarks:""});
const EMPTY_STOCK_ITEM = () => ({id:Math.random().toString(36).substr(2,9),stockId:"",name:"",unit:"Nos",qty:0,remarks:""});
const EMPTY_ISS_FORM = () => ({pid:"",issuedTo:"",dept:"Civil",location:"",issueDate:"",issuedBy:"",purpose:"",remarks:"",items:[]});

'''

# Check what's already defined
missing = []
for name in ["EMPTY_STOCK_FORM","EMPTY_STOCK_ITEM","EMPTY_ISS_FORM","STOCK_CATS","UNITS","STOCK_STATUS","ST_BADGE","DEPT_LIST"]:
    # Check if it's properly defined (not just called)
    pattern = r'const ' + name + r'\s*='
    if not re.search(pattern, content):
        missing.append(name)

print("Missing constants: " + str(missing))

if missing:
    # Find MaterialStore and insert before it
    ms_idx = content.find("const MaterialStore = ({")
    if ms_idx != -1:
        # Only add constants that are missing
        block_lines = ['// ── Material Store Constants ─────────────────────────────────────────────────\n']
        if "DEPT_LIST" in missing:
            block_lines.append('const DEPT_LIST = ["Civil","MEP","Architecture","QAQC","Store","Safety","Admin","Finishing","Steel","Concrete"];\n')
        if "UNITS" in missing:
            block_lines.append('const UNITS = ["Nos","m","m2","m3","kg","ton","bag","box","set","roll","ltr","gallon","sheet","length","lot","pair","pcs"];\n')
        if "STOCK_CATS" in missing:
            block_lines.append('const STOCK_CATS = ["Cement & Concrete","Steel & Rebar","Sand & Aggregate","Blocks & Masonry","Timber & Formwork","Pipes & Fittings","Electrical","Finishing Materials","Safety Equipment","Tools & Equipment","Chemicals","Others"];\n')
        if "STOCK_STATUS" in missing:
            block_lines.append('const STOCK_STATUS = ["Available","Low Stock","Out of Stock","Inactive"];\n')
        if "ST_BADGE" in missing:
            block_lines.append('const ST_BADGE = {"Available":"bg-green-100 text-green-700 border-green-200","Low Stock":"bg-amber-100 text-amber-700 border-amber-200","Out of Stock":"bg-red-100 text-red-700 border-red-200","Inactive":"bg-slate-100 text-slate-500 border-slate-200"};\n')
        if "EMPTY_STOCK_FORM" in missing:
            block_lines.append('const EMPTY_STOCK_FORM = () => ({code:"",name:"",category:"Cement & Concrete",unit:"Nos",pid:"",location:"",opening:"0",received:"0",issued:"0",minLevel:"0",supplier:"",rate:"",status:"Available",remarks:""});\n')
        if "EMPTY_STOCK_ITEM" in missing:
            block_lines.append('const EMPTY_STOCK_ITEM = () => ({id:Math.random().toString(36).substr(2,9),stockId:"",name:"",unit:"Nos",qty:0,remarks:""});\n')
        if "EMPTY_ISS_FORM" in missing:
            block_lines.append('const EMPTY_ISS_FORM = () => ({pid:"",issuedTo:"",dept:"Civil",location:"",issueDate:"",issuedBy:"",purpose:"",remarks:"",items:[]});\n')
        block_lines.append('\n')
        block_str = "".join(block_lines)
        content = content[:ms_idx] + block_str + content[ms_idx:]
        changes += 1
        print("FIXED: Added " + str(len(block_lines)-2) + " constants before MaterialStore")
    else:
        print("WARN: MaterialStore not found")
else:
    print("SKIP: All constants already defined")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 2: NOC Others — add custom input after nocType select
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- FIX 2: NOC Others Custom Input ---")

noc_start = content.find("const NOCModule = (")
if noc_start == -1:
    noc_start = content.find("const NOCModule=(")

if noc_start != -1:
    noc_body = content[noc_start:]

    # Check if Others custom input already exists
    if 'nocType==="Others"' in noc_body or "nocType===\"Others\"" in noc_body:
        print("SKIP: NOC Others custom input already exists")
    else:
        # Find the nocType Sel inside NOC form
        # Look for onChange={set("nocType")} pattern
        patterns = [
            'onChange={set("nocType")}',
            "onChange={set('nocType')}",
        ]
        for pat in patterns:
            idx = noc_body.find(pat)
            if idx != -1:
                # Find the closing </Sel> after this onChange
                sel_close = noc_body.find('</Sel>', idx)
                if sel_close != -1:
                    insert_pos = sel_close + len('</Sel>')
                    custom_input = (
                        '\n              {form.nocType==="Others" && (\n'
                        '                <Inp value={form.customNocType||""} '
                        'onChange={e=>setForm(p=>({...p,customNocType:e.target.value}))} '
                        'placeholder="Enter NOC/Permit type manually..." className="mt-2 border-amber-300"/>\n'
                        '              )}'
                    )
                    noc_body = noc_body[:insert_pos] + custom_input + noc_body[insert_pos:]
                    content = content[:noc_start] + noc_body
                    changes += 1
                    print("FIXED: Added custom input after nocType select")
                    break
                else:
                    print("WARN: </Sel> not found after nocType onChange")
                break
        else:
            print("WARN: nocType onChange pattern not found")
            # Show context for manual fix
            idx2 = noc_body.find("NOC_TYPES.map")
            if idx2 != -1:
                print("  NOC_TYPES.map found at NOC+" + str(idx2))
                print("  Context: " + noc_body[max(0,idx2-100):idx2+200])
else:
    print("WARN: NOCModule not found")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 3: NOC Others — also fix save to use customNocType
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- FIX 3: NOC save with customNocType ---")

noc_type_save_patterns = [
    # In insert/update calls
    ("noc_type: f.nocType,", 'noc_type: f.nocType==="Others" ? (f.customNocType||"Others") : f.nocType,'),
    ("noc_type: form.nocType,", 'noc_type: form.nocType==="Others" ? (form.customNocType||"Others") : form.nocType,'),
]
for old, new in noc_type_save_patterns:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        changes += 1
        print("FIXED: noc_type save uses customNocType (" + str(count) + " places)")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 4: NOC Others — populate customNocType when editing
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- FIX 4: NOC edit restores customNocType ---")

noc_start2 = content.find("const NOCModule = (")
if noc_start2 != -1:
    noc_body2 = content[noc_start2:]
    # Find setForm in openEdit or similar
    for pat in ['nocType:n.nocType,', 'nocType: n.nocType,']:
        if pat in noc_body2:
            new_pat = pat.replace(
                'nocType:n.nocType,',
                'nocType:NOC_TYPES.includes(n.nocType)?n.nocType:"Others",customNocType:NOC_TYPES.includes(n.nocType)?"":n.nocType,'
            ).replace(
                'nocType: n.nocType,',
                'nocType:NOC_TYPES.includes(n.nocType)?n.nocType:"Others",customNocType:NOC_TYPES.includes(n.nocType)?"":n.nocType,'
            )
            noc_body2 = noc_body2.replace(pat, new_pat, 1)
            content = content[:noc_start2] + noc_body2
            changes += 1
            print("FIXED: Edit restores customNocType")
            break
    else:
        print("SKIP: nocType edit pattern not found (may already be correct)")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 5: NOC table — add Description column header and cell
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- FIX 5: NOC Description Column ---")

noc_start3 = content.find("const NOCModule = (")
if noc_start3 != -1:
    noc_body3 = content[noc_start3:]

    # Fix table headers
    header_patterns = [
        ('["NOC No.","Authority","Type","Project","Status","Priority","Submitted","Expiry","Responsible","Actions"]',
         '["NOC No.","Authority","Type","Description","Project","Status","Submitted","Expiry","Responsible","Actions"]'),
        ('["NOC No.","Authority","Type","Project","Status","Submitted","Expiry","Responsible","Actions"]',
         '["NOC No.","Authority","Type","Description","Project","Status","Submitted","Expiry","Responsible","Actions"]'),
    ]
    header_fixed = False
    for old_h, new_h in header_patterns:
        if old_h in noc_body3:
            noc_body3 = noc_body3.replace(old_h, new_h, 1)
            content = content[:noc_start3] + noc_body3
            changes += 1
            header_fixed = True
            print("FIXED: Added Description to NOC table headers")
            break
    if not header_fixed:
        if "Description" in noc_body3[:noc_body3.find('</table>'[:50] if '</table>' in noc_body3 else len(noc_body3))]:
            print("SKIP: Description already in NOC headers")
        else:
            print("WARN: NOC table headers pattern not matched")

    # Fix table row — add description cell after Type cell
    # Find the nocType cell in the table row
    noc_body3 = content[noc_start3:]

    type_cell_patterns = [
        # Common pattern: truncate nocType cell followed by project cell
        ('className="truncate font-semibold">{n.nocType}</div>\n                    </td>\n                    <td className="px-4 py-3 text-xs font-bold text-slate-700">{proj?.number',
         'className="truncate font-semibold">{n.nocType}</div>\n                    </td>\n                    <td className="px-4 py-3 text-xs text-slate-600 max-w-[160px]"><div className="truncate">{n.desc||"—"}</div></td>\n                    <td className="px-4 py-3 text-xs font-bold text-slate-700">{proj?.number'),
    ]
    row_fixed = False
    for old_r, new_r in type_cell_patterns:
        if old_r in noc_body3:
            noc_body3 = noc_body3.replace(old_r, new_r, 1)
            content = content[:noc_start3] + noc_body3
            changes += 1
            row_fixed = True
            print("FIXED: Added Description cell to NOC table row")
            break

    if not row_fixed:
        # Try a simpler approach - find the project number cell in table row
        noc_body3 = content[noc_start3:]
        simple_pattern = '>{proj?.number||"—"}</td>'
        alt_pattern = ">{proj?.number||'—'}</td>"
        desc_cell = '<td className="px-4 py-3 text-xs text-slate-600 max-w-[180px]"><div className="truncate">{n.desc||"—"}</div></td>'

        if simple_pattern in noc_body3:
            # Only add if description cell not already before this
            idx = noc_body3.find(simple_pattern)
            before = noc_body3[max(0,idx-200):idx]
            if 'n.desc' not in before:
                noc_body3 = noc_body3[:idx] + desc_cell + noc_body3[idx:]
                content = content[:noc_start3] + noc_body3
                changes += 1
                row_fixed = True
                print("FIXED: Added Description cell (simple method)")
        elif alt_pattern in noc_body3:
            idx = noc_body3.find(alt_pattern)
            before = noc_body3[max(0,idx-200):idx]
            if 'n.desc' not in before:
                noc_body3 = noc_body3[:idx] + desc_cell + noc_body3[idx:]
                content = content[:noc_start3] + noc_body3
                changes += 1
                row_fixed = True
                print("FIXED: Added Description cell (alt simple method)")

        if not row_fixed:
            print("WARN: Could not add Description cell to row")

# ─────────────────────────────────────────────────────────────────────────────
# WRITE
# ─────────────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("DONE — " + str(changes) + " fixes applied")
print("Backup: " + bk)
print()
print("NEXT STEPS:")
print("  1. set CI=false && npm run build")
print("  2. npx vercel --prod --force")
print()
print("GITHUB (after successful deploy):")
print("  git add src/App.js")
print('  git commit -m "Fix: Material Store, NOC Others, NOC Description"')
print("  git push")
print("=" * 60)
input("Press Enter...")
