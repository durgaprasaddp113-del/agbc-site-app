import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

changes = 0

# ─────────────────────────────────────────────────────────────────────
# ROOT CAUSE:
#   onChange converts "All" → "all" (lowercase)
#   but filter checks fProject !== "All" (capital A)
#   So "all" !== "All" = TRUE → tries to filter by project "all" → 0 records
#
# FIX: Replace the fProject !== "All" check with _fpid !== "all"
#   since _fpid is already .toLowerCase(), this handles both "All" and "all"
# ─────────────────────────────────────────────────────────────────────

OLD_COND = 'if (fProject !== "All" && _fpid && _pid !== _fpid) return false;'
NEW_COND = 'if (_fpid && _fpid !== "all" && _pid !== _fpid) return false;'

count = content.count(OLD_COND)
print("Occurrences of filter condition found:", count, "(expected 3 for MR, LPO, NOC)")

if count > 0:
    content = content.replace(OLD_COND, NEW_COND)
    changes += count
    print("FIX 1: Replaced", count, "filter condition(s) — fProject !== 'All' → _fpid !== 'all'")
else:
    print("WARN 1: Condition not found - checking for already-fixed version...")
    if NEW_COND in content:
        print("  Already fixed!")
    else:
        print("  Neither old nor new found - manual check needed")

# ─────────────────────────────────────────────────────────────────────
# FIX 2: useMatReqs — store pid as lowercase (safety)
# Line 5490: pid: r.project_id || "",
# ─────────────────────────────────────────────────────────────────────
OLD_PID = 'pid: r.project_id || "",'
NEW_PID = 'pid: String(r.project_id||"").toLowerCase(),'

if OLD_PID in content:
    content = content.replace(OLD_PID, NEW_PID, 1)
    changes += 1
    print("FIX 2: useMatReqs pid now stored as lowercase")
else:
    print("SKIP 2: useMatReqs pid already fixed or pattern differs")

# ─────────────────────────────────────────────────────────────────────
# FIX 3: Initial state — ensure "All" default is consistent
# The initial useState("All") is fine since the filter now handles both
# But navFilter.projectId should be lowercased if passed
# ─────────────────────────────────────────────────────────────────────
# MR uses: useState(navFilter.projectId || "All")
# On init, if navFilter.projectId is undefined → "All" → _fpid="all" → no filter ✓
# If navFilter.projectId is a UUID → stored as-is → _fpid=lowercase UUID → filter ✓
# No change needed here.
print("INFO 3: Initial fProject states are compatible with fix — no change needed")

# ─────────────────────────────────────────────────────────────────────
# WRITE
# ─────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

print()
print("=" * 60)
print("TOTAL FIXES APPLIED:", changes)
print("Backup saved:", bk)
print()
print("NEXT STEPS:")
print("  1. set CI=false && npm run build")
print("  2. npx vercel --prod --force")
print("  3. git add src/App.js")
print('  4. git commit -m "Fix: project filter All/all case bug MR LPO NOC"')
print("  5. git push")
print("=" * 60)
input("Press Enter...")
