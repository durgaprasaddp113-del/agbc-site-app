import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# Show the full panel usage block (L3777 onwards)
print("── Panel usage block ──")
for j in range(3776, min(3800, len(lines))):
    print(f"L{j+1}: {s(lines[j].rstrip())}")
    if "/>" in lines[j] and j > 3777:
        break

# Find closing /> of panel usage starting at L3777
panel_start = 3776  # 0-based
close_line = -1
for j in range(panel_start, min(panel_start+20, len(lines))):
    stripped = lines[j].rstrip()
    if stripped.endswith("/>}") or stripped.endswith("/>") or stripped == "/>}" or stripped == "/>":
        close_line = j
        break

print(f"\nClose line: L{close_line+1}: {s(lines[close_line].rstrip()) if close_line!=-1 else 'NOT FOUND'}")

if close_line != -1:
    already = "onRowsChange" in "".join(lines[panel_start:close_line+1])
    if not already:
        old = lines[close_line].rstrip('\n')
        # Add onRowsChange before the closing />
        if old.rstrip().endswith("/>}"):
            lines[close_line] = old.rstrip().rstrip("/>}").rstrip() + "\n        onRowsChange={r=>{ attRowsRef.current=r; }}\n      />}\n"
        elif old.rstrip().endswith("/>"):
            lines[close_line] = old.rstrip().rstrip("/>").rstrip() + "\n        onRowsChange={r=>{ attRowsRef.current=r; }}\n      />\n"
        print(f"FIX: onRowsChange added at L{close_line+1}")
        print(f"New line: {s(lines[close_line].rstrip())[:120]}")
    else:
        print("SKIP: onRowsChange already present")

# Safety check
out = "".join(lines)
checks = ["const DailyReports","DprAttendancePanel","attRowsRef","saveAttendance"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL:", failed)
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("Saved OK")

print("\nRUN: set CI=false && npm run build")
input("Press Enter...")
