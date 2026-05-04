#!/usr/bin/env python3
"""
Minimal NOC filter fix on clean file.
ONLY changes filter comparisons - no JSX, no state changes.
Run from: C:\Apps\agbc-site-app\
Command:  python fix_noc_clean.py
"""
import os, shutil, re
from datetime import datetime

APP = r"src\App.js"
if not os.path.exists(APP):
    print("ERROR: src\\App.js not found"); input(); exit(1)

with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

# Safety check - must be clean file
if "projRef" in app or "refilter" in app:
    print("ERROR: File has old patches. Restore clean backup first:")
    print("  copy src\\App.js.bak_20260502_104255 src\\App.js")
    input(); exit(1)

bk = APP + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(APP, bk)
print(f"Backup: {bk}")

# Find NOCModule
noc_start = app.find("const NOCModule = (")
if noc_start == -1: noc_start = app.find("const NOCModule=(")
if noc_start == -1: print("ERROR: NOCModule not found"); input(); exit(1)

noc_body = app[noc_start:]
changes = 0

# ── DIAGNOSTIC first ──────────────────────────────────────────────────────────
print("\n=== CURRENT FILTER BLOCK ===")
fi = noc_body.find("const filtered = nocs.filter")
if fi != -1:
    chunk = noc_body[fi:fi+400]
    print(chunk[:400])

print("\n=== CURRENT EXPIRY DROPDOWN ===")
di = noc_body.find("All Dates")
if di != -1:
    print(noc_body[max(0,di-150):di+150])

print("\n=== CURRENT PROJECT DROPDOWN ===")
pi = noc_body.find("All Projects")
if pi != -1:
    print(noc_body[max(0,pi-100):pi+250])

print("\n=== APPLYING FIXES ===")

# ── FIX 1: Project filter comparison — add lowercase ──────────────────────────
patterns_proj = [
    # Most common original pattern
    ('if (fProject!=="All" && n.pid!==fProject) return false;',
     'if (fProject!=="All" && String(n.pid||"").toLowerCase()!==String(fProject||"").toLowerCase()) return false;'),
    ('if (fProject !== "All" && n.pid !== fProject) return false;',
     'if (fProject !== "All" && String(n.pid||"").toLowerCase() !== String(fProject||"").toLowerCase()) return false;'),
    ('if (fProject !== "All" && n.project_id !== fProject) return false;',
     'if (fProject !== "All" && String(n.pid||"").toLowerCase() !== String(fProject||"").toLowerCase()) return false;'),
]
for old, new in patterns_proj:
    if old in noc_body:
        noc_body = noc_body.replace(old, new, 1)
        changes += 1
        print(f"✅ Fixed project filter: {old[:50]}")
        break
else:
    print("⚠️  Project filter pattern not found — showing current:")
    fi2 = noc_body.find("fProject")
    if fi2 != -1:
        print(f"  {noc_body[fi2:fi2+80]}")

# ── FIX 2: Project option value — ensure lowercase UUID ──────────────────────
proj_opt_patterns = [
    ('{projects.map(p=><option key={p.id} value={p.id}>{p.number}</option>)}',
     '{(projects||[]).map(p=><option key={p.id} value={String(p.id).toLowerCase()}>{p.number} \u2014 {p.name}</option>)}'),
    ('{projects.map(p => <option key={p.id} value={p.id}>{p.number}</option>)}',
     '{(projects||[]).map(p=><option key={p.id} value={String(p.id).toLowerCase()}>{p.number} \u2014 {p.name}</option>)}'),
]
for old, new in proj_opt_patterns:
    if old in noc_body:
        noc_body = noc_body.replace(old, new, 1)
        changes += 1
        print(f"✅ Fixed project option values")
        break
else:
    print("⚠️  Project option not matched — may need manual check")

# ── FIX 3: Project onChange — set lowercase ───────────────────────────────────
on_patterns = [
    ('onChange={e=>setFProject(e.target.value)}',
     'onChange={e=>setFProject(String(e.target.value).toLowerCase())}'),
    ('onChange={e => setFProject(e.target.value)}',
     'onChange={e=>setFProject(String(e.target.value).toLowerCase())}'),
]
for old, new in on_patterns:
    if old in noc_body:
        noc_body = noc_body.replace(old, new, 1)
        changes += 1
        print(f"✅ Fixed fProject onChange")
        break

# ── FIX 4: Fix n.pid to lowercase in useNOCs ─────────────────────────────────
hook = app.find("function useNOCs()")
if hook == -1: hook = app.find("const useNOCs =")
if hook != -1:
    h = app[hook:hook+4000]
    # Replace pid mapping
    new_h = re.sub(
        r'pid:\s*[(\s]*n\.project_id\s*\|\|\s*["\']["\'][\s)]*,',
        'pid: String(n.project_id||"").toLowerCase(),',
        h, count=1
    )
    if new_h != h:
        app = app[:hook] + new_h + app[hook+4000:]
        changes += 1
        print("✅ Fixed n.pid lowercase in useNOCs")
    else:
        # Try alternate pattern
        new_h2 = h.replace(
            'pid: n.project_id || "",',
            'pid: String(n.project_id||"").toLowerCase(),'
        )
        if new_h2 != h:
            app = app[:hook] + new_h2 + app[hook+4000:]
            changes += 1
            print("✅ Fixed n.pid lowercase (alt)")
        else:
            print("⚠️  pid pattern not found in useNOCs")
            # Show what we have
            pi2 = h.find("pid:")
            if pi2 != -1:
                print(f"  Current: {h[pi2:pi2+50]}")

# ── FIX 5: Fix expiry option values if needed ─────────────────────────────────
expiry_fixes = [
    # No value attr → add value
    ('<option>All Dates</option>',       '<option value="All">All Dates</option>'),
    ('<option>Expiring Soon</option>',   '<option value="expiring">Expiring Soon (30 days)</option>'),
    ('<option>Expired</option>',         '<option value="expired">Already Expired</option>'),
    # Emoji versions → clean versions
    ('<option value="expiring">⚠️ Expiring Soon</option>', '<option value="expiring">Expiring Soon (30 days)</option>'),
    ('<option value="expired">🚨 Expired</option>',        '<option value="expired">Already Expired</option>'),
    ('<option value="expiring">⚠️  Expiring Soon</option>','<option value="expiring">Expiring Soon (30 days)</option>'),
]
for old, new in expiry_fixes:
    if old in noc_body:
        noc_body = noc_body.replace(old, new)
        changes += 1
        print(f"✅ Fixed expiry option: {old[:45]}")

# ── Rebuild ───────────────────────────────────────────────────────────────────
app = app[:noc_start] + noc_body

with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 55)
print(f"✅ Done — {changes} changes applied")
print(f"   File size: {len(app):,} bytes")
print(f"   Backup: {bk}")
print()
print("Now run:")
print("  set CI=false && npm run build")
print("  npx vercel --prod")
print("=" * 55)
input("Press Enter to exit...")
