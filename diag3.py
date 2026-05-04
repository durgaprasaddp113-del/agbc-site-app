import os, shutil
from datetime import datetime

APP = r"src\App.js"

with open(APP, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []

# 1. Find EMPTY_STOCK_FORM definition
for i,l in enumerate(lines):
    if "EMPTY_STOCK_FORM" in l and ("const " in l or "function " in l):
        out.append("EMPTY_STOCK_FORM defined at line " + str(i+1) + ": " + l.rstrip())

# 2. Find LPO form mode section (not view mode)
lpo_start = 0
for i,l in enumerate(lines):
    if "const LPOModule = (" in l:
        lpo_start = i
        break

lpo_form_line = 0
for i in range(lpo_start, min(lpo_start+1500, len(lines))):
    l = lines[i]
    if 'mode==="form"' in l or 'mode === "form"' in l:
        if 'view' not in l:  # skip view mode
            lpo_form_line = i
            break

out.append("\nLPO FORM MODE at line " + str(lpo_form_line+1))
for i in range(lpo_form_line, min(lpo_form_line+120, len(lines))):
    out.append(str(i+1) + ": " + lines[i].rstrip()[:130])

# 3. Find useStore final return
us = 0
for i,l in enumerate(lines):
    if "function useStore() {" in l:
        us = i
        break
# Find last return { in useStore
for i in range(us+400, min(us+600, len(lines))):
    if "return {" in lines[i] and "ok:" not in lines[i]:
        out.append("\nuseStore FINAL RETURN at line " + str(i+1))
        for j in range(i, min(i+20, len(lines))):
            out.append(str(j+1) + ": " + lines[j].rstrip()[:130])
        break

result = "\n".join(out)
with open("diag3.txt", "w", encoding="utf-8") as f:
    f.write(result)
print(result)
print("\nSaved to diag3.txt")
input("Press Enter...")
