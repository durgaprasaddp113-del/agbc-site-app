#!/usr/bin/env python3
"""
Manpower Master System — Patch Script
Injects manpower master hook, component, and nav item into App.js
Run from: C:\Apps\agbc-site-app\
Command:  python patch_manpower.py
"""
import os, shutil
from datetime import datetime

APP       = r"src\App.js"
MOD_FILE  = "manpower_module.js"

if not os.path.exists(APP):
    print("ERROR: src\\App.js not found"); input(); exit(1)
if not os.path.exists(MOD_FILE):
    print(f"ERROR: {MOD_FILE} not found — put it in same folder"); input(); exit(1)

bk = APP + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(APP, bk)
print(f"Backup: {bk}")

with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

with open(MOD_FILE, "r", encoding="utf-8") as f:
    module = f.read()

changes = 0

# ── Safety check: don't double-patch ─────────────────────────────────────────
if "useManpowerMaster" in app:
    print("⚠️  Manpower master already in App.js — skipping injection")
    print("   Running nav + case fixes only...")
else:
    # ── Inject module BEFORE DailyReports component ───────────────────────────
    anchor = "const DailyReports = ("
    if anchor not in app:
        anchor = "const DailyReportModule = ("
    if anchor not in app:
        anchor = "function DailyReports("

    if anchor in app:
        idx = app.find(anchor)
        app = app[:idx] + module + "\n\n" + app[idx:]
        changes += 1
        print("✅ Injected manpower module before DailyReports")
    else:
        # Fallback: inject before export default
        anchor2 = "export default function App()"
        if anchor2 in app:
            idx = app.find(anchor2)
            app = app[:idx] + module + "\n\n" + app[idx:]
            changes += 1
            print("✅ Injected manpower module before App export")
        else:
            print("⚠️  Could not find injection point")

# ── Add Manpower Master to sidebar nav ───────────────────────────────────────
nav_anchors = [
    # Common pattern: DPR nav item
    ('{ id: "reports", label: "Daily Reports"',
     '{ id: "manpower-master", label: "Manpower Master", icon: "👷", section: "DPR" },\n    { id: "reports", label: "Daily Reports"'),
    ('{ id:"reports", label:"Daily Reports"',
     '{ id:"manpower-master", label:"Manpower Master", icon:"👷" },\n    { id:"reports", label:"Daily Reports"'),
    # After NOC in nav
    ('{ id: "noc", label: "NOC & Permits"',
     '{ id: "noc", label: "NOC & Permits"'),
]

mp_nav_added = False
for old, new in nav_anchors:
    if old in app and "manpower-master" not in app:
        app = app.replace(old, new, 1)
        mp_nav_added = True
        changes += 1
        print("✅ Added Manpower Master to nav")
        break

if not mp_nav_added:
    print("⚠️  Nav item not added — add manually or check nav structure")

# ── Add sidebar menu item ─────────────────────────────────────────────────────
# Look for Material Store in sidebar and add Manpower Master after it
sidebar_anchors = [
    ('Material Store', 'Manpower Master'),
]
for label, new_label in sidebar_anchors:
    # Find the sidebar button for Material Store
    store_btn_idx = app.find(f'"store"')
    if store_btn_idx != -1:
        # Find the next nav button block after store
        after = app[store_btn_idx:store_btn_idx+500]
        # Look for the closing of that nav item
        close_idx = after.find('</button>')
        if close_idx != -1:
            abs_close = store_btn_idx + close_idx + len('</button>')
            after_close = app[abs_close:abs_close+50]
            # Check if manpower-master already there
            if "manpower-master" not in app[store_btn_idx:store_btn_idx+600]:
                print("⚠️  Sidebar manual add needed — see instructions below")

# ── Add case "manpower-master" to renderPage ─────────────────────────────────
case_anchors = [
    # After store case
    'case "store":',
    # After noc case
    'case "noc":',
    # After reports case
    'case "reports":',
]

case_added = False
for anchor_case in case_anchors:
    if anchor_case in app and "manpower-master" not in app:
        # Find the line with this case and add manpower-master case before it
        idx = app.find(anchor_case)
        new_case = '''case "manpower-master": return <ManpowerMaster subcontractors={subcontractors} projects={projects} showToast={showToast}/>;
      '''
        app = app[:idx] + new_case + app[idx:]
        case_added = True
        changes += 1
        print(f"✅ Added case 'manpower-master' before {anchor_case}")
        break

if not case_added and "manpower-master" not in app:
    print("⚠️  Could not add case — add manually (see instructions)")

# ── Add "Manpower Master" to sidebar JSX ─────────────────────────────────────
# Find the NavBtn or sidebar button for "Material Store" and add after it
sidebar_patterns = [
    # Pattern: onClick={()=>setPage("store")} variations
    ('onClick={()=>setPage("store")}',),
    ("onClick={()=>setPage('store')}",),
]

sidebar_added = False
for (pat,) in sidebar_patterns:
    if pat in app:
        # Find the end of this button
        btn_start = app.find(pat)
        btn_end_search = app[btn_start:btn_start+300]
        btn_close = btn_end_search.find('</button>')
        if btn_close == -1:
            btn_close = btn_end_search.find('/>')
        if btn_close != -1:
            abs_end = btn_start + btn_close + len('</button>' if '</button>' in btn_end_search[:btn_close+10] else '/>')
            mp_btn = '''
          <button onClick={()=>setPage("manpower-master")}
            className={`w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-2.5 ${page==="manpower-master"?"bg-amber-500 text-white":"text-slate-300 hover:bg-slate-700 hover:text-white"}`}>
            👷 Manpower Master
          </button>'''
            if "manpower-master" not in app:
                app = app[:abs_end] + mp_btn + app[abs_end:]
                sidebar_added = True
                changes += 1
                print("✅ Added Manpower Master sidebar button")
                break

if not sidebar_added:
    print("⚠️  Sidebar button not added automatically — see manual steps below")

# ── Write ─────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 60)
print(f"✅ Done! {changes} changes applied to App.js")
print(f"   Backup: {bk}")
print()
print("NEXT STEPS:")
print("  1. set CI=false && npm run build")
print("  2. If OK: npx vercel --prod")
print()
print("IF SIDEBAR BUTTON NOT AUTO-ADDED:")
print("  Find in App.js: onClick={()=>setPage(\"store\")}")
print("  After that button's closing </button>, add:")
print("""
  <button onClick={()=>setPage("manpower-master")}
    className={`w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium
      transition-colors flex items-center gap-2.5
      ${page==="manpower-master"
        ?"bg-amber-500 text-white"
        :"text-slate-300 hover:bg-slate-700 hover:text-white"}`}>
    \U0001f477 Manpower Master
  </button>
""")
print("=" * 60)
input("Press Enter to exit...")
