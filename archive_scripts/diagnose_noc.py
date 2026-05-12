#!/usr/bin/env python3
"""
Diagnostic - shows current NOC filter code
Run from: C:\Apps\agbc-site-app\
Command:  python diagnose_noc.py
"""
import os, re

APP = r"src\App.js"
if not os.path.exists(APP):
    print("ERROR: src\\App.js not found"); input(); exit(1)

with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

noc_start = app.find("const NOCModule = (")
if noc_start == -1:
    noc_start = app.find("const NOCModule=(")
if noc_start == -1:
    print("ERROR: NOCModule not found"); input(); exit(1)

noc_body = app[noc_start:noc_start+8000]
lines = noc_body.split('\n')

print("=" * 60)
print("NOC FILTER DIAGNOSTICS")
print("=" * 60)

# 1. Show all useState declarations
print("\n[1] STATE DECLARATIONS:")
for i, line in enumerate(lines[:80]):
    if 'useState' in line and ('fProject' in line or 'fAuth' in line or 
       'fStatus' in line or 'fExpiry' in line or 'search' in line.lower()):
        print(f"  Line {i:3d}: {line.strip()}")

# 2. Show useEffect for navFilter
print("\n[2] NAVFILTER USEEFFECT:")
for i, line in enumerate(lines[:150]):
    if 'navFilter' in line or ('useEffect' in line and i < 100):
        print(f"  Line {i:3d}: {line.strip()}")

# 3. Show the expiry dropdown
print("\n[3] EXPIRY DROPDOWN (lines around 'All Dates'):")
for i, line in enumerate(lines):
    if 'All Dates' in line or 'fExpiry' in line and ('Sel' in line or 'select' in line or 'onChange' in line):
        start = max(0, i-2)
        end = min(len(lines), i+8)
        for j in range(start, end):
            print(f"  Line {j:3d}: {lines[j]}")
        print("  ...")
        break

# 4. Show project dropdown
print("\n[4] PROJECT DROPDOWN:")
for i, line in enumerate(lines):
    if 'All Projects' in line:
        start = max(0, i-2)
        end = min(len(lines), i+6)
        for j in range(start, end):
            print(f"  Line {j:3d}: {lines[j]}")
        break

# 5. Show filter block
print("\n[5] FILTER BLOCK (nocs.filter):")
filter_idx = noc_body.find("const filtered = nocs.filter")
if filter_idx != -1:
    chunk = noc_body[filter_idx:filter_idx+600]
    for i, line in enumerate(chunk.split('\n')[:20]):
        print(f"  {i:3d}: {line}")

# 6. Count duplicates
print("\n[6] DUPLICATE CHECK:")
for v in ["fProject", "fAuth", "fStatus", "fExpiry"]:
    count = sum(1 for line in lines[:200] if f"[{v}," in line and "useState" in line)
    status = "OK" if count == 1 else f"*** {count} DUPLICATES ***"
    print(f"  {v} useState count: {count} — {status}")

print("\n" + "=" * 60)
print("Copy ALL text above and share it.")
print("=" * 60)
input("\nPress Enter to exit...")
