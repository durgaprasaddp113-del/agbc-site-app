APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def find(t):
    for i,l in enumerate(lines):
        if t in l: return i
    return -1

# Show useManpowerMaster loadData - how it maps data
umm = find("function useManpowerMaster()")
print("=== useManpowerMaster loadData map ===")
if umm != -1:
    for j in range(umm, min(umm+30,len(lines))):
        print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")
        if "return { masters" in lines[j]: break

# Show loadFromMaster function in DprAttendancePanel
print("\n=== loadFromMaster function ===")
dap = find("const DprAttendancePanel = (")
if dap != -1:
    for j in range(dap, min(dap+80,len(lines))):
        if "loadFromMaster" in lines[j] and "const" in lines[j]:
            for k in range(j, min(j+15,len(lines))):
                print(f"L{k+1}: {s(lines[k].rstrip())[:120]}")
            break

input("Press Enter...")
