import os, shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Show LPO form to understand structure
print("=== LPO MODULE FORM SECTION ===")
lpo_start = 0
for i, l in enumerate(lines):
    if "const LPOModule = (" in l:
        lpo_start = i
        break

# Find the form mode section inside LPO
form_start = 0
for i in range(lpo_start, min(lpo_start+500, len(lines))):
    if 'mode === "form"' in lines[i] or 'mode==="form"' in lines[i]:
        form_start = i
        break

if form_start:
    print("LPO form at line " + str(form_start+1))
    for i in range(form_start, min(form_start+80, len(lines))):
        print(str(i+1) + ": " + lines[i].rstrip()[:120])
else:
    print("Form section not found, showing lines 5674-5750:")
    for i in range(lpo_start, min(lpo_start+80, len(lines))):
        print(str(i+1) + ": " + lines[i].rstrip()[:120])

input("\nPress Enter to apply fixes...")

changes = 0

# Find all <Sel> inside LPO that have category/type options WITHOUT Others
# Look for selects with onChange={set("...")} pattern
for i in range(lpo_start, min(lpo_start+2000, len(lines))):
    line = lines[i]
    # Find onChange patterns for common LPO fields
    for field in ['category', 'lpoType', 'scope', 'type', 'priority']:
        if ('set("' + field + '")') in line or ("set('" + field + "')") in line:
            print("Found field '" + field + "' at line " + str(i+1))
            # Find the opening <Sel
            sel_open = -1
            for j in range(max(lpo_start, i-10), i+1):
                if '<Sel' in lines[j]:
                    sel_open = j
            # Find closing </Sel>
            sel_close = -1
            for j in range(i, min(i+20, len(lines))):
                if '</Sel>' in lines[j]:
                    sel_close = j
                    break
            if sel_open != -1 and sel_close != -1:
                sel_block = "".join(lines[sel_open:sel_close+1])
                print("  Sel block (" + str(sel_close-sel_open+1) + " lines):")
                for j in range(sel_open, sel_close+1):
                    print("  " + str(j+1) + ": " + lines[j].rstrip()[:100])
                if 'Others' not in sel_block:
                    # Add Others before </Sel>
                    cap = field[0].upper() + field[1:]
                    indent = "                "
                    others_opt = indent + "<option>Others</option>\n"
                    lines.insert(sel_close, others_opt)
                    # After </Sel> add custom input
                    # sel_close shifted by 1 after insert
                    new_sel_close = sel_close + 1
                    custom = (indent + '{form.' + field + '==="Others" && (\n' +
                              indent + '  <Inp value={form.custom' + cap + '||""} ' +
                              'onChange={e=>setForm(p=>({...p,custom' + cap + ':e.target.value}))} ' +
                              'placeholder="Specify..." className="mt-2 border-amber-300"/>\n' +
                              indent + ')}\n')
                    lines.insert(new_sel_close + 1, custom)
                    changes += 1
                    print("  FIXED: Added Others + custom input for " + field)
                else:
                    # Others exists - check if custom input exists
                    cap = field[0].upper() + field[1:]
                    custom_key = 'custom' + cap
                    nearby = "".join(lines[sel_close:min(sel_close+5, len(lines))])
                    if custom_key not in nearby:
                        indent = "                "
                        custom = (indent + '{form.' + field + '==="Others" && (\n' +
                                  indent + '  <Inp value={form.' + custom_key + '||""} ' +
                                  'onChange={e=>setForm(p=>({...p,' + custom_key + ':e.target.value}))} ' +
                                  'placeholder="Specify..." className="mt-2 border-amber-300"/>\n' +
                                  indent + ')}\n')
                        lines.insert(sel_close + 1, custom)
                        changes += 1
                        print("  FIXED: Added custom input for " + field + " (Others existed)")
                    else:
                        print("  SKIP: Others + custom input already exist for " + field)
            break

# Also look for supplier select that might need Others
for i in range(lpo_start, min(lpo_start+2000, len(lines))):
    if 'supplierName' in lines[i] or 'supplier_name' in lines[i]:
        if 'set("supplier' in lines[i] or "set('supplier" in lines[i]:
            print("Found supplier field at line " + str(i+1) + ": " + lines[i].strip()[:80])
            break

with open(APP, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("\nDone - " + str(changes) + " changes")
print("\nNow run:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
input("Press Enter...")
