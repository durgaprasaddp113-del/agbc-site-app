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

# 1. DailyReports component start - first 20 lines
dr = find("const DailyReports = ({")
print("### DailyReports start ###")
if dr != -1: show("DR start", dr, dr+20)

# 2. Full manpower section in form render
print("### Manpower section in DPR form ###")
if dr != -1:
    for j in range(dr, min(dr+700, len(lines))):
        if "MANPOWER section" in lines[j] or 'activeSection==="manpower"' in lines[j] or "DprAttendancePanel" in lines[j]:
            show("Manpower area", j, j+25)
            break

# 3. DprAttendancePanel component - first 15 lines
print("### DprAttendancePanel component ###")
dap = find("const DprAttendancePanel = (")
if dap != -1: show("DprAttendancePanel", dap, dap+15)
else: print("NOT FOUND!")

# 4. useManpowerMaster in DailyReports state
print("### useManpowerMaster in DailyReports ###")
if dr != -1:
    for j in range(dr, min(dr+20, len(lines))):
        if "useManpowerMaster" in lines[j] or "mpMasters" in lines[j] or "mpAttDprId" in lines[j]:
            print("L"+str(j+1)+": "+s(lines[j].rstrip()))

# 5. DailyReports case in App()
print("\n### DailyReports case in App ###")
for i,l in enumerate(lines):
    if 'case "reports"' in l:
        show("reports case", i, i+3)

# 6. subcontractors passed to DailyReports?
print("### subcontractors in DailyReports ###")
if dr != -1:
    l = lines[dr]
    print("Props line: "+s(l.rstrip())[:200])

print("\n=== DONE ===")
input("Press Enter...")
