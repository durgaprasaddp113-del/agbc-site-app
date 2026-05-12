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
def find(t):
    for i,l in enumerate(lines): 
        if t in l: return i
    return -1

# ── STEP 1: Add attRowsRef after useManpowerMaster in DailyReports ───
# L3570: const { masters: mpMasters, loadAttendance, saveAttendance } = useManpowerMaster();
hook_line = find("const { masters: mpMasters, loadAttendance, saveAttendance } = useManpowerMaster();")
if hook_line != -1:
    if "attRowsRef" not in lines[hook_line+1]:
        lines.insert(hook_line+1, "  const attRowsRef = useRef([]);\n")
        changes += 1
        print(f"STEP 1: attRowsRef added at L{hook_line+2}")
else:
    print("WARN 1: useManpowerMaster line not found")

# ── STEP 2: Add onRowsChange prop to DprAttendancePanel signature ─────
dap = find("const DprAttendancePanel = ({")
if dap != -1:
    if "onRowsChange" not in lines[dap]:
        lines[dap] = lines[dap].replace(
            "onSaved })",
            "onSaved, onRowsChange })"
        ).replace(
            "showToast })",
            "showToast, onRowsChange })"
        )
        changes += 1
        print(f"STEP 2: onRowsChange added to DprAttendancePanel signature at L{dap+1}")

# ── STEP 3: Call onRowsChange when rows change inside DprAttendancePanel
# Add useEffect after the rows useState
dap2 = find("const DprAttendancePanel = ({")
if dap2 != -1:
    for j in range(dap2, min(dap2+15, len(lines))):
        if "const [rows, setRows]" in lines[j]:
            if "onRowsChange" not in "".join(lines[j:j+5]):
                lines.insert(j+1, "  useEffect(() => { if (onRowsChange) onRowsChange(rows); }, [rows]);\n")
                changes += 1
                print(f"STEP 3: rows sync useEffect added at L{j+2}")
            break

# ── STEP 4: Remove "Save Attendance" button from panel toolbar ─────────
# (attendance now auto-saves with DPR)
for i,l in enumerate(lines):
    if "Save Attendance" in l and "onClick={handleSave}" in l and "button" in l:
        lines[i] = ""
        changes += 1
        print(f"STEP 4: Save Attendance button removed at L{i+1}")
        break
# Also remove the wrapping conditional
for i,l in enumerate(lines):
    if "rows.length > 0" in l and "handleSave" in "".join(lines[i:i+4]):
        # Check it's the Save Attendance wrapper
        block = "".join(lines[i:i+4])
        if "Save Attendance" in block:
            for k in range(i, min(i+4, len(lines))):
                lines[k] = ""
            changes += 1
            print(f"STEP 4b: Save Attendance wrapper removed at L{i+1}")
            break

# ── STEP 5: Pass onRowsChange to DprAttendancePanel usage in form ──────
for i,l in enumerate(lines):
    if "<DprAttendancePanel" in l and "dprId={mpAttDprId" in l:
        for j in range(i, min(i+15, len(lines))):
            if "/>}" in lines[j] or (lines[j].strip().startswith("/>")):
                if "onRowsChange" not in "".join(lines[i:j+1]):
                    lines[j] = lines[j].replace("/>}", " onRowsChange={r => attRowsRef.current = r}/>}")
                    lines[j] = lines[j].replace("/>", " onRowsChange={r => attRowsRef.current = r}/>", 1) if "/>}" not in lines[j] else lines[j]
                    changes += 1
                    print(f"STEP 5: onRowsChange passed to panel at L{j+1}")
                break
        break

# ── STEP 6: Modify handleSave to auto-save attendance + update count ───
# Find: const res = sel ? await onUpdate(sel.id, payload) : await onAdd(payload);
for i,l in enumerate(lines):
    if "const res = sel ? await onUpdate(sel.id, payload) : await onAdd(payload);" in l:
        # Check context - inside DailyReports handleSave
        ctx = "".join(lines[max(0,i-30):i])
        if "manpowerTotal" in ctx and "payload" in ctx:
            # 1. Before this line, recalculate manpowerTotal from attRowsRef
            lines.insert(i, "    const attRows = attRowsRef.current || [];\n")
            lines.insert(i+1, "    const attPresent = attRows.filter(r => r.am===\"P\" || r.pm===\"P\").length;\n")
            lines.insert(i+2, "    payload.manpowerTotal = attPresent > 0 ? attPresent : totalMP;\n")
            # After res, save attendance
            # Find the setSaving(false) line after res
            for j in range(i+3, min(i+15, len(lines))):
                if "setSaving(false)" in lines[j]:
                    lines.insert(j+1, "    // Auto-save attendance with DPR\n")
                    lines.insert(j+2, "    const dprId = res.id || (sel && sel.id) || null;\n")
                    lines.insert(j+3, "    if (dprId && attRows.length > 0) { await saveAttendance(dprId, attRows); }\n")
                    changes += 1
                    print(f"STEP 6: Auto-save attendance added to handleSave at L{j+2}")
                    break
            changes += 1
            print(f"STEP 6a: manpowerTotal from attendance added at L{i+1}")
            break

# ── STEP 7: Remove old Manpower Summary section from form ─────────────
dr = find("const DailyReports = ({")
for i,l in enumerate(lines):
    if ("Manpower Summary" in l or "Quick Summary" in l) and "SectionHead" in l:
        # Find the surrounding conditional div and remove the whole block
        for k in range(i-1, max(0,i-8),-1):
            if 'activeSection==="manpower"' in lines[k] and "<div" in lines[k]:
                # Find the end of this div
                depth = 0
                for m in range(k, min(k+60, len(lines))):
                    depth += lines[m].count("{") - lines[m].count("}")
                    if depth <= 0 and m > k:
                        # Blank all lines from k to m
                        for n in range(k, m+1):
                            lines[n] = ""
                        changes += 1
                        print(f"STEP 7: Old Manpower Summary removed (L{k+1}-L{m+1})")
                        break
                break
        break

# ── SAFETY CHECK AND WRITE ────────────────────────────────────────────
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","saveAttendance","useManpowerMaster"]
failed = [c for c in checks if c not in out]
if failed:
    print("\nSAFETY FAIL:", failed)
    shutil.copy2(bk, APP)
    print("Restored backup")
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print(f"\nFile saved. Lines: {len([l for l in out.split(chr(10)) if l])}")

print(f"\nTOTAL CHANGES: {changes}")
print()
print("RUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js && git commit -m "Fix: DPR integrated save + auto attendance" && git push')
input("\nPress Enter...")
