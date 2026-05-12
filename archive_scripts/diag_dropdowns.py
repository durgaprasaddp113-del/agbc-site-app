APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')

def show(label,a,b):
    print("=== "+label+" ===")
    for i in range(a,min(b,len(lines))):
        print(str(i+1)+"\t"+s(lines[i].rstrip()))
    print()

def find(t):
    for i,l in enumerate(lines): 
        if t in l: return i
    return -1

# ── Show FULL dropdown sections for MR, LPO, NOC ─────────────────────
print("### MR DROPDOWN (full) ###")
show("MR dropdown", 5921, 5927)

print("### LPO DROPDOWN (full) ###")
lpo = find("const LPOModule = (")
if lpo != -1:
    # Find the fProject Sel in LPO
    for i in range(lpo+200, min(lpo+600, len(lines))):
        if "fProject" in lines[i] and "Sel" in lines[i]:
            show("LPO Sel found", i, i+8)
            break

print("### NOC DROPDOWN (full) ###")
noc = find("const NOCModule = (")
if noc != -1:
    for i in range(noc+200, min(noc+700, len(lines))):
        if "fProject" in lines[i] and "Sel" in lines[i]:
            show("NOC Sel found", i, i+10)
            break

# ── Show option value= attributes specifically ────────────────────────
print("### OPTION VALUE ATTRS in MR/LPO/NOC dropdowns ###")
mr   = find("const MaterialRequests = (")
lpo  = find("const LPOModule = (")
noc  = find("const NOCModule = (")

for label, start in [("MR",mr),("LPO",lpo),("NOC",noc)]:
    if start == -1: continue
    end = min(start+700, len(lines))
    found_sel = False
    for i in range(start+100, end):
        l = lines[i]
        if "fProject" in l and "Sel" in l:
            found_sel = True
        if found_sel and "option" in l and ("p.id" in l or "p.number" in l or "p.name" in l or "value=" in l):
            print(label+" L"+str(i+1)+": "+s(l.rstrip())[:200])
        if found_sel and "</Sel>" in l or (found_sel and i > start+500):
            break

# ── Show useMatReqs, useLPOs, useNOCs pid storage ─────────────────────
print()
print("### HOOK PID STORAGE ###")
for hook in ["function useMatReqs","function useLPOs","function useNOCs"]:
    idx = find(hook)
    if idx != -1:
        for j in range(idx, min(idx+60, len(lines))):
            if "pid:" in lines[j] and ("project_id" in lines[j] or "String" in lines[j]):
                print(hook+" L"+str(j+1)+": "+s(lines[j].rstrip()))
        print()

# ── Show what value fProject is set to in all 3 dropdowns ────────────
print("### ALL setFProject onChange calls ###")
for i,l in enumerate(lines):
    if "setFProject" in l and "onChange" in l:
        print("L"+str(i+1)+" [lc="+str("toLowerCase" in l)+"]: "+s(l.rstrip())[:160])

print("\n=== DONE ===")
input("Press Enter...")
