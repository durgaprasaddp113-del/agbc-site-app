#!/usr/bin/env python3
"""
AGBC Store Fix — adds missing constants before useStore()
Run from: C:\Apps\agbc-site-app\
"""
import os, shutil
from datetime import datetime

PATH = r"src\App.js"

CONSTANTS = '''
// ─────────────────────────────────────────────────────────────────────────────
// MATERIAL STORE CONSTANTS
// ─────────────────────────────────────────────────────────────────────────────
const DEPT_LIST = ["Civil","MEP","Architecture","QAQC","Store","Safety","Admin"];

const STOCK_CATS = [
  "Cement & Concrete","Steel & Rebar","Blocks & Masonry",
  "Sand & Aggregate","Tiles & Finishes","Waterproofing",
  "MEP Materials","Paints & Chemicals","Safety Equipment",
  "Tools & Equipment","Others",
];

const STOCK_STATUS = ["Available","Low Stock","Out of Stock","Inactive"];

const ST_BADGE = {
  "Available":    "bg-green-100 text-green-700 border-green-200",
  "Low Stock":    "bg-amber-100 text-amber-700 border-amber-200",
  "Out of Stock": "bg-red-100 text-red-700 border-red-200",
  "Inactive":     "bg-slate-100 text-slate-500 border-slate-200",
};

const EMPTY_STOCK_ITEM = () => ({
  id: Date.now() + Math.random(),
  stockId:"", name:"", unit:"Nos", qty:0, remarks:""
});

const EMPTY_STOCK_FORM = () => ({
  code:"", name:"", category:"Cement & Concrete",
  unit:"Nos", pid:"", location:"",
  opening:"0", received:"0", issued:"0",
  minLevel:"0", supplier:"", rate:"",
  status:"Available", remarks:""
});

const EMPTY_ISS_FORM = () => ({
  pid:"", issuedTo:"", dept:"Civil", location:"",
  issueDate: new Date().toISOString().split("T")[0],
  issuedBy:"", purpose:"", remarks:"",
  items:[EMPTY_STOCK_ITEM()]
});

'''

if not os.path.exists(PATH):
    print(f"ERROR: {PATH} not found. Run this from C:\\Apps\\agbc-site-app\\")
    exit(1)

backup = PATH + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(PATH, backup)
print(f"✅ Backup: {backup}")

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# 1. Add missing constants before useStore
ANCHOR = "function useStore() {"
if CONSTANTS.strip() not in content and ANCHOR in content:
    content = content.replace(ANCHOR, CONSTANTS + ANCHOR, 1)
    changes += 1
    print("✅ Added 7 missing store constants")
else:
    if "EMPTY_STOCK_FORM" in content:
        print("✅ Constants already exist — skipped")
        changes += 1
    else:
        print("⚠️  Could not find anchor 'function useStore()' — check App.js")

# 2. Ensure approveReceipt in destructuring
old_d = "const { stock, receipts, issues, loading: stLoad, addStock, updateStock, removeStock, addReceipt, removeReceipt, addIssue, removeIssue } = useStore();"
new_d = "const { stock, receipts, issues, loading: stLoad, addStock, updateStock, removeStock, addReceipt, approveReceipt, removeReceipt, addIssue, removeIssue } = useStore();"
if old_d in content:
    content = content.replace(old_d, new_d, 1)
    changes += 1
    print("✅ Added approveReceipt to destructuring")
elif "approveReceipt" in content:
    print("✅ approveReceipt already in destructuring")
    changes += 1

# 3. Ensure onApproveReceipt prop
old_jsx = 'onAddReceipt={addReceipt} onRemoveReceipt={removeReceipt}'
new_jsx = 'onAddReceipt={addReceipt} onApproveReceipt={approveReceipt} onRemoveReceipt={removeReceipt}'
if old_jsx in content:
    content = content.replace(old_jsx, new_jsx, 1)
    changes += 1
    print("✅ Added onApproveReceipt prop")
elif "onApproveReceipt" in content:
    print("✅ onApproveReceipt already in JSX")
    changes += 1

with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n{'='*50}")
print(f"✅ Done! {changes} changes applied.")
print(f"Backup at: {backup}")
