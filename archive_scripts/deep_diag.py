import re

APP = r"src\App.js"

with open(APP, "r", encoding="utf-8") as f:
    lines = f.readlines()

total = len(lines)
print("Total lines: " + str(total))
print()

def show_lines(label, start, end):
    print("=== " + label + " (lines " + str(start+1) + "-" + str(end+1) + ") ===")
    for i in range(start, min(end+1, total)):
        print(str(i+1) + "\t" + lines[i].rstrip())
    print()

def find_line(text):
    for i,l in enumerate(lines):
        if text in l:
            return i
    return -1

print("### HOOK LOCATIONS ###")
for sig in ["function useMRs", "function useLPOs", "function useNOCs"]:
    i = find_line(sig)
    print(sig + " at line " + str(i+1) if i != -1 else sig + " NOT FOUND")
print()

print("### PID MAPPING IN HOOKS ###")
for sig in ["function useMRs", "function useLPOs", "function useNOCs"]:
    idx = find_line(sig)
    if idx == -1:
        print(sig + ": NOT FOUND")
        continue
    chunk = lines[idx:idx+80]
    for j, l in enumerate(chunk):
        if "pid" in l or "project_id" in l or ".map(" in l:
            print(sig + " L" + str(idx+j+1) + ": " + l.rstrip()[:120])
    print()

print("### FPROJECT FILTER LINES ###")
for module, sig in [("MR","const MaterialRequests = ("), ("LPO","const LPOModule = ("), ("NOC","const NOCModule = (")]:
    idx = find_line(sig)
    if idx == -1:
        print(module + ": component NOT FOUND")
        continue
    chunk = lines[idx:idx+300]
    for j, l in enumerate(chunk):
        if "fProject" in l or "setFProject" in l:
            print(module + " L" + str(idx+j+1) + ": " + l.rstrip()[:120])
    print()

print("### FULL FILTERED BLOCKS ###")
for module, sig in [("MR","const MaterialRequests = ("), ("LPO","const LPOModule = ("), ("NOC","const NOCModule = (")]:
    idx = find_line(sig)
    if idx == -1:
        print(module + ": NOT FOUND")
        continue
    fi = -1
    for j in range(idx, min(idx+400, total)):
        if "const filtered" in lines[j]:
            fi = j
            break
    if fi == -1:
        print(module + ": filtered block NOT FOUND")
        continue
    show_lines(module + " filtered block", fi, min(fi+20, total-1))

print("### ALL r.project_id OCCURRENCES ###")
found_r = False
for i, l in enumerate(lines):
    if "r.project_id" in l:
        print("L" + str(i+1) + ": " + l.rstrip()[:120])
        found_r = True
if not found_r:
    print("None found - good!")
print()

print("### PROJECT DROPDOWN OPTION VALUES ###")
for i, l in enumerate(lines):
    if "option" in l and ("value={p.id}" in l or "value={String(p.id)" in l):
        print("L" + str(i+1) + ": " + l.rstrip()[:120])
print()

print("### MATERIAL STORE CONSTANTS ###")
for const in ["EMPTY_STOCK_FORM","EMPTY_STOCK_ITEM","EMPTY_ISS_FORM","STOCK_CATS","STOCK_STATUS","ST_BADGE","DEPT_LIST"]:
    found = [i for i, l in enumerate(lines) if "const " + const in l]
    if found:
        print(const + " at L" + str(found[0]+1) + ": " + lines[found[0]].strip()[:80])
    else:
        print(const + " *** NOT DEFINED ***")
print()

print("### useStore RETURN ###")
idx = find_line("function useStore(")
if idx == -1:
    idx = find_line("function useStore (")
if idx != -1:
    for j in range(idx, min(idx+250, total)):
        if "return {" in lines[j]:
            show_lines("useStore return", j, min(j+15, total-1))
            break
else:
    print("useStore NOT FOUND")
print()

print("### MaterialStore COMPONENT ###")
idx = find_line("const MaterialStore = ({")
if idx != -1:
    print("MaterialStore at L" + str(idx+1))
    show_lines("MaterialStore props", idx, min(idx+5, total-1))
else:
    print("MaterialStore NOT FOUND")
print()

print("=== DONE ===")
