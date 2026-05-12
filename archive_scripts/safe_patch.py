#!/usr/bin/env python3
"""
AGBC Safe Patch - Fixes App.js carefully with validation.
Place in C:\Apps\agbc-site-app\ with store_update.js
Run: python safe_patch.py
"""
import os, shutil, re
from datetime import datetime

APP = r"src\App.js"
STORE = "store_update.js"

if not os.path.exists(APP):
    print("ERROR: src\\App.js not found"); input(); exit(1)
if not os.path.exists(STORE):
    print(f"ERROR: {STORE} not found"); input(); exit(1)

# Backup
bk = APP + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(APP, bk)
print(f"✅ Backup: {bk}")

with open(APP, "r", encoding="utf-8") as f:
    app = f.read()
with open(STORE, "r", encoding="utf-8") as f:
    store = f.read()

# ── Helper: find balanced block ───────────────────────────────────────────────
def find_block_end(text, start):
    depth, i = 0, start
    while i < len(text):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0: return i
        i += 1
    return -1

# ── Extract new useStore ──────────────────────────────────────────────────────
us_start = store.find("function useStore() {")
if us_start == -1: print("ERROR: useStore not in store_update.js"); input(); exit(1)
us_end = find_block_end(store, us_start)
new_useStore = store[us_start:us_end+1]
print(f"✅ Extracted useStore ({len(new_useStore)} chars)")

# ── Extract new MaterialStore ─────────────────────────────────────────────────
ms_start = store.find("\nconst MaterialStore = (")
if ms_start == -1: ms_start = store.find("\nconst MaterialStore=(")
if ms_start == -1: print("ERROR: MaterialStore not in store_update.js"); input(); exit(1)
ms_start += 1  # skip \n
# Find the opening { of the arrow function body
arrow_pos = store.find("=> {", ms_start)
if arrow_pos == -1: arrow_pos = store.find("=>{", ms_start)
ms_end = find_block_end(store, arrow_pos)
# Include trailing ;
new_MS = store[ms_start:ms_end+1]
if not new_MS.rstrip().endswith(';'): new_MS = new_MS.rstrip() + ';\n'
print(f"✅ Extracted MaterialStore ({len(new_MS)} chars)")

# ── Replace useStore in App.js ────────────────────────────────────────────────
app_us_start = app.find("function useStore() {")
if app_us_start == -1: print("⚠️  useStore not found in App.js - skipping"); 
else:
    app_us_end = find_block_end(app, app_us_start)
    old_us = app[app_us_start:app_us_end+1]
    app = app[:app_us_start] + new_useStore + app[app_us_end+1:]
    print("✅ Replaced useStore in App.js")

# ── Replace MaterialStore in App.js ──────────────────────────────────────────
app_ms_start = app.find("\nconst MaterialStore = (")
if app_ms_start == -1: app_ms_start = app.find("\nconst MaterialStore=(")
if app_ms_start == -1:
    print("⚠️  MaterialStore not found in App.js")
else:
    app_ms_start += 1
    arrow_pos2 = app.find("=> {", app_ms_start)
    if arrow_pos2 == -1: arrow_pos2 = app.find("=>{", app_ms_start)
    app_ms_end = find_block_end(app, arrow_pos2)
    # Skip trailing semicolon if present
    after = app[app_ms_end+1:app_ms_end+3].strip()
    trim_end = app_ms_end + 1
    if after.startswith(';'): trim_end = app_ms_end + 2
    app = app[:app_ms_start] + new_MS + app[trim_end:]
    print("✅ Replaced MaterialStore in App.js")

# ── Fix destructuring ─────────────────────────────────────────────────────────
new_d = 'const { stock, receipts, issues, loading: stLoad, addStock, updateStock, removeStock, addReceipt, updateReceipt, removeReceipt, addIssue, removeIssue } = useStore();'
for old in [
    'const { stock, receipts, issues, loading: stLoad, addStock, updateStock, removeStock, addReceipt, approveReceipt, removeReceipt, addIssue, removeIssue } = useStore();',
    'const { stock, receipts, issues, loading: stLoad, addStock, updateStock, removeStock, addReceipt, removeReceipt, addIssue, removeIssue } = useStore();',
]:
    if old in app:
        app = app.replace(old, new_d, 1)
        print("✅ Fixed useStore destructuring"); break
else:
    if 'updateReceipt' in app: print("✅ Destructuring already OK")
    else:
        app = re.sub(r'const \{ stock, receipts, issues, loading: stLoad,[^}]+\} = useStore\(\);', new_d, app, count=1)
        print("✅ Fixed destructuring (regex)")

# ── Fix case "store" JSX ──────────────────────────────────────────────────────
new_case = '''      case "store": return <MaterialStore stock={stock} receipts={receipts} issues={issues} loading={stLoad} onAddStock={addStock} onUpdateStock={updateStock} onRemoveStock={removeStock} onAddReceipt={addReceipt} onUpdateReceipt={updateReceipt} onRemoveReceipt={removeReceipt} onAddIssue={addIssue} onRemoveIssue={removeIssue} projects={projects} lpos={lpos} showToast={showToast}/>;'''

# Find case "store" line and replace whole line
lines = app.split('\n')
for i, line in enumerate(lines):
    if 'case "store":' in line:
        lines[i] = new_case
        print('✅ Fixed case "store" JSX')
        break
app = '\n'.join(lines)

# ── Validate — check for duplicate useStore ───────────────────────────────────
count_us = app.count("function useStore() {")
count_ms = app.count("const MaterialStore = (")
print(f"\n📊 Validation:")
print(f"   useStore() occurrences:     {count_us} {'✅' if count_us==1 else '❌ DUPLICATE!'}")
print(f"   MaterialStore occurrences:  {count_ms} {'✅' if count_ms==1 else '❌ DUPLICATE!'}")

if count_us > 1 or count_ms > 1:
    print("\n❌ Duplicates found! Restoring backup...")
    shutil.copy2(bk, APP)
    print(f"✅ Backup restored. Please share this message with your developer.")
    input(); exit(1)

# ── Write ─────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print(f"\n{'='*50}")
print("✅ App.js patched successfully!")
print(f"   Backup: {bk}")
print("\nNext: run   npm run build")
print("      then: npx vercel --prod")
print('='*50)
input("\nPress Enter to exit...")
