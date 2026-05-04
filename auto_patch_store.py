#!/usr/bin/env python3
"""
AGBC Auto Patch - Run this file, it fixes everything automatically.
Place this file in: C:\Apps\agbc-site-app\
Then run: python auto_patch_store.py
"""
import os, re, shutil
from datetime import datetime

APP = r"src\App.js"
STORE_FILE = "store_update.js"  # put store_update.js in same folder as this script

# ── Check files exist ──────────────────────────────────────────────────────────
if not os.path.exists(APP):
    print("ERROR: src\\App.js not found.")
    print("Make sure you run this script from C:\\Apps\\agbc-site-app\\")
    input("Press Enter to exit...")
    exit(1)

if not os.path.exists(STORE_FILE):
    print(f"ERROR: {STORE_FILE} not found.")
    print(f"Put {STORE_FILE} in the same folder as this script.")
    input("Press Enter to exit...")
    exit(1)

# ── Backup App.js ──────────────────────────────────────────────────────────────
backup = APP + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(APP, backup)
print(f"✅ Backup saved: {backup}")

# ── Read files ─────────────────────────────────────────────────────────────────
with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

with open(STORE_FILE, "r", encoding="utf-8") as f:
    store_code = f.read()

# ── Extract useStore function from store_update.js ────────────────────────────
def extract_function(code, start_marker):
    idx = code.find(start_marker)
    if idx == -1:
        return None
    # Find matching closing brace
    depth = 0
    started = False
    i = idx
    while i < len(code):
        if code[i] == '{':
            depth += 1
            started = True
        elif code[i] == '}':
            depth -= 1
            if started and depth == 0:
                return code[idx:i+1]
        i += 1
    return None

new_useStore = extract_function(store_code, "function useStore() {")
if not new_useStore:
    print("ERROR: Could not find 'function useStore()' in store_update.js")
    input("Press Enter to exit...")
    exit(1)
print("✅ Extracted new useStore() from store_update.js")

# ── Extract MaterialStore from store_update.js ────────────────────────────────
ms_start = store_code.find("const MaterialStore = (")
if ms_start == -1:
    ms_start = store_code.find("const MaterialStore=(")
if ms_start == -1:
    print("ERROR: Could not find 'const MaterialStore' in store_update.js")
    input("Press Enter to exit...")
    exit(1)
# Find end - find the last "};" after the component
ms_rest = store_code[ms_start:]
# Find the closing "};" of the arrow function
depth = 0
started = False
end_idx = ms_start
for i, ch in enumerate(ms_rest):
    if ch == '{':
        depth += 1
        started = True
    elif ch == '}':
        if started:
            depth -= 1
            if depth == 0:
                end_idx = ms_start + i + 1
                # Check for ; after }
                remaining = ms_rest[i+1:i+3].strip()
                if remaining.startswith(';'):
                    end_idx += 1
                break
new_MaterialStore = store_code[ms_start:end_idx]
if not new_MaterialStore.strip().endswith(';'):
    new_MaterialStore += ';'
print("✅ Extracted new MaterialStore from store_update.js")

# ── Fix 1: Replace function useStore() in App.js ──────────────────────────────
old_useStore = extract_function(app, "function useStore() {")
if old_useStore:
    app = app.replace(old_useStore, new_useStore, 1)
    print("✅ Replaced useStore() in App.js")
else:
    print("⚠️  Could not find useStore() in App.js - adding before export default")

# ── Fix 2: Replace MaterialStore component in App.js ─────────────────────────
ms_pos = app.find("const MaterialStore = (")
if ms_pos == -1:
    ms_pos = app.find("const MaterialStore=(")

if ms_pos != -1:
    # Find end of existing MaterialStore
    rest = app[ms_pos:]
    depth = 0
    started = False
    end = ms_pos
    for i, ch in enumerate(rest):
        if ch == '{':
            depth += 1
            started = True
        elif ch == '}':
            if started:
                depth -= 1
                if depth == 0:
                    end = ms_pos + i + 1
                    if rest[i+1:i+3].strip().startswith(';'):
                        end += 1
                    break
    old_ms = app[ms_pos:end]
    app = app[:ms_pos] + new_MaterialStore + app[end:]
    print("✅ Replaced MaterialStore in App.js")
else:
    print("⚠️  Could not find MaterialStore in App.js")

# ── Fix 3: Update useStore destructuring ──────────────────────────────────────
old_destruct_patterns = [
    'const { stock, receipts, issues, loading: stLoad, addStock, updateStock, removeStock, addReceipt, approveReceipt, removeReceipt, addIssue, removeIssue } = useStore();',
    'const { stock, receipts, issues, loading: stLoad, addStock, updateStock, removeStock, addReceipt, removeReceipt, addIssue, removeIssue } = useStore();',
]
new_destruct = 'const { stock, receipts, issues, loading: stLoad, addStock, updateStock, removeStock, addReceipt, updateReceipt, removeReceipt, addIssue, removeIssue } = useStore();'

replaced_destruct = False
for old in old_destruct_patterns:
    if old in app:
        app = app.replace(old, new_destruct, 1)
        replaced_destruct = True
        print("✅ Updated useStore destructuring")
        break

if not replaced_destruct:
    if 'updateReceipt' in app and 'useStore()' in app:
        print("✅ useStore destructuring already correct")
    else:
        # Try regex replace
        pattern = r'const \{ stock, receipts, issues, loading: stLoad,[^}]+\} = useStore\(\);'
        if re.search(pattern, app):
            app = re.sub(pattern, new_destruct, app, count=1)
            print("✅ Updated useStore destructuring (regex)")
        else:
            print("⚠️  Could not update useStore destructuring - do it manually")

# ── Fix 4: Update case "store" JSX ────────────────────────────────────────────
new_case = 'case "store": return <MaterialStore stock={stock} receipts={receipts} issues={issues} loading={stLoad} onAddStock={addStock} onUpdateStock={updateStock} onRemoveStock={removeStock} onAddReceipt={addReceipt} onUpdateReceipt={updateReceipt} onRemoveReceipt={removeReceipt} onAddIssue={addIssue} onRemoveIssue={removeIssue} projects={projects} lpos={lpos} showToast={showToast}/>;'

# Find any case "store": line
store_case_pattern = r'case "store":[^\n]*\n'
match = re.search(store_case_pattern, app)
if match:
    app = app[:match.start()] + new_case + '\n' + app[match.end():]
    print('✅ Updated case "store" JSX')
elif 'case "store"' in app:
    print('✅ case "store" already exists - checking props...')
    if 'onUpdateReceipt' not in app:
        # Add onUpdateReceipt prop
        app = app.replace(
            'onAddReceipt={addReceipt} onRemoveReceipt={removeReceipt}',
            'onAddReceipt={addReceipt} onUpdateReceipt={updateReceipt} onRemoveReceipt={removeReceipt}',
            1
        )
        print('✅ Added onUpdateReceipt prop')
else:
    print('⚠️  case "store" not found - add manually inside renderPage()')

# ── Write patched App.js ───────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 55)
print("✅ ALL DONE! App.js has been updated successfully.")
print(f"   Backup saved at: {backup}")
print()
print("Next step: run   npx vercel --prod")
print("=" * 55)
input("\nPress Enter to exit...")
