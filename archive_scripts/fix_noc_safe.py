#!/usr/bin/env python3
"""
SAFE minimal NOC fix — restore backup first, then ONLY fix filter values.
No JSX changes. No state changes. Just fixes option values + comparison.
Run from: C:\Apps\agbc-site-app\
Command:  python fix_noc_safe.py
"""
import os, shutil, re
from datetime import datetime

APP = r"src\App.js"
if not os.path.exists(APP):
    print("ERROR: src\\App.js not found"); input(); exit(1)

# Check if this looks like a clean file (no ref-based patches)
with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

if "projRef" in app or "authRef" in app:
    print("WARNING: File still has ref-based patches.")
    print("Please restore backup first:")
    print("  copy src\\App.js.bak_20260502_172227 src\\App.js")
    print("Then run this script again.")
    input("Press Enter to exit..."); exit(1)

bk = APP + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(APP, bk)
print(f"Backup: {bk}")

changes = 0

# ── Find NOCModule ─────────────────────────────────────────────────────────────
noc_start = app.find("const NOCModule = (")
if noc_start == -1: noc_start = app.find("const NOCModule=(")
if noc_start == -1: print("ERROR: NOCModule not found"); input(); exit(1)
print(f"NOCModule found at position {noc_start}")

noc_body = app[noc_start:]

# ── DIAGNOSTIC: Show current state of expiry dropdown ─────────────────────────
print("\n--- Current expiry dropdown ---")
idx = noc_body.find("All Dates")
if idx != -1:
    snippet = noc_body[max(0,idx-200):idx+200]
    for line in snippet.split('\n'):
        if line.strip(): print(f"  {line}")

print("\n--- Current project dropdown ---")
idx2 = noc_body.find("All Projects")
if idx2 != -1:
    snippet2 = noc_body[max(0,idx2-200):idx2+300]
    for line in snippet2.split('\n'):
        if line.strip(): print(f"  {line}")

print("\n--- Current filter block ---")
fi = noc_body.find("const filtered = nocs.filter")
if fi != -1:
    fe = noc_body.find("\n  });", fi)
    if fe != -1:
        for line in noc_body[fi:fe+5].split('\n'):
            print(f"  {line}")

# ── FIX 1: Fix fExpiry filter — only change the filter comparison ─────────────
print("\n--- Applying fixes ---")

# Fix the filter block - make comparison robust
old_exp_filter1 = "if (fExpiry===\"expiring\" && !isExpiringSoon(n.expiryDate,n.status)) return false;"
new_exp_filter1 = "if ((fExpiry===\"expiring\"||fExpiry===\"Expiring Soon\") && !isExpiringSoon(n.expiryDate,n.status)) return false;"
old_exp_filter2 = "if (fExpiry===\"expired\" && !isExpired(n.expiryDate,n.status)) return false;"
new_exp_filter2 = "if ((fExpiry===\"expired\"||fExpiry===\"Expired\") && !isExpired(n.expiryDate,n.status)) return false;"

if old_exp_filter1 in noc_body:
    noc_body = noc_body.replace(old_exp_filter1, new_exp_filter1, 1)
    noc_body = noc_body.replace(old_exp_filter2, new_exp_filter2, 1)
    changes += 1
    print("Fixed expiry filter (with spaces variation)")

# Also fix spaced version
old_es = "if (fExpiry === \"expiring\" && !isExpiringSoon(n.expiryDate, n.status)) return false;"
new_es = "if ((fExpiry === \"expiring\" || fExpiry === \"Expiring Soon\") && !isExpiringSoon(n.expiryDate, n.status)) return false;"
old_ex = "if (fExpiry === \"expired\"  && !isExpired(n.expiryDate,      n.status)) return false;"
new_ex = "if ((fExpiry === \"expired\"  || fExpiry === \"Expired\") && !isExpired(n.expiryDate, n.status)) return false;"
old_ex2 = "if (fExpiry === \"expired\" && !isExpired(n.expiryDate, n.status)) return false;"
new_ex2 = "if ((fExpiry === \"expired\" || fExpiry === \"Expired\") && !isExpired(n.expiryDate, n.status)) return false;"

if old_es in noc_body:
    noc_body = noc_body.replace(old_es, new_es, 1)
    changes += 1
    print("Fixed expiry filter (spaced version)")
if old_ex in noc_body:
    noc_body = noc_body.replace(old_ex, new_ex, 1)
if old_ex2 in noc_body:
    noc_body = noc_body.replace(old_ex2, new_ex2, 1)

# ── FIX 2: Ensure expiry dropdown options have correct VALUES ─────────────────
# Replace text-based options with explicit value attributes
expiry_fixes = [
    # If options don't have value attr
    ("<option>Expiring Soon</option>",  '<option value="expiring">Expiring Soon</option>'),
    ("<option>Expired</option>",        '<option value="expired">Expired</option>'),
    ("<option>All Dates</option>",      '<option value="All">All Dates</option>'),
    # If options have emoji but correct values
    ('<option value="expiring">⚠️ Expiring Soon</option>', '<option value="expiring">Expiring Soon (30 days)</option>'),
    ('<option value="expired">🚨 Expired</option>',        '<option value="expired">Already Expired</option>'),
    # Spaced versions
    ('<option value="expiring">⚠️ Expiring Soon (30 days)</option>', '<option value="expiring">Expiring Soon (30 days)</option>'),
]
for old, new in expiry_fixes:
    if old in noc_body:
        noc_body = noc_body.replace(old, new)
        changes += 1
        print(f"Fixed option: {old[:40]} -> {new[:40]}")

# ── FIX 3: Fix project filter comparison ─────────────────────────────────────
proj_filter_fixes = [
    # Original strict comparison
    ("if (fProject!==\"All\" && n.pid!==fProject) return false;",
     "if (fProject!==\"All\" && String(n.pid||'').toLowerCase()!==String(fProject||'').toLowerCase()) return false;"),
    # With spaces
    ("if (fProject !== \"All\" && n.pid !== fProject) return false;",
     "if (fProject !== \"All\" && String(n.pid||'').toLowerCase() !== String(fProject||'').toLowerCase()) return false;"),
    # Previous partial fix
    ("if (fProject && fProject!==\"All\" && String(n.pid)!==String(fProject)) return false;",
     "if (fProject && fProject!==\"All\" && String(n.pid||'').toLowerCase()!==String(fProject||'').toLowerCase()) return false;"),
]
for old, new in proj_filter_fixes:
    if old in noc_body:
        noc_body = noc_body.replace(old, new, 1)
        changes += 1
        print(f"Fixed project filter comparison")

# ── FIX 4: Fix project option values to use lowercase ────────────────────────
# Find project options in NOCModule and ensure value uses lowercase
# Pattern: <option key={p.id} value={p.id}>
old_proj_opt = "{projects.map(p=><option key={p.id} value={p.id}>{p.number}</option>)}"
new_proj_opt = "{(projects||[]).map(p=><option key={p.id} value={String(p.id).toLowerCase()}>{p.number} \u2014 {p.name}</option>)}"
if old_proj_opt in noc_body:
    noc_body = noc_body.replace(old_proj_opt, new_proj_opt, 1)
    changes += 1
    print("Fixed project option values")

# Also fix onChange to lowercase
old_onch = "onChange={e=>setFProject(e.target.value)}"
new_onch = "onChange={e=>setFProject(String(e.target.value).toLowerCase())}"
if old_onch in noc_body:
    noc_body = noc_body.replace(old_onch, new_onch, 1)
    changes += 1
    print("Fixed fProject onChange")

# And n.pid in useNOCs hook
hook_start = app.find("function useNOCs()")
if hook_start == -1:
    hook_start = app.find("const useNOCs =")
if hook_start != -1:
    hook_body = app[hook_start:hook_start+3000]
    new_hook = re.sub(
        r"pid:\s*[(\s]*n\.project_id\s*\|\|\s*[\"'][\"'][\s)]*,",
        'pid: String(n.project_id||"").toLowerCase(),',
        hook_body
    )
    if new_hook != hook_body:
        app = app[:hook_start] + new_hook + app[hook_start+3000:]
        changes += 1
        print("Fixed n.pid in useNOCs")

# ── Rebuild ───────────────────────────────────────────────────────────────────
app = app[:noc_start] + noc_body

with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 55)
print(f"Done! {changes} changes applied.")
print(f"Backup: {bk}")
print()
print("IMPORTANT: Run build test first!")
print("  set CI=false && npm run build")
print("  (only deploy if it says 'Compiled successfully')")
print("  npx vercel --prod")
print("=" * 55)
input("Press Enter to exit...")
