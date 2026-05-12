APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

# Find and remove duplicate DprAttendanceViewPanel line
# Keep the first one, remove the second
found = 0
new_lines = []
for i, l in enumerate(lines):
    if '<DprAttendanceViewPanel dprId={sel.id}' in l:
        found += 1
        if found == 2:
            print(f"REMOVED duplicate at L{i+1}")
            continue  # skip the duplicate
    new_lines.append(l)

with open(APP,"w",encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Done. Kept {found-1 if found>1 else found} instance(s)")
print("\nRun: set CI=false && npm run build")
input("Press Enter...")
