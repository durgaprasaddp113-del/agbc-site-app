APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def show(l,a,b):
    print("=== "+l+" ===")
    for i in range(a,min(b,len(lines))):
        print(str(i+1)+"\t"+s(lines[i].rstrip()))
    print()
def find(t):
    for i,l in enumerate(lines):
        if t in l: return i
    return -1

dr = find("const DailyReports = ({")

# 1. DPR list row - how manpower count is shown
print("### DPR LIST ROW - manpower column ###")
for j in range(dr, min(dr+600,len(lines))):
    if "workers" in lines[j] and ("mp=" in lines[j] or "manpowerTotal" in lines[j] or "totalMP" in lines[j]):
        show("list row mp", j, j+4)
        break

# 2. Save DPR - how manpowerTotal is calculated
print("### handleSave - manpowerTotal ###")
for j in range(dr, min(dr+300,len(lines))):
    if "manpowerTotal" in lines[j]:
        show("manpowerTotal", j, j+5)
        break

# 3. Save button emoji issue
print("### Save Attendance button ###")
att = find("const DprAttendancePanel = (")
if att != -1:
    for j in range(att, min(att+200,len(lines))):
        if "Save Attendance" in lines[j] or "128190" in lines[j]:
            print(f"L{j+1}: {s(lines[j].rstrip())[:160]}")

# 4. Old manpower summary section
print("\n### Old Manpower Summary section ###")
for j in range(dr, min(dr+700,len(lines))):
    if "Manpower Summary" in lines[j]:
        show("manpower summary", j, j+5)
        break

# 5. DPR add/update functions - what goes to DB
print("### useDailyReports add function ###")
udr = find("function useDailyReports()")
if udr != -1:
    for j in range(udr, min(udr+80,len(lines))):
        if "manpower_total" in lines[j] or "manpowerTotal" in lines[j]:
            print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

# 6. useManpowerMaster return
print("\n### useManpowerMaster return ###")
umm = find("function useManpowerMaster()")
if umm != -1:
    for j in range(umm,min(umm+200,len(lines))):
        if "return {" in lines[j] and j > umm+5:
            show("useManpowerMaster return", j, j+5)
            break

# 7. DailyReports passes subcontractors?
print("### DailyReports component signature ###")
show("DR signature", dr, dr+3)

# 8. View mode - print button exists?
print("### View mode action buttons ###")
for j in range(dr, min(dr+1200,len(lines))):
    if "flex flex-wrap gap-3" in lines[j] and j > dr+500:
        show("action buttons", j, j+10)
        break

print("=== DONE ===")
input("Press Enter...")
