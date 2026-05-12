import sys
APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
total = len(lines)

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def show(label,a,b):
    print("=== "+label+" ===")
    for i in range(a,min(b+1,total)):
        print(str(i+1)+"\t"+s(lines[i].rstrip()))
    print()
def find(t):
    for i,l in enumerate(lines):
        if t in l: return i
    return -1

print("Total lines:",total)

# useMatReqs pid
print("\n### useMatReqs pid ###")
idx=find("function useMatReqs(")
if idx!=-1:
    for j in range(idx,min(idx+50,total)):
        if "pid:" in lines[j] or "project_id" in lines[j]:
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:120])

# MR dropdown
print("\n### MR dropdown (L5919-5930) ###")
show("MR dropdown",5919,5930)

# MR filter
print("\n### MR filter ###")
mr=find("const MaterialRequests = (")
if mr!=-1:
    fi=-1
    for j in range(mr,min(mr+350,total)):
        if "const filtered" in lines[j]: fi=j; break
    if fi!=-1: show("MR filter",fi,fi+12)

# LPO filter
print("\n### LPO filter ###")
lpo=find("const LPOModule = (")
if lpo!=-1:
    fi=-1
    for j in range(lpo,min(lpo+400,total)):
        if "const filtered" in lines[j]: fi=j; break
    if fi!=-1: show("LPO filter",fi,fi+12)

# LPO dropdown lines
print("\n### LPO fProject dropdown ###")
if lpo!=-1:
    for j in range(lpo,min(lpo+500,total)):
        if "fProject" in lines[j] and ("Sel" in lines[j] or "option" in lines[j]):
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:160])

# NOC filter
print("\n### NOC filter ###")
noc=find("const NOCModule = (")
if noc!=-1:
    fi=-1
    for j in range(noc,min(noc+400,total)):
        if "const filtered" in lines[j]: fi=j; break
    if fi!=-1: show("NOC filter",fi,fi+12)

# NOC dropdown lines
print("\n### NOC fProject dropdown ###")
if noc!=-1:
    for j in range(noc,min(noc+600,total)):
        if "fProject" in lines[j] and ("Sel" in lines[j] or "option" in lines[j]):
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:160])

print("\n=== DONE ===")
input("Press Enter...")
