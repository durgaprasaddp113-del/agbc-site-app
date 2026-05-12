APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# Find exact Edit Report button line
print("Searching for edit button variants...")
for i,l in enumerate(lines):
    if "openEdit(sel)" in l and ("Edit" in l or "edit" in l):
        print(f"L{i+1}: {s(l.rstrip())[:120]}")

print("\nSearching for view mode buttons block...")
dr = next((i for i,l in enumerate(lines) if "const DailyReports = ({" in l), -1)
if dr != -1:
    for j in range(dr+400, min(dr+1600, len(lines))):
        if "flex flex-wrap gap-3" in lines[j]:
            for k in range(j, min(j+8, len(lines))):
                print(f"L{k+1}: {s(lines[k].rstrip())[:120]}")
            print()

input("Press Enter...")
