import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
changes = 0

# ── FIX 1: L3677 broken Manpower label (0-based: 3676) ──────────────
print("Before L3677: "+s(lines[3676].rstrip()))
lines[3676] = '      {id:"manpower",label:`\U0001f9cd Manpower (${(attRowsRef.current||[]).length})`},\n'
changes += 1
print("After  L3677: "+s(lines[3676].rstrip())[:80])

# ── FIX 2: Remove duplicate useEffect (L3590-3596 area, 0-based 3589+) ─
# L3584-3589 is the good one. L3590+ is duplicate. Remove it.
print("\nRemoving duplicate useEffect...")
# Find and remove the second useEffect block for printRptId
dup_start = -1
dup_end = -1
for i in range(3589, min(3605, len(lines))):
    if "useEffect" in lines[i] and "printRptId" in lines[i]:
        dup_start = i
        depth = 0
        for j in range(i, min(i+10, len(lines))):
            depth += lines[j].count('{') - lines[j].count('}')
            if depth <= 0 and j > i:
                dup_end = j
                break
        break

if dup_start != -1 and dup_end != -1:
    print("Removing duplicate useEffect L"+str(dup_start+1)+"-"+str(dup_end+1))
    for i in range(dup_start, dup_end+1):
        lines[i] = ""
    changes += 1
    print("FIX 2: Duplicate useEffect removed")

# ── FIX 3: L4044 empty line between setPrintData and }; ─────────────
# L4044 (0-based 4043) is just "\n" - leave it, it's fine

# ── FIX 4: Print modal - check if it renders printData.att ──────────
# Check around L3808 for the modal content
print("\nLines around print modal L3800-3820:")
for j in range(3799, min(3825, len(lines))):
    print(str(j+1)+"\t"+s(lines[j].rstrip())[:100])

# WRITE
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","printRptId"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL: "+str(failed))
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("\nSaved OK")

print("CHANGES: "+str(changes))
print("RUN: set CI=false && npm run build && npx vercel --prod --force")
input("\nPress Enter...")
