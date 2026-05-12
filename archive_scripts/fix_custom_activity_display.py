import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# ══════════════════════════════════════════════════════════
# FIX 1: Save display name correctly in add/update DB calls
# When activity = "Other (Custom)", save customActivity as activity_name
# Already done in previous fix — but double-check the logic:
# activity_name: f.unit==="Other (Custom)" ... <- wrong, should check f.activity
# ══════════════════════════════════════════════════════════

# Fix add function — was checking f.unit instead of f.activity
OLD_ADD = 'activity_name: f.unit==="Other (Custom)"&&f.customActivity ? f.customActivity : f.activity,'
NEW_ADD = 'activity_name: f.activity==="Other (Custom)"&&f.customActivity ? f.customActivity : f.activity,'
if OLD_ADD in content:
    content = content.replace(OLD_ADD, NEW_ADD)
    changes += 1
    print("FIX 1a: add — activity_name saves customActivity correctly ✅")
else:
    print("INFO: add pattern already correct or not found")

# Fix update function
OLD_UPD = 'activity_name: f.unit==="Other (Custom)"&&f.customActivity ? f.customActivity : f.activity,'
NEW_UPD = 'activity_name: f.activity==="Other (Custom)"&&f.customActivity ? f.customActivity : f.activity,'
if OLD_UPD in content:
    content = content.replace(OLD_UPD, NEW_UPD)
    changes += 1
    print("FIX 1b: update — activity_name saves customActivity correctly ✅")

# ══════════════════════════════════════════════════════════
# FIX 2: Display name helper — used in table rows + charts
# Add a helper: getActivityLabel(item) => customActivity || activity
# Insert this just before ProgressDashboard component
# ══════════════════════════════════════════════════════════
HELPER = '''// Helper: returns display name for an activity item
const getActivityLabel = (item) => {
  if (!item) return "";
  if (item.activity === "Other (Custom)" && item.customActivity) return item.customActivity;
  if (item.customActivity && item.activity === item.customActivity) return item.customActivity;
  return item.activity || item.customActivity || "";
};

'''
if 'const getActivityLabel' not in content:
    content = content.replace('const ProgressDashboard = (', HELPER + 'const ProgressDashboard = (', 1)
    changes += 1
    print("FIX 2: getActivityLabel helper added ✅")

# ══════════════════════════════════════════════════════════
# FIX 3: ProgressDashboard chartData — use getActivityLabel
# ══════════════════════════════════════════════════════════
OLD_CHART = '    const shortName = (i.activity||"").length > 11 ? (i.activity||"").slice(0,11)+"…" : (i.activity||"");\n    return { name: shortName, fullName: i.activity||"",'
NEW_CHART = '    const label = getActivityLabel(i);\n    const shortName = label.length > 11 ? label.slice(0,11)+"…" : label;\n    return { name: shortName, fullName: label,'
if OLD_CHART in content:
    content = content.replace(OLD_CHART, NEW_CHART, 1)
    changes += 1
    print("FIX 3: ProgressDashboard chart uses getActivityLabel ✅")
else:
    print("WARN FIX 3: chart label pattern not found")

# ══════════════════════════════════════════════════════════
# FIX 4: Summary table — fullName column uses getActivityLabel
# ══════════════════════════════════════════════════════════
OLD_TBL = '<td className="px-3 py-2 font-semibold text-slate-800">{r.fullName}</td>'
NEW_TBL = '<td className="px-3 py-2 font-semibold text-slate-800">{r.fullName}</td>'
# fullName is already set from getActivityLabel in chartData above — no change needed
print("INFO FIX 4: table fullName already uses getActivityLabel via chartData ✅")

# ══════════════════════════════════════════════════════════
# FIX 5: Progress activities TABLE rows — show custom name
# Find the activity column in the progress list table
# ══════════════════════════════════════════════════════════
OLD_ROW1 = '{pg.activity}'
NEW_ROW1 = '{getActivityLabel(pg)}'
# Be specific — only replace inside progress table td cells
OLD_TD = '<td className="px-3 py-2.5 text-slate-800 font-medium">{pg.activity}</td>'
NEW_TD = '<td className="px-3 py-2.5 text-slate-800 font-medium">{getActivityLabel(pg)}</td>'
if OLD_TD in content:
    content = content.replace(OLD_TD, NEW_TD, 1)
    changes += 1
    print("FIX 5a: Progress table row shows custom name ✅")
else:
    # Try alternate class names
    alts = [
        ('<td className="px-3 py-3 font-semibold text-slate-800">{pg.activity}</td>',
         '<td className="px-3 py-3 font-semibold text-slate-800">{getActivityLabel(pg)}</td>'),
        ('<td className="px-4 py-3 font-medium text-slate-800">{pg.activity}</td>',
         '<td className="px-4 py-3 font-medium text-slate-800">{getActivityLabel(pg)}</td>'),
    ]
    found_alt = False
    for o,n in alts:
        if o in content:
            content = content.replace(o, n, 1)
            changes += 1
            print(f"FIX 5b: alt pattern replaced ✅")
            found_alt = True
            break
    if not found_alt:
        # Find any td with {pg.activity}
        import re
        matches = [(m.start(), m.group()) for m in re.finditer(r'<td[^>]*>\{pg\.activity\}</td>', content)]
        print(f"FIX 5 fallback: found {len(matches)} td with {{pg.activity}}")
        for start, match in matches:
            new_match = match.replace('{pg.activity}', '{getActivityLabel(pg)}')
            content = content.replace(match, new_match, 1)
            changes += 1
            print(f"  Replaced: {match[:60]}")

# ══════════════════════════════════════════════════════════
# FIX 6: Progress VIEW panel — show custom name in header
# ══════════════════════════════════════════════════════════
OLD_VIEW_HDR = '{selPg.activity}'
# Find the specific view mode heading
OLD_VH = '<div className="font-bold text-slate-800">{selPg.activity}</div>'
NEW_VH = '<div className="font-bold text-slate-800">{getActivityLabel(selPg)}</div>'
if OLD_VH in content:
    content = content.replace(OLD_VH, NEW_VH, 1)
    changes += 1
    print("FIX 6: View panel header shows custom name ✅")
else:
    import re
    matches = list(re.finditer(r'\{selPg\.activity\}', content))
    print(f"INFO FIX 6: found {len(matches)} selPg.activity occurrences — replacing all with getActivityLabel")
    content = re.sub(r'\{selPg\.activity\}', '{getActivityLabel(selPg)}', content)
    changes += 1

# ══════════════════════════════════════════════════════════
# FIX 7: Edit form — pre-fill customActivity from DB correctly
# When loading an item that has customActivity, set activity dropdown to "Other (Custom)"
# ══════════════════════════════════════════════════════════
OLD_EDIT = "setSelPg(pg); setPgForm({pid:pg.pid,activity:pg.activity,customActivity:pg.customActivity||''"
NEW_EDIT = "setSelPg(pg); const _isCustom=pg.activity&&!['Mobilization','Excavation','Shoring / Piling','Concrete Works','Steel Reinforcement','Block Work / Masonry','Waterproofing','Plaster Work','Electrical Work','Plumbing Work','HVAC Work','Fire Fighting','Tiles','False Ceiling','Painting','Joinery / Carpentry','Doors & Windows','Aluminum & Glazing','External Works','Landscaping','Lift Installation','Testing & Commissioning','Other (Custom)'].includes(pg.activity); setPgForm({pid:pg.pid,activity:_isCustom?'Other (Custom)':pg.activity,customActivity:_isCustom?pg.activity:(pg.customActivity||'')"
if OLD_EDIT in content:
    content = content.replace(OLD_EDIT, NEW_EDIT, 1)
    changes += 1
    print("FIX 7: Edit form pre-fills custom activity correctly ✅")
else:
    print("WARN FIX 7: edit form pattern not found")

# ══════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════
with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved. Total changes: {changes}")
print("\nRUN:")
print("  set CI=false && npm run build")
print("  git add src/App.js && git commit -m 'fix: show custom activity name instead of Other (Custom)' && git push")
input("\nPress Enter...")
