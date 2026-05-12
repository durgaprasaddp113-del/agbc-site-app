APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def find(t):
    for i,l in enumerate(lines): 
        if t in l: return i
    return -1

# Find ALL occurrences of key functions
print("useManpowerMaster occurrences:")
for i,l in enumerate(lines):
    if "function useManpowerMaster()" in l:
        print("  L"+str(i+1))

print("ManpowerMaster component occurrences:")
for i,l in enumerate(lines):
    if "const ManpowerMaster = (" in l:
        print("  L"+str(i+1))

print("DprAttendancePanel occurrences:")
for i,l in enumerate(lines):
    if "const DprAttendancePanel = (" in l:
        print("  L"+str(i+1))

print("EMPTY_MP occurrences:")
for i,l in enumerate(lines):
    if "const EMPTY_MP" in l:
        print("  L"+str(i+1)+": "+l.rstrip()[:80])

print("MP_TRADES occurrences:")
for i,l in enumerate(lines):
    if "const MP_TRADES" in l:
        print("  L"+str(i+1))

input("Press Enter...")
