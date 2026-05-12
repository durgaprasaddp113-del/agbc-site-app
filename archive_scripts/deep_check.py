#!/usr/bin/env python3
"""
Deep diagnostic - shows exact code for all 3 issues
Run: python deep_check.py
"""
import os

APP = r"src\App.js"
with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

lines = app.split('\n')

def show_lines(label, search, before=5, after=15):
    idx = app.find(search)
    if idx == -1:
        print(f"\n[{label}] NOT FOUND: {search}")
        return
    line_no = app[:idx].count('\n')
    print(f"\n[{label}] Found at line {line_no}:")
    for i in range(max(0,line_no-before), min(len(lines),line_no+after)):
        print(f"  {i+1:5d}: {lines[i]}")

print("="*60)
print("DEEP DIAGNOSTIC REPORT")
print("="*60)

# 1. Check ManpowerMaster component
print(f"\n1. ManpowerMaster component: {'YES' if 'const ManpowerMaster' in app else 'NO - NOT FOUND'}")
print(f"   useManpowerMaster hook:    {'YES' if 'useManpowerMaster' in app else 'NO'}")

# 2. Show the exact renderPage / switch block
show_lines("RENDERPAGE SWITCH", 'case "manpower-master"', 2, 3)
show_lines("CASE STORE", 'case "store"', 2, 3)
show_lines("CASE REPORTS", 'case "reports"', 2, 3)
show_lines("CASE NOC", 'case "noc"', 2, 3)
show_lines("DEFAULT CASE", 'default:', 2, 5)

# 3. Show useStore destructuring
show_lines("USESTORE DESTRUCT", 'const { stock, receipts', 1, 3)

# 4. Show MaterialStore component signature
show_lines("MATERIALSTORE COMP", 'const MaterialStore = (', 1, 5)

# 5. Show LPO Others
show_lines("LPO OTHERS", '>Others<', 5, 10)
show_lines("LPO OTHERS2", '"Others"', 5, 10)

# 6. Count how many times key items appear
print(f"\n5. Counts:")
print(f"   'case \"store\"'       : {app.count('case \"store\"')} times")
print(f"   'manpower-master'   : {app.count('manpower-master')} times")
print(f"   'ManpowerMaster'    : {app.count('ManpowerMaster')} times")
print(f"   'Module coming soon': {app.count('Module coming soon')} times")
print(f"   'function useStore' : {app.count('function useStore')} times")
print(f"   'updateReceipt'     : {app.count('updateReceipt')} times")

# 7. Show "Module coming soon" context
show_lines("COMING SOON", 'Module coming soon', 5, 5)

# 8. Show the renderPage function
rp_idx = app.find('const renderPage')
if rp_idx == -1: rp_idx = app.find('function renderPage')
if rp_idx == -1: rp_idx = app.find('renderPage =')
if rp_idx != -1:
    chunk = app[rp_idx:rp_idx+2000]
    print(f"\n[RENDERPAGE FULL - first 2000 chars]")
    for i, line in enumerate(chunk.split('\n')[:60]):
        print(f"  {i+1:3d}: {line}")
else:
    print("\n[RENDERPAGE] Function not found by name")
    # Try to find switch(page)
    sw_idx = app.find('switch(page)')
    if sw_idx == -1: sw_idx = app.find('switch (page)')
    if sw_idx != -1:
        chunk = app[sw_idx:sw_idx+2000]
        print(f"\n[SWITCH PAGE - first 2000 chars]")
        for i, line in enumerate(chunk.split('\n')[:60]):
            print(f"  {i+1:3d}: {line}")

print("\n" + "="*60)
print("Copy ALL text above and share it.")
print("="*60)
input("Press Enter...")
