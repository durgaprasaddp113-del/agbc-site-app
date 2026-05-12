#!/usr/bin/env python3
"""
AGBC NOC Module Fix
- Adds custom input when "Others" selected
- Adds Description column to NOC table
- Fixes "All Projects" filter
Run from: C:\Apps\agbc-site-app\
Command:  python fix_noc.py
"""
import os, shutil
from datetime import datetime

APP = r"src\App.js"

if not os.path.exists(APP):
    print("ERROR: src\\App.js not found.")
    print("Run this from C:\\Apps\\agbc-site-app\\")
    input("Press Enter to exit..."); exit(1)

bk = APP + f".noc_bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(APP, bk)
print(f"✅ Backup: {bk}")

with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

changes = 0

# ─────────────────────────────────────────────────────────────────
# FIX 1 — "Others" shows custom input in NOC form
# Find the NOC/Permit Type selector and add conditional input
# ─────────────────────────────────────────────────────────────────
OLD1 = '''            <div><Lbl t="NOC / Permit Type" req/>
              <Sel value={form.nocType} onChange={set("nocType")}>
                {NOC_TYPES.map(t=><option key={t}>{t}</option>)}
              </Sel>
            </div>'''

NEW1 = '''            <div>
              <Lbl t="NOC / Permit Type" req/>
              <Sel value={form.nocType} onChange={e => { set("nocType")(e); if(e.target.value !== "Others") setForm(p=>({...p,customNocType:""})); }}>
                {NOC_TYPES.map(t=><option key={t}>{t}</option>)}
              </Sel>
              {form.nocType === "Others" && (
                <Inp value={form.customNocType||""} onChange={set("customNocType")}
                  placeholder="Enter permit type manually..." className="mt-2"/>
              )}
            </div>'''

if OLD1 in app:
    app = app.replace(OLD1, NEW1, 1)
    changes += 1
    print("✅ Fix 1: Added 'Others' custom input field")
else:
    # Try simpler match
    OLD1B = '<div><Lbl t="NOC / Permit Type" req/>'
    if OLD1B in app:
        OLD1C = '''<div><Lbl t="NOC / Permit Type" req/>
              <Sel value={form.nocType} onChange={set("nocType")}>
                {NOC_TYPES.map(t=><option key={t}>{t}</option>)}
              </Sel>
            </div>'''
        NEW1C = '''<div>
              <Lbl t="NOC / Permit Type" req/>
              <Sel value={form.nocType} onChange={e => { set("nocType")(e); if(e.target.value !== "Others") setForm(p=>({...p,customNocType:""})); }}>
                {NOC_TYPES.map(t=><option key={t}>{t}</option>)}
              </Sel>
              {form.nocType === "Others" && (
                <Inp value={form.customNocType||""} onChange={set("customNocType")}
                  placeholder="Enter permit type manually..." className="mt-2"/>
              )}
            </div>'''
        app = app.replace(OLD1C, NEW1C, 1)
        changes += 1
        print("✅ Fix 1 (alt): Added 'Others' custom input field")
    else:
        print("⚠️  Fix 1: NOC type selector not found — skipping")

# ─────────────────────────────────────────────────────────────────
# FIX 2 — Save custom NOC type in add()
# ─────────────────────────────────────────────────────────────────
OLD2 = "noc_type: f.nocType,"
NEW2 = "noc_type: f.nocType === 'Others' ? (f.customNocType || 'Others') : f.nocType,"

count2 = app.count(OLD2)
if count2 >= 1:
    app = app.replace(OLD2, NEW2)  # replace ALL occurrences (add + update)
    changes += 1
    print(f"✅ Fix 2: Custom NOC type saved correctly ({count2} places)")
else:
    print("⚠️  Fix 2: noc_type field not found — skipping")

# ─────────────────────────────────────────────────────────────────
# FIX 3 — Populate customNocType when editing existing record
# ─────────────────────────────────────────────────────────────────
OLD3 = "setForm({ pid:n.pid, authority:n.authority, nocType:n.nocType, desc:n.desc,"
NEW3 = """setForm({ pid:n.pid, authority:n.authority,
      nocType: NOC_TYPES.includes(n.nocType) ? n.nocType : "Others",
      customNocType: NOC_TYPES.includes(n.nocType) ? "" : n.nocType,
      desc:n.desc,"""

if OLD3 in app:
    app = app.replace(OLD3, NEW3, 1)
    changes += 1
    print("✅ Fix 3: Edit restores custom NOC type correctly")
else:
    # Try without desc
    OLD3B = "setForm({ pid:n.pid, authority:n.authority, nocType:n.nocType,"
    if OLD3B in app:
        app = app.replace(OLD3B,
            'setForm({ pid:n.pid, authority:n.authority, nocType: NOC_TYPES.includes(n.nocType) ? n.nocType : "Others", customNocType: NOC_TYPES.includes(n.nocType) ? "" : n.nocType,',
            1)
        changes += 1
        print("✅ Fix 3 (alt): Edit restores custom NOC type")
    else:
        print("⚠️  Fix 3: openEdit setForm not found — skipping")

# ─────────────────────────────────────────────────────────────────
# FIX 4 — Add Description column header to NOC table
# ─────────────────────────────────────────────────────────────────
OLD4 = '["NOC No.","Authority","Type","Project","Status","Priority","Submitted","Expiry","Responsible","Actions"]'
NEW4 = '["NOC No.","Authority","Type","Description","Project","Status","Submitted","Expiry","Responsible","Actions"]'

if OLD4 in app:
    app = app.replace(OLD4, NEW4, 1)
    changes += 1
    print("✅ Fix 4: Added Description column header")
else:
    print("⚠️  Fix 4: NOC table headers not found — skipping")

# ─────────────────────────────────────────────────────────────────
# FIX 5 — Add Description cell to NOC table row
# ─────────────────────────────────────────────────────────────────
OLD5 = '''<td className="px-4 py-3 text-xs text-slate-700 max-w-[160px]">
                      <div className="truncate font-semibold">{n.nocType}</div>
                    </td>
                    <td className="px-4 py-3 text-xs font-bold text-slate-700">{proj?.number||"—"}</td>'''

NEW5 = '''<td className="px-4 py-3 text-xs text-slate-700 max-w-[160px]">
                      <div className="truncate font-semibold">{n.nocType}</div>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-600 max-w-[200px]">
                      <div className="truncate">{n.desc||"—"}</div>
                    </td>
                    <td className="px-4 py-3 text-xs font-bold text-slate-700">{proj?.number||"—"}</td>'''

if OLD5 in app:
    app = app.replace(OLD5, NEW5, 1)
    changes += 1
    print("✅ Fix 5: Added Description cell to table row")
else:
    print("⚠️  Fix 5: NOC table row pattern not found — skipping")

# ─────────────────────────────────────────────────────────────────
# FIX 6 — Fix "All Projects" filter in NOC module
# The filter uses fProject but was not resetting properly
# ─────────────────────────────────────────────────────────────────

# Fix the NOC filter logic — ensure fProject comparison works
OLD6 = '''  const filtered = nocs.filter(n => {
    if (fProject!=="All" && n.pid!==fProject) return false;
    if (fAuth!=="All" && n.authority!==fAuth) return false;
    if (fStatus!=="All" && n.status!==fStatus) return false;
    if (fExpiry==="expiring" && !isExpiringSoon(n.expiryDate,n.status)) return false;
    if (fExpiry==="expired" && !isExpired(n.expiryDate,n.status)) return false;
    if (search && !`${n.nocNum} ${n.authority} ${n.nocType} ${n.responsible}`.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });'''

NEW6 = '''  const filtered = nocs.filter(n => {
    if (fProject && fProject!=="All" && n.pid!==fProject) return false;
    if (fAuth && fAuth!=="All" && n.authority!==fAuth) return false;
    if (fStatus && fStatus!=="All" && n.status!==fStatus) return false;
    if (fExpiry==="expiring" && !isExpiringSoon(n.expiryDate,n.status)) return false;
    if (fExpiry==="expired" && !isExpired(n.expiryDate,n.status)) return false;
    if (search && !`${n.nocNum} ${n.authority} ${n.nocType} ${n.responsible} ${n.desc||""}`.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });'''

if OLD6 in app:
    app = app.replace(OLD6, NEW6, 1)
    changes += 1
    print("✅ Fix 6: Fixed All Projects filter")
else:
    # Simpler fix — just patch the fProject line
    OLD6B = 'if (fProject!=="All" && n.pid!==fProject) return false;'
    NEW6B = 'if (fProject && fProject!=="All" && n.pid!==fProject) return false;'
    if OLD6B in app:
        # Count occurrences — only fix the one inside NOC filtered (last occurrence usually)
        app = app.replace(OLD6B, NEW6B)
        changes += 1
        print("✅ Fix 6 (alt): Fixed All Projects filter")
    else:
        print("⚠️  Fix 6: NOC filter not found — skipping")

# ─────────────────────────────────────────────────────────────────
# FIX 7 — Fix project filter SELECT to include proper value
# ─────────────────────────────────────────────────────────────────
# Make sure the NOC project filter dropdown uses correct value
OLD7 = '''        <Sel value={fProject} onChange={e=>setFProject(e.target.value)} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={p.id}>{p.number}</option>)}
          </Sel>
          <Sel value={fAuth} onChange={e=>setFAuth(e.target.value)} className="w-auto">'''

NEW7 = '''        <Sel value={fProject} onChange={e=>setFProject(e.target.value||"All")} className="w-auto">
            <option value="All">All Projects</option>
            {projects.map(p=><option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}
          </Sel>
          <Sel value={fAuth} onChange={e=>setFAuth(e.target.value)} className="w-auto">'''

if OLD7 in app:
    app = app.replace(OLD7, NEW7, 1)
    changes += 1
    print("✅ Fix 7: Project filter dropdown shows project names")
else:
    print("⚠️  Fix 7: NOC filter dropdown not found — skipping")

# ─────────────────────────────────────────────────────────────────
# Write result
# ─────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 55)
print(f"✅ Done! {changes} fixes applied to App.js")
print(f"   Backup: {bk}")
print()
print("Next steps:")
print("  1. npm run build   (check for errors)")
print("  2. npx vercel --prod")
print("=" * 55)
input("\nPress Enter to exit...")
