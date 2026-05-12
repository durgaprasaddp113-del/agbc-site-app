import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

print("Lines:", len(lines))
changes = 0

def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# ── Find exact line numbers ───────────────────────────────────────────
hook_line = -1   # useManpowerMaster in DailyReports
totalmp_line = -1 # const totalMP = form.manpower.reduce
mptotal_line = -1 # manpowerTotal: totalMP
res_line = -1    # const res = sel ? await onUpdate
saving_line = -1 # setSaving(false) — AFTER res_line
dap_line = -1    # const DprAttendancePanel = ({
rows_line = -1   # const [rows, setRows]
panel_close = -1 # closing /> of DprAttendancePanel usage in form

dr = -1
for i,l in enumerate(lines):
    if "const DailyReports = ({" in l: dr = i
    if "const { masters: mpMasters, loadAttendance, saveAttendance } = useManpowerMaster();" in l:
        hook_line = i
    if "const DprAttendancePanel = ({" in l: dap_line = i
    if "const [rows, setRows]" in l and dap_line != -1 and i < dap_line+10:
        rows_line = i

# Find handleSave items (inside DailyReports only)
if dr != -1:
    for i in range(dr, min(dr+700, len(lines))):
        l = lines[i]
        if "form.manpower.reduce" in l and "totalMP" in l: totalmp_line = i
        if "manpowerTotal: totalMP" in l and mptotal_line == -1: mptotal_line = i
        if "const res = sel ? await onUpdate(sel.id, payload) : await onAdd(payload);" in l:
            res_line = i
        if "setSaving(false)" in l and res_line != -1 and saving_line == -1:
            saving_line = i

print(f"hook_line={hook_line+1}, totalmp={totalmp_line+1}, mptotal={mptotal_line+1}")
print(f"res_line={res_line+1}, saving={saving_line+1}")
print(f"dap_line={dap_line+1}, rows_line={rows_line+1}")

# ── CHANGE 1: Add attRowsRef after hook_line ──────────────────────────
if hook_line != -1 and "attRowsRef" not in lines[hook_line+1]:
    lines.insert(hook_line+1, "  const attRowsRef = useRef([]);\n")
    # Adjust all subsequent line numbers
    if totalmp_line > hook_line: totalmp_line += 1
    if mptotal_line > hook_line: mptotal_line += 1
    if res_line > hook_line: res_line += 1
    if saving_line > hook_line: saving_line += 1
    changes += 1
    print(f"CHANGE 1: attRowsRef added at L{hook_line+2}")

# ── CHANGE 2: Update manpowerTotal to use attendance count ────────────
if mptotal_line != -1:
    old = lines[mptotal_line]
    if "attRows" not in old:
        lines[mptotal_line] = old.replace(
            "manpowerTotal: totalMP,",
            "manpowerTotal: (attRowsRef.current||[]).filter(r=>r.am===\"P\"||r.pm===\"P\").length || totalMP,"
        )
        changes += 1
        print(f"CHANGE 2: manpowerTotal now uses attendance at L{mptotal_line+1}")

# ── CHANGE 3: Auto-save attendance after setSaving(false) ─────────────
if saving_line != -1 and res_line != -1:
    # Insert after setSaving(false)
    insert_pos = saving_line + 1
    if "saveAttendance" not in lines[insert_pos]:
        auto_save = (
            "    // Auto-save attendance with DPR\n"
            "    const _dprId = res.id || (sel && sel.id);\n"
            "    const _attRows = attRowsRef.current || [];\n"
            "    if (_dprId && _attRows.length > 0) { saveAttendance(_dprId, _attRows).catch(()=>{}); }\n"
        )
        for k, ln in enumerate(auto_save.split('\n')):
            if ln:
                lines.insert(insert_pos + k, ln + '\n')
        changes += 1
        print(f"CHANGE 3: Auto-save attendance added after setSaving at L{insert_pos+1}")

# ── CHANGE 4: Add onRowsChange to DprAttendancePanel props ───────────
if dap_line != -1 and "onRowsChange" not in lines[dap_line]:
    lines[dap_line] = lines[dap_line].replace(
        "showToast, allRe",  "onRowsChange, showToast, allRe"
    ).replace(
        "showToast })",  "onRowsChange, showToast })"
    )
    # Fallback
    if "onRowsChange" not in lines[dap_line]:
        lines[dap_line] = lines[dap_line].replace(
            "showToast,", "onRowsChange, showToast,"
        )
    changes += 1
    print(f"CHANGE 4: onRowsChange prop added to DprAttendancePanel at L{dap_line+1}")

# ── CHANGE 5: Add useEffect to sync rows in DprAttendancePanel ────────
if rows_line != -1 and "onRowsChange" not in "".join(lines[rows_line:rows_line+4]):
    lines.insert(rows_line + 1,
        "  useEffect(() => { if (typeof onRowsChange === 'function') onRowsChange(rows); }, [rows]);\n"
    )
    changes += 1
    print(f"CHANGE 5: rows sync useEffect added at L{rows_line+2}")

# ── CHANGE 6: Pass onRowsChange in DprAttendancePanel usage ──────────
found_usage = False
for i,l in enumerate(lines):
    if "<DprAttendancePanel" in l and "dprId={mpAttDprId" in l:
        for j in range(i, min(i+15, len(lines))):
            stripped = lines[j].rstrip()
            if (stripped.endswith("/>}") or stripped.endswith("/>")) and "onRowsChange" not in "".join(lines[i:j+1]):
                lines[j] = lines[j].replace(
                    "/>}", " onRowsChange={r=>{ attRowsRef.current=r; }}/>}"
                )
                if "onRowsChange" not in lines[j]:
                    lines[j] = lines[j].replace(
                        "/>", " onRowsChange={r=>{ attRowsRef.current=r; }}/>"
                    )
                changes += 1
                print(f"CHANGE 6: onRowsChange passed to panel at L{j+1}")
                found_usage = True
                break
        break

if not found_usage:
    print("WARN 6: Could not pass onRowsChange to panel")

# ── CHANGE 7: Hide old Manpower Summary with style instead of removing
for i,l in enumerate(lines):
    if ("Manpower Summary" in l or "Quick Summary" in l) and "SectionHead" in l:
        # Find enclosing activeSection div and add display:none
        for k in range(i-1, max(0,i-8),-1):
            if 'activeSection==="manpower"' in lines[k] and "<div" in lines[k]:
                if 'display' not in lines[k]:
                    lines[k] = lines[k].replace(
                        '<div className="bg-white rounded-xl',
                        '<div style={{display:"none"}} className="bg-white rounded-xl'
                    )
                    changes += 1
                    print(f"CHANGE 7: Old manpower summary hidden at L{k+1}")
                break
        break

# ── CHANGE 8: Fix &#128190; HTML entity ──────────────────────────────
for i,l in enumerate(lines):
    if "&#128190;" in l:
        lines[i] = l.replace("&#128190; Save Attendance","Save Attendance").replace("&#128190;","")
        changes += 1
        print(f"CHANGE 8: HTML entity removed at L{i+1}")

# ── SAFETY CHECK AND WRITE ────────────────────────────────────────────
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","saveAttendance","attRowsRef"]
failed = [c for c in checks if c not in out]
if failed:
    print("\nSAFETY FAIL:", failed)
    shutil.copy2(bk, APP)
    print("Backup restored")
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print(f"\nFile saved. Lines: {len(lines)}")

print(f"\nTOTAL CHANGES: {changes}")
print("\nRUN: set CI=false && npm run build")
input("\nPress Enter...")
