APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def show(label,a,b):
    print("=== "+label+" ===")
    for i in range(a,min(b,len(lines))):
        print(str(i+1)+"\t"+s(lines[i].rstrip()))
    print()

# 1. Full lines for MR form project selector
print("### MR FORM PROJECT SELECTOR - FULL LINE ###")
show("L5863-5866", 5862, 5866)

# 2. Full lines for LPO form project selector
print("### LPO FORM PROJECT SELECTOR - FULL LINE ###")
show("L6170-6173", 6169, 6173)

# 3. MR table row - how PROJECT column is rendered
print("### MR TABLE ROW - PROJECT COLUMN ###")
mr_idx = next((i for i,l in enumerate(lines) if "const MaterialRequests = (" in l), -1)
if mr_idx != -1:
    for j in range(mr_idx+200, min(mr_idx+700, len(lines))):
        l = lines[j]
        if ("proj" in l.lower() or "number" in l) and "<td" in l:
            print("L"+str(j+1)+": "+s(l.rstrip())[:200])
        if j > mr_idx+700: break

# 4. How m.pid is used for project name lookup in MR list
print("\n### MR LIST - pid lookup for display ###")
if mr_idx != -1:
    for j in range(mr_idx+100, min(mr_idx+800, len(lines))):
        l = lines[j]
        if ".pid" in l and ("find" in l or "filter" in l or "number" in l or "proj" in l.lower()):
            print("L"+str(j+1)+": "+s(l.rstrip())[:200])

# 5. NOC form project selector
print("\n### NOC FORM PROJECT SELECTOR ###")
noc_idx = next((i for i,l in enumerate(lines) if "const NOCModule = (" in l), -1)
if noc_idx != -1:
    for j in range(noc_idx, min(noc_idx+400, len(lines))):
        l = lines[j]
        if "pid" in l and ("option" in l or "Sel" in l) and "form" in l.lower():
            print("L"+str(j+1)+": "+s(l.rstrip())[:200])

# 6. The Sel component definition
print("\n### Sel COMPONENT DEFINITION ###")
for i,l in enumerate(lines):
    if "const Sel " in l or "const Sel=" in l or "function Sel(" in l:
        show("Sel definition", i, i+5)
        break

# 7. Check if there's a useMemo or useEffect wrapping filtered
print("\n### MR COMPONENT - is filtered in useMemo? ###")
if mr_idx != -1:
    for j in range(mr_idx, min(mr_idx+50, len(lines))):
        print(str(j+1)+"\t"+s(lines[j].rstrip()))

print("\n=== DONE ===")
input("Press Enter...")
