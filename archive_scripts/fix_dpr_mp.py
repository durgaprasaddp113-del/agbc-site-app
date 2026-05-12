import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()
    lines   = content.splitlines(keepends=True)

changes = 0
def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# ── FIX 1: Add subcontractors to DailyReports props destructuring ────
OLD_SIG = 'const DailyReports = ({ projects, reports, loading, onAdd, onUpdate, onDelete, showToast, navFilter = {} }) => {'
NEW_SIG = 'const DailyReports = ({ projects, reports, loading, onAdd, onUpdate, onDelete, showToast, navFilter = {}, subcontractors = [] }) => {'
if OLD_SIG in content:
    content = content.replace(OLD_SIG, NEW_SIG, 1)
    changes += 1
    print("FIX 1: subcontractors added to DailyReports props")
else:
    print("WARN 1: DailyReports signature not found — checking variant...")
    # Try to find and patch the line
    new_lines = []
    for l in content.split('\n'):
        if 'const DailyReports = ({' in l and 'subcontractors' not in l:
            l = l.replace('navFilter = {}', 'navFilter = {}, subcontractors = []')
            changes += 1
            print("FIX 1b: patched via variant")
        new_lines.append(l)
    content = '\n'.join(new_lines)

# ── FIX 2: Move DprAttendancePanel BELOW old manpower summary ────────
# Current order: DprAttendancePanel → old manpower summary
# Correct order: old manpower summary → DprAttendancePanel
# The old manpower summary is the existing one (trade/count/foreman)
# The DprAttendancePanel is the new one with master integration

# Find and reorder: remove DprAttendancePanel block from before manpower
# and place it after the manpower summary closing </div>}

# Strategy: find the MANPOWER section comment line,
# then extract DprAttendancePanel usage and move it after old summary

lines2 = content.split('\n')

# Find the manpower section block
mp_comment = -1
att_panel_start = -1
att_panel_end   = -1
old_mp_start    = -1
old_mp_end      = -1

for i, l in enumerate(lines2):
    if '{/* MANPOWER section */}' in l:
        mp_comment = i
    if '{/* DETAILED ATTENDANCE PANEL' in l:
        att_panel_start = i
    if att_panel_start != -1 and att_panel_end == -1:
        if '/>}' in l and 'DprAttendancePanel' not in l and i > att_panel_start:
            att_panel_end = i
    if att_panel_end != -1 and old_mp_start == -1:
        if 'activeSection==="manpower"&&<div' in l:
            old_mp_start = i

print(f"MANPOWER comment at L{mp_comment+1}")
print(f"AttPanel: L{att_panel_start+1} → L{att_panel_end+1}")
print(f"Old summary starts: L{old_mp_start+1}")

# Find where the old manpower summary div ends
if old_mp_start != -1:
    depth = 0
    for i in range(old_mp_start, min(old_mp_start+80, len(lines2))):
        depth += lines2[i].count('{') - lines2[i].count('}')
        if depth <= 0 and i > old_mp_start:
            old_mp_end = i
            break
    print(f"Old summary ends: L{old_mp_end+1}")

if att_panel_start != -1 and att_panel_end != -1 and old_mp_start != -1 and old_mp_end != -1:
    # Extract the DprAttendancePanel block (lines att_panel_start to att_panel_end)
    att_block = lines2[att_panel_start:att_panel_end+1]
    
    # Remove it from current position
    del lines2[att_panel_start:att_panel_end+1]
    
    # Recalculate old_mp_end after deletion
    shift = att_panel_end - att_panel_start + 1
    new_old_mp_end = old_mp_end - shift
    
    # Insert after old manpower summary
    for b in reversed(att_block):
        lines2.insert(new_old_mp_end + 1, b)
    
    changes += 1
    print(f"FIX 2: DprAttendancePanel moved after old manpower summary")
else:
    print("WARN 2: Could not reorder — check positions manually")
    print(f"  att_panel_start={att_panel_start} att_panel_end={att_panel_end}")
    print(f"  old_mp_start={old_mp_start} old_mp_end={old_mp_end}")

content = '\n'.join(lines2)

# ── FIX 3: App() — ensure subcontractors={subs} comes AFTER {...pp} ──
# Current: <DailyReports subcontractors={subs} {...pp} ...>
# Problem: {...pp} might not contain subcontractors and could override
# Fix: move subcontractors after {...pp}
OLD_CASE = 'return <DailyReports subcontractors={subs} {...pp}'
NEW_CASE = 'return <DailyReports {...pp} subcontractors={subs}'
if OLD_CASE in content:
    content = content.replace(OLD_CASE, NEW_CASE, 1)
    changes += 1
    print("FIX 3: subcontractors moved after {...pp} spread in App()")
else:
    if 'return <DailyReports {...pp} subcontractors={subs}' in content:
        print("INFO 3: Already in correct order")
    else:
        print("WARN 3: DailyReports case pattern not found")

# ── WRITE ─────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

# ── VERIFY ────────────────────────────────────────────────────────────
print()
with open(APP, "r", encoding="utf-8", errors="replace") as f:
    vlines = f.readlines()

print("── VERIFY: DailyReports props ──")
for i, l in enumerate(vlines):
    if "const DailyReports = ({" in l:
        print(f"L{i+1}: {s(l.rstrip())[:150]}")

print()
print("── VERIFY: Manpower section order ──")
for i, l in enumerate(vlines):
    if "MANPOWER section" in l or "DETAILED ATTENDANCE" in l or \
       "DprAttendancePanel" in l or ('activeSection==="manpower"' in l and "<div" in l):
        print(f"L{i+1}: {s(l.rstrip())[:120]}")

print()
print("── VERIFY: App() DailyReports case ──")
for i, l in enumerate(vlines):
    if 'case "reports"' in l:
        print(f"L{i+1}: {s(l.rstrip())[:160]}")

print()
print("="*55)
print("TOTAL FIXES:", changes)
print()
print("RUN NOW:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print("="*55)
input("Press Enter...")
