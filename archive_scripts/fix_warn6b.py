APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# Find all DprAttendancePanel occurrences
print("── All DprAttendancePanel lines ──")
for i,l in enumerate(lines):
    if "DprAttendancePanel" in l:
        print(f"L{i+1}: {s(l.rstrip())[:120]}")

print()

# Find the usage block by looking for dprId={mpAttDprId
print("── Lines with mpAttDprId ──")
for i,l in enumerate(lines):
    if "mpAttDprId" in l:
        print(f"L{i+1}: {s(l.rstrip())[:120]}")

input("\nPress Enter...")
