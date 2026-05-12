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

dr = find("const DailyReports = ({")

# 1. View mode render - find manpower in view
print("### DPR VIEW MODE - manpower section ###")
for j in range(dr, min(dr+1000, len(lines))):
    l = lines[j]
    if 'mode==="view"' in l or "mode === \"view\"" in l:
        show("View mode start", j, j+5)
        break

# 2. Find the view render for manpower
for j in range(dr, min(dr+1000, len(lines))):
    l = lines[j]
    if "sel.manpower" in l and ("view" in lines[max(0,j-20):j+1] or True):
        show("sel.manpower in view", j, j+5)

# 3. Find attendance in view mode
print("### attendance / DprAttendancePanel in view ###")
for j in range(dr, min(dr+1200, len(lines))):
    l = lines[j]
    if "DprAttendancePanel" in l or "attendance" in l.lower() or "mpAttDprId" in l:
        print(f"L{j+1}: {s(l.rstrip())[:140]}")

# 4. saveAttendance full function
print("\n### saveAttendance function ###")
uh = find("function useManpowerMaster()")
if uh != -1:
    for j in range(uh, min(uh+200, len(lines))):
        if "saveAttendance" in lines[j] and "async" in lines[j]:
            show("saveAttendance", j, j+20)
            break

# 5. loadAttendance full function
print("### loadAttendance function ###")
if uh != -1:
    for j in range(uh, min(uh+200, len(lines))):
        if "loadAttendance" in lines[j] and "async" in lines[j]:
            show("loadAttendance", j, j+15)
            break

# 6. How DPR View renders sections
print("### DPR view render sections ###")
for j in range(dr, min(dr+1000, len(lines))):
    l = lines[j]
    if ("title:\"" in l or "title: \"" in l) and ("Manpower" in l or "manpower" in l.lower()):
        show("Manpower view section def", j, j+8)
        break

# 7. DPR view - full view block
print("### DPR view block start ###")
view_start = -1
for j in range(dr, min(dr+1000, len(lines))):
    if 'mode === "view"' in lines[j] or 'mode==="view"' in lines[j]:
        view_start = j
        show("View block", j, j+60)
        break

print("=== DONE ===")
input("Press Enter...")
