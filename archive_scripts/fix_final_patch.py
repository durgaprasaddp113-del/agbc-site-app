import shutil, re
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()
    lines = content.splitlines()

def s(x): return x.encode('ascii', errors='replace').decode('ascii')

changes = 0

# ── THE PROBLEM ───────────────────────────────────────────────────────
# FIX C/D previously changed ALL 4 navFilter useState/setFProject to use
# String(...).toLowerCase() || "all"
# BUT modules at L2744, L2893, L3165 (Tasks, Snag, DailyReports) use
# filter condition: fProject !== "All"  (capital A)
# So now fProject = "all" on load → "all" !== "All" = TRUE → 0 records shown
#
# FIX: Revert those 3 modules back to "All" default
#      Keep MR (L5735) with "all" default since its filter uses _fpid !== "all"
# ─────────────────────────────────────────────────────────────────────

# The pattern introduced by FIX C (useState)
WRONG_US  = 'useState(String(navFilter.projectId||"").toLowerCase() || "all")'
RIGHT_US  = 'useState(navFilter.projectId || "All")'

# The pattern introduced by FIX D (setFProject in useEffect)
WRONG_SF  = 'setFProject(String(navFilter.projectId||"").toLowerCase() || "all")'
RIGHT_SF  = 'setFProject(navFilter.projectId || "All")'

# MR module region: lines 5700–5800 (keep MR fix, revert others)
MR_START = 5700
MR_END   = 5800

new_lines = list(lines)

for i, l in enumerate(lines):
    lineno = i + 1   # 1-based

    # Revert useState — but NOT the MR one
    if WRONG_US in l:
        if MR_START <= lineno <= MR_END:
            print("KEEP  useState L"+str(lineno)+" (MR module) — stays lowercase")
        else:
            new_lines[i] = l.replace(WRONG_US, RIGHT_US, 1)
            changes += 1
            print("REVERT useState L"+str(lineno)+" → back to 'All'")

    # Revert setFProject in useEffect — but NOT the MR one
    if WRONG_SF in l:
        if MR_START <= lineno <= MR_END:
            print("KEEP  setFProject L"+str(lineno)+" (MR module) — stays lowercase")
        else:
            new_lines[i] = l.replace(WRONG_SF, RIGHT_SF, 1)
            changes += 1
            print("REVERT setFProject L"+str(lineno)+" → back to 'All'")

# ── Write ─────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write("\n".join(new_lines))

# ── VERIFY ────────────────────────────────────────────────────────────
print()
print("── VERIFY: All fProject useState after patch ──")
with open(APP, "r", encoding="utf-8", errors="replace") as f:
    vlines = f.readlines()

for i, l in enumerate(vlines):
    if 'fProject' in l and 'useState' in l:
        print("L"+str(i+1)+": "+s(l.rstrip()))

print()
print("── VERIFY: All filter conditions ──")
for i, l in enumerate(vlines):
    if 'fProject' in l and 'return false' in l:
        print("L"+str(i+1)+": "+s(l.rstrip()))

print()
print("── VERIFY: All 'All Projects' option values ──")
for i, l in enumerate(vlines):
    if 'All Projects' in l and 'option' in l:
        m = re.search(r'value="([^"]*)"', l)
        val = m.group(1) if m else "?"
        lc = 'toLowerCase' in "".join(vlines[max(0,i-3):i+3])
        print("L"+str(i+1)+" val='"+val+"' toLowerCase="+str(lc))

print()
print("── VERIFY: setFProject in useEffect ──")
for i, l in enumerate(vlines):
    if 'setFProject' in l and 'navFilter' in l:
        print("L"+str(i+1)+": "+s(l.rstrip()))

# ── FINAL SUMMARY ─────────────────────────────────────────────────────
print()
print("="*60)
print("EXPECTED STATE:")
print("  MR      (L5735): useState 'all' + filter _fpid !== 'all'  ✓")
print("  LPO     (L5991): useState 'All' + filter _fpid !== 'all'  ✓")
print("  NOC     (L11030):useState 'All' + filter _fpid !== 'all'  ✓")
print("  Others  (Tasks/Snag/DPR): useState 'All' + filter !== 'All' ✓")
print()
print("TOTAL REVERTS:", changes)
print()
print("NOW RUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js')
print('  git commit -m "Fix: project filter MR LPO NOC + revert side effects"')
print('  git push')
print("="*60)
input("Press Enter...")
