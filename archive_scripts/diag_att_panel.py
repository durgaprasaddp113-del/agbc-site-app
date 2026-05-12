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

# Full DprAttendancePanel component
dap = find("const DprAttendancePanel = (")
if dap != -1:
    # find end by brace counting
    depth=0
    end=dap
    for i in range(dap,min(dap+300,len(lines))):
        depth += lines[i].count('{') - lines[i].count('}')
        if depth<=0 and i>dap+5:
            end=i; break
    show("DprAttendancePanel FULL", dap, end+1)
    print(f"Lines: {dap+1} to {end+1}")
else:
    print("DprAttendancePanel NOT FOUND")

# EMPTY_ATT_ROW
emp = find("const EMPTY_ATT_ROW")
if emp != -1: show("EMPTY_ATT_ROW", emp, emp+5)

# useManpowerMaster loadAttendance
uh = find("function useManpowerMaster()")
if uh != -1:
    for j in range(uh,min(uh+120,len(lines))):
        if "loadAttendance" in lines[j] or "saveAttendance" in lines[j]:
            print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

print("\n=== DONE ===")
input("Press Enter...")
