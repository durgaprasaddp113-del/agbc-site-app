import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

content = "".join(lines)
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
changes = 0

# ── Show exact current saveAttendance and loadAttendance ──────────────
print("── CURRENT saveAttendance ──")
for i,l in enumerate(lines):
    if "saveAttendance" in l and "async" in l:
        for j in range(i, min(i+15,len(lines))):
            print(f"L{j+1}: {s(lines[j].rstrip())}")
        print()
        break

print("── CURRENT loadAttendance ──")
for i,l in enumerate(lines):
    if "loadAttendance" in l and "async" in l:
        for j in range(i, min(i+15,len(lines))):
            print(f"L{j+1}: {s(lines[j].rstrip())}")
        print()
        break

print("── CURRENT View mode end (issues/remarks lines) ──")
for i,l in enumerate(lines):
    if "sel.issues&&" in l and "Issues / Delays" in l:
        for j in range(max(0,i-2), min(i+4,len(lines))):
            print(f"L{j+1}: {s(lines[j].rstrip())}")
        print()
        break

# ── FIX 1: saveAttendance — line by line replacement ─────────────────
print("── APPLYING FIX 1: saveAttendance ──")
new_lines = list(lines)
i = 0
while i < len(new_lines):
    l = new_lines[i]
    # Find the saveAttendance function
    if "saveAttendance = async" in l and "dprId" in l:
        # Found start — now find the filter line
        for j in range(i, min(i+20, len(new_lines))):
            if "rows.filter(r => r.mpId)" in new_lines[j]:
                new_lines[j] = new_lines[j].replace(
                    "rows.filter(r => r.mpId)",
                    "rows.filter(r => r.name && r.name.trim())"
                )
                changes += 1
                print(f"  FIX 1a: filter fixed at L{j+1}")
            if "dpr_id: dprId," in new_lines[j] and "manpower_id" in new_lines[j]:
                # This is the insert map — add emp fields
                if "emp_name" not in new_lines[j]:
                    new_lines[j] = new_lines[j].replace(
                        "manpower_id: r.mpId || null,",
                        "manpower_id: r.mpId || null, employee_id: r.empId || \"\", emp_name: r.name || \"\", designation: r.designation || \"\","
                    )
                    changes += 1
                    print(f"  FIX 1b: emp fields added to insert at L{j+1}")
                break
        break
    i += 1

# ── FIX 2: loadAttendance — add empId/name/designation to return ─────
print("── APPLYING FIX 2: loadAttendance ──")
i = 0
while i < len(new_lines):
    l = new_lines[i]
    if "loadAttendance = async" in l and "dprId" in l:
        for j in range(i, min(i+20, len(new_lines))):
            if "mpId: a.manpower_id" in new_lines[j] and "emp_name" not in new_lines[j]:
                new_lines[j] = new_lines[j].replace(
                    "mpId: a.manpower_id || \"\",",
                    "mpId: a.manpower_id || \"\", empId: a.employee_id || \"\", name: a.emp_name || \"\", designation: a.designation || \"\","
                )
                changes += 1
                print(f"  FIX 2: empId/name/designation added at L{j+1}")
                break
        break
    i += 1

# ── FIX 3: View mode — insert DprAttendanceViewPanel before issues ────
print("── APPLYING FIX 3: View mode ──")
i = 0
while i < len(new_lines):
    l = new_lines[i]
    if "sel.issues&&" in l and "Issues / Delays" in l:
        VIEW_LINE = '            {/* Attendance Register */}\n            <DprAttendanceViewPanel dprId={sel.id} loadAttendance={loadAttendance} subcontractors={subcontractors}/>\n'
        new_lines.insert(i, VIEW_LINE)
        changes += 1
        print(f"  FIX 3: DprAttendanceViewPanel inserted before issues at L{i+1}")
        break
    i += 1

# ── WRITE ─────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

# ── VERIFY ────────────────────────────────────────────────────────────
print()
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    vl = f.readlines()

print("── VERIFY saveAttendance filter ──")
for i,l in enumerate(vl):
    if "saveAttendance = async" in l:
        for j in range(i,min(i+15,len(vl))):
            if "filter" in vl[j] or "emp_name" in vl[j]:
                print(f"L{j+1}: {s(vl[j].rstrip())[:120]}")

print()
print("── VERIFY loadAttendance ──")
for i,l in enumerate(vl):
    if "loadAttendance = async" in l:
        for j in range(i,min(i+12,len(vl))):
            if "mpId" in vl[j] or "emp_name" in vl[j] or "empId" in vl[j]:
                print(f"L{j+1}: {s(vl[j].rstrip())[:120]}")

print()
print("── VERIFY view mode attendance panel ──")
for i,l in enumerate(vl):
    if "DprAttendanceViewPanel" in l:
        print(f"L{i+1}: {s(l.rstrip())[:120]}")

print()
print("="*55)
print("TOTAL FIXES:", changes)
print()
print("NOW RUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js')
print('  git commit -m "Fix: DPR save all rows + view attendance + team"')
print('  git push')
print("="*55)
input("Press Enter...")
