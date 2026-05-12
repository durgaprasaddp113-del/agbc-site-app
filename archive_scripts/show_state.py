APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def find(t):
    for i,l in enumerate(lines):
        if t in l: return i
    return -1

# Show all key sections
dr = find("const DailyReports = ({")

print("1. printData/printRptId states:")
for i,l in enumerate(lines):
    if "printData" in l and "useState" in l: print("L"+str(i+1)+": "+s(l.rstrip()))
    if "printRptId" in l and "useState" in l: print("L"+str(i+1)+": "+s(l.rstrip()))

print("\n2. useEffect with printRptId:")
for i,l in enumerate(lines):
    if "useEffect" in l and ("printRptId" in l or "printData" in l) and "loadAttendance" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:120])

print("\n3. handlePrintDPR (first 6 lines):")
hp = find("const handlePrintDPR =")
if hp!=-1:
    for j in range(hp, min(hp+6,len(lines))):
        print("L"+str(j+1)+": "+s(lines[j].rstrip())[:120])

print("\n4. Manpower tab label (search for 'Manpower' near 'label'):")
if dr!=-1:
    for j in range(dr,min(dr+900,len(lines))):
        if "Manpower" in lines[j] and "label" in lines[j] and ('"manpower"' in lines[j] or "id:" in lines[j]):
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:160])
            break

print("\n5. DprAttendancePanel usage (show/hide):")
for i,l in enumerate(lines):
    if "DprAttendancePanel" in l and ("display" in l or "activeSection" in l):
        print("L"+str(i+1)+": "+s(l.rstrip())[:120])

print("\n6. Print modal in view:")
for i,l in enumerate(lines):
    if "setPrintData(null)" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:120])

input("\nPress Enter...")
