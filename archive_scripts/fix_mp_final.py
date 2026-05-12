import os, shutil
from datetime import datetime

APP = r"src\App.js"
MOD = "manpower_module.js"

bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Total lines: " + str(len(lines)))

# Find Module coming soon line
cs_line = -1
for i, line in enumerate(lines):
    if "Module coming soon" in line:
        cs_line = i
        print("Found at line " + str(i+1) + ": " + line.strip()[:80])
        break

if cs_line == -1:
    print("ERROR: Module coming soon not found")
    input(); exit(1)

# Check if case already nearby
has_case = any('manpower-master' in lines[j] for j in range(max(0,cs_line-15), cs_line+2))
print("Case already exists: " + str(has_case))

# Check ManpowerMaster component
has_comp = any("const ManpowerMaster" in l for l in lines)
print("ManpowerMaster in file: " + str(has_comp))

# Inject component if missing
if not has_comp:
    if not os.path.exists(MOD):
        print("ERROR: manpower_module.js missing from folder!")
        input(); exit(1)
    with open(MOD, "r", encoding="utf-8") as f:
        mod = f.read()
    # Find export default line
    exp = next((i for i,l in enumerate(lines) if "export default function App()" in l), -1)
    if exp == -1:
        print("ERROR: export default not found"); input(); exit(1)
    mod_lines = (mod + "\n\n").splitlines(keepends=True)
    lines = lines[:exp] + mod_lines + lines[exp:]
    print("Injected " + str(len(mod_lines)) + " lines before export default")
    # Recalculate cs_line
    cs_line = next((i for i,l in enumerate(lines) if "Module coming soon" in l), cs_line)
    print("Module coming soon now at line " + str(cs_line+1))

# Insert case
if not has_case:
    sp = "      "
    nc = sp + 'case "manpower-master": return <ManpowerMaster subcontractors={subs} projects={projects} showToast={showToast}/>;\n'
    lines.insert(cs_line, nc)
    print("INSERTED: " + nc.strip())

# Show context
print("\nLines around fix:")
for i in range(max(0,cs_line-1), min(len(lines),cs_line+4)):
    print(str(i+1) + ": " + lines[i].rstrip()[:100])

with open(APP, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("\nDone! Now run:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
input("Press Enter...")
