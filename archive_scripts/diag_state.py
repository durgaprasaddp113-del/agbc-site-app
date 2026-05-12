APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def find(t):
    for i,l in enumerate(lines): 
        if t in l: return i
    return -1

print("Total lines:", len(lines))

# 1. handleSave in DailyReports
print("\n### handleSave ###")
dr = find("const DailyReports = ({")
for j in range(dr, min(dr+400, len(lines))):
    if "handleSave = async" in lines[j] or "const handleSave" in lines[j]:
        for k in range(j, min(j+30, len(lines))):
            print(f"L{k+1}: {s(lines[k].rstrip())[:120]}")
        break

# 2. DprAttendancePanel - what state does it expose?
print("\n### DprAttendancePanel state (rows) ###")
dap = find("const DprAttendancePanel = (")
if dap != -1:
    for j in range(dap, min(dap+5, len(lines))):
        print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

# 3. window.open or iframe in handlePrintDPR
print("\n### print method ###")
hp = find("handlePrintDPR = async")
if hp != -1:
    for j in range(hp, min(hp+90, len(lines))):
        if "window.open" in lines[j] or "_if" in lines[j] or "_pf" in lines[j] or "iframe" in lines[j]:
            print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")
            break

# 4. Old manpower summary - still there?
print("\n### Old manpower summary ###")
for j in range(dr, min(dr+900, len(lines))):
    if ("Manpower Summary" in lines[j] or "Quick Summary" in lines[j]) and "SectionHead" in lines[j]:
        print(f"L{j+1}: {s(lines[j].rstrip())[:100]}")
        break

# 5. Print button in view
print("\n### Print button ###")
for i,l in enumerate(lines):
    if "Print DPR" in l and "button" in l:
        print(f"L{i+1}: {s(l.rstrip())[:120]}")

# 6. useManpowerMaster in DailyReports
print("\n### attendance hook in DailyReports ###")
for j in range(dr, min(dr+30, len(lines))):
    if "useManpowerMaster" in lines[j] or "loadAttendance" in lines[j] or "saveAttendance" in lines[j]:
        print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

print("\n=== DONE ===")
input("Press Enter...")
