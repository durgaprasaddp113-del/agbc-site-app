import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# Remove OLD useManpowerMaster at L11514 (0-based: 11513)
# and OLD ManpowerMaster at L11593 (0-based: 11592)
# Find the OLD hook start and remove until the OLD component ends

old_hook_start = 11513  # 0-based (L11514)

# Find end of OLD ManpowerMaster component (by counting braces from L11593)
old_comp_start = 11592  # 0-based (L11593)
depth = 0
old_comp_end = old_comp_start
for i in range(old_comp_start, min(old_comp_start+500, len(lines))):
    depth += lines[i].count('{') - lines[i].count('}')
    if depth <= 0 and i > old_comp_start + 5:
        old_comp_end = i
        break

print(f"Removing OLD hook: L{old_hook_start+1} to OLD component end: L{old_comp_end+1}")
print("Sample lines being removed:")
for j in [old_hook_start, old_hook_start+1, old_comp_start, old_comp_end]:
    print(f"  L{j+1}: {s(lines[j].rstrip())[:80]}")

# Remove from old_hook_start to old_comp_end (inclusive)
del lines[old_hook_start:old_comp_end+1]
print(f"Removed {old_comp_end - old_hook_start + 1} lines")

with open(APP,"w",encoding="utf-8") as f:
    f.writelines(lines)

print("Saved. Lines now:", len(lines))
print("\nRUN: set CI=false && npm run build")
input("Press Enter...")
