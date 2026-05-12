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

print("Lines:", len(lines))

dr = find("const DailyReports = ({")

# 1. handleSave full
print("\n### handleSave ###")
for j in range(dr,min(dr+400,len(lines))):
    if "handleSave = async" in lines[j]:
        show("handleSave", j, j+35)
        break

# 2. printData state
print("### printData state ###")
for i,l in enumerate(lines):
    if "printData" in l and "useState" in l:
        print(f"L{i+1}: {s(l.rstrip())[:100]}")

# 3. handlePrintDPR
print("\n### handlePrintDPR ###")
hp = find("handlePrintDPR = async")
if hp != -1: show("handlePrintDPR", hp, hp+10)
else: print("NOT FOUND")

# 4. attRowsRef
print("### attRowsRef ###")
for i,l in enumerate(lines):
    if "attRowsRef" in l:
        print(f"L{i+1}: {s(l.rstrip())[:100]}")

# 5. Print overlay in JSX
print("\n### Print overlay ###")
for i,l in enumerate(lines):
    if "dpr-print-overlay" in l or "printData.rpt" in l:
        print(f"L{i+1}: {s(l.rstrip())[:100]}")

# 6. DprAttendancePanel usage
print("\n### DprAttendancePanel usage ###")
show("panel usage", 3776, 3800)

# 7. Last build - check if deployed
print("\n### autoSave in handleSave ###")
for j in range(dr,min(dr+400,len(lines))):
    if "saveAttendance" in lines[j] and "attRows" in lines[j]:
        print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

# 8. useManpowerMaster loadData
print("\n### manpower_master loadData ###")
umm = find("function useManpowerMaster()")
if umm != -1:
    for j in range(umm,min(umm+30,len(lines))):
        if "select" in lines[j] or "setMasters" in lines[j]:
            print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

print("\n=== DONE ===")
input("Press Enter...")
