import sys
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

print("Total lines:", len(lines))

# 1. DPR list - manpower count display
print("\n### 1. DPR LIST manpower count ###")
dr = find("const DailyReports = ({")
for j in range(dr, min(dr+700,len(lines))):
    if "workers" in lines[j] and ("mp=" in lines[j] or "manpowerTotal" in lines[j] or "0 workers" in lines[j] or ".length" in lines[j]):
        if "<td" in lines[j] or "className" in lines[j]:
            print(f"L{j+1}: {s(lines[j].rstrip())[:140]}")

# 2. DPR save - manpowerTotal calculation
print("\n### 2. totalMP calculation ###")
for j in range(dr, min(dr+300,len(lines))):
    if "totalMP" in lines[j] or "manpowerTotal" in lines[j]:
        print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

# 3. saveAttendance - does it update daily_reports?
print("\n### 3. saveAttendance function ###")
sa = find("saveAttendance = async")
if sa != -1: show("saveAttendance", sa, sa+20)

# 4. DprAttendancePanel toolbar
print("### 4. DprAttendancePanel toolbar buttons ###")
dap = find("const DprAttendancePanel = (")
if dap != -1:
    for j in range(dap, min(dap+120,len(lines))):
        if "Load" in lines[j] or "Copy" in lines[j] or "Save" in lines[j] or "Master" in lines[j]:
            print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

# 5. DPR view mode - action buttons
print("\n### 5. DPR VIEW action buttons ###")
view_start = -1
for j in range(dr, min(dr+1500,len(lines))):
    if 'mode==="view"' in lines[j] or "mode === \"view\"" in lines[j]:
        view_start = j; break
if view_start != -1:
    for j in range(view_start, min(view_start+400,len(lines))):
        if ("openEdit" in lines[j] or "Edit" in lines[j]) and ("Btn" in lines[j] or "button" in lines[j]) and "label" in lines[j].lower():
            show("view buttons", max(0,j-2), j+3)
            break

# 6. useDailyReports - add function (what goes to DB)
print("### 6. useDailyReports add fn ###")
udr = find("function useDailyReports()")
if udr != -1:
    for j in range(udr,min(udr+80,len(lines))):
        if "manpower_total" in lines[j]:
            print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

# 7. handlePrintDPR exists?
print("\n### 7. handlePrintDPR exists? ###")
hp = find("handlePrintDPR")
print("handlePrintDPR found at L"+str(hp+1) if hp != -1 else "NOT FOUND")

# 8. DprAttendanceViewPanel in view mode?
print("\n### 8. DprAttendanceViewPanel in view ###")
for i,l in enumerate(lines):
    if "DprAttendanceViewPanel" in l:
        print(f"L{i+1}: {s(l.rstrip())[:120]}")

# 9. manpowerTotal in form
print("\n### 9. form manpowerTotal ###")
for j in range(dr, min(dr+400,len(lines))):
    if "totalMP" in lines[j]:
        print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

print("\n=== DONE ===")
input("Press Enter...")
