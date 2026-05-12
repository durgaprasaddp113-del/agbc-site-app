import shutil, re
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

content = "".join(lines)
total = len(lines)

def s(x): return x.encode('ascii', errors='replace').decode('ascii')

# ── STEP 1: Find all modules and their fProject/filter state ──────────
print("\n── ALL fProject dropdowns and their onChange ──")
for i, l in enumerate(lines):
    if 'setFProject' in l and ('onChange' in l or 'Sel' in l):
        has_lower = 'toLowerCase' in l
        print("L"+str(i+1)+" [toLowerCase="+str(has_lower)+"]: "+s(l.rstrip())[:140])

print("\n── ALL fProject filter conditions ──")
for i, l in enumerate(lines):
    if 'fProject' in l and ('return false' in l or '!== "All"' in l or "!== 'All'" in l or '!== "all"' in l):
        print("L"+str(i+1)+": "+s(l.rstrip()))

print("\n── ALL 'All Projects' option values ──")
for i, l in enumerate(lines):
    if 'All Projects' in l and 'option' in l:
        # Extract just the value attribute
        m = re.search(r'value="([^"]*)"', l)
        val = m.group(1) if m else "?"
        print("L"+str(i+1)+" value='"+val+"'  ["+s(l.rstrip())[:80]+"]")

print("\n── ALL useState fProject ──")
for i, l in enumerate(lines):
    if 'fProject' in l and 'useState' in l:
        print("L"+str(i+1)+": "+s(l.rstrip()))

# ── STEP 2: Identify which modules are broken ─────────────────────────
print("\n\n── ANALYSIS ──")
# Modules that use toLowerCase in onChange → OK with "all"
# Modules that DON'T use toLowerCase → need "All" option value AND "All" condition

# Find all option lines with All Projects
changes = 0
new_lines = list(lines)

for i, l in enumerate(lines):
    if 'All Projects' in l and 'option' in l and 'value="all"' in l:
        # Check if this module's onChange uses toLowerCase
        # Scan backwards up to 5 lines for the Sel element
        context = "".join(lines[max(0,i-3):i+3])
        if 'toLowerCase' not in context:
            # This module doesn't use toLowerCase → revert option to "All"
            new_lines[i] = l.replace('value="all"', 'value="All"', 1)
            changes += 1
            print("REVERT L"+str(i+1)+": option value back to 'All' (module uses no toLowerCase)")
        else:
            print("KEEP   L"+str(i+1)+": option value stays 'all' (module uses toLowerCase) OK")

# ── STEP 3: Fix modules that use value="All" but have no toLowerCase ──
# Those modules: filter condition might be fProject !== "All"
# We need to ensure those conditions still work
# Since we reverted option to "All" above, their fProject will be "All" when user
# selects "All Projects" — the condition fProject !== "All" will be FALSE — correct

# ── STEP 4: For MR/LPO/NOC that keep value="all" ─────────────────────
# Their onChange uses toLowerCase, so "all" stays "all"
# Their filter uses _fpid !== "all" ← already correct
# Their useState for "All" initial state: _fpid = "all" → condition FALSE → OK

# ── STEP 5: Fix remaining modules that have value="All" option
#   but fProject starts as "All" and no toLowerCase ──────────────────
# These are already fine as long as the filter uses fProject !== "All"
# Let's verify those conditions exist and are correct
print()
for i, l in enumerate(lines):
    if 'fProject' in l and '!== "All"' in l and 'return false' in l:
        # These are the non-MR/LPO/NOC modules
        # Check if we reverted option value near their dropdown
        print("OK - Other module filter at L"+str(i+1)+": "+s(l.rstrip()))

# ── STEP 6: Write ────────────────────────────────────────────────────
if changes > 0:
    content2 = "".join(new_lines)
    with open(APP, "w", encoding="utf-8") as f:
        f.write(content2)
    print("\nWrote", changes, "reverts to file")
else:
    print("\nNo reverts needed")

# ── STEP 7: Final verify ─────────────────────────────────────────────
print("\n── FINAL: All Projects option values ──")
with open(APP, "r", encoding="utf-8", errors="replace") as f:
    vlines = f.readlines()
for i, l in enumerate(vlines):
    if 'All Projects' in l and 'option' in l:
        m2 = re.search(r'value="([^"]*)"', l)
        val2 = m2.group(1) if m2 else "?"
        lc = 'toLowerCase' in "".join(vlines[max(0,i-3):i+3])
        print("L"+str(i+1)+" val='"+val2+"' [toLowerCase="+str(lc)+"] "+s(l.rstrip())[:70])

print("\n── FINAL: Filter conditions ──")
for i, l in enumerate(vlines):
    if 'fProject' in l and 'return false' in l:
        print("L"+str(i+1)+": "+s(l.rstrip()))

print()
print("="*55)
print("Total reverts:", changes)
print()
print("NOW RUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js')
print('  git commit -m "Fix: project filter MR LPO NOC"')
print('  git push')
print("="*55)
input("Press Enter...")
