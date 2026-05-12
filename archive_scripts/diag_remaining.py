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

# 1. DPR list row - exact workers display
print("### 1. DPR list workers display ###")
for j in range(dr, min(dr+800, len(lines))):
    if "workers" in lines[j].lower() and ("manpower" in lines[j].lower() or "mp" in lines[j]):
        print(f"L{j+1}: {s(lines[j].rstrip())[:160]}")

# 2. handlePrintDPR - first 5 lines to confirm placement
print("\n### 2. handlePrintDPR location ###")
hp = find("handlePrintDPR = async")
if hp != -1:
    show("handlePrintDPR start", hp, hp+5)
else:
    print("NOT FOUND")

# 3. Print button exact line
print("### 3. Print button ###")
for i,l in enumerate(lines):
    if "Print DPR" in l and "button" in l:
        print(f"L{i+1}: {s(l.rstrip())[:120]}")

# 4. Old manpower summary section - exact location
print("\n### 4. Old manpower summary ###")
for j in range(dr, min(dr+900, len(lines))):
    if "Quick Summary" in lines[j] or ("Manpower Summary" in lines[j] and "SectionHead" in lines[j]):
        show("old mp summary", j, j+4)
        break

# 5. saveAttendance - does it update daily_reports?
print("### 5. saveAttendance update ###")
sa = find("saveAttendance = async")
if sa != -1:
    show("saveAttendance", sa, sa+18)

# 6. Load Master button label
print("### 6. Load Master button ###")
dap = find("const DprAttendancePanel = (")
if dap != -1:
    for j in range(dap, min(dap+150, len(lines))):
        if "Load" in lines[j] and ("button" in lines[j] or "Master" in lines[j]):
            print(f"L{j+1}: {s(lines[j].rstrip())[:140]}")

# 7. useDailyReports - loadData maps manpower_total
print("\n### 7. useDailyReports manpower_total ###")
udr = find("function useDailyReports()")
if udr != -1:
    for j in range(udr, min(udr+60, len(lines))):
        if "manpower" in lines[j].lower():
            print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

print("\n=== DONE ===")
input("Press Enter...")
