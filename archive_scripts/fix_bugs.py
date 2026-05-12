import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def find(t):
    for i,l in enumerate(lines): 
        if t in l: return i
    return -1

changes = 0

# ── BUG 1 FIX: useDailyReports.add — return the new DPR id ──────────
# Find: await supabase.from("daily_reports").insert([{
udr = find("function useDailyReports()")
if udr != -1:
    for j in range(udr, min(udr+80, len(lines))):
        # Find the insert line in the add function
        if ".insert([{" in lines[j] and "daily_reports" in "".join(lines[max(0,j-3):j+1]):
            # Check the line after insert for the error check
            for k in range(j, min(j+10, len(lines))):
                if "if (error) return" in lines[k] and "ok: false" in lines[k]:
                    # Next line should be: await loadData(); return { ok: true };
                    if k+1 < len(lines) and "return { ok: true }" in lines[k+1]:
                        old = lines[k+1]
                        # Change insert to use .select() and return id
                        # First fix the insert line to add .select()
                        if ".select()" not in lines[j] and ".select()" not in "".join(lines[j:k+1]):
                            # Add .select() - find the closing ]) of insert
                            for m in range(j, min(j+8, len(lines))):
                                if "])" in lines[m] and "insert" in "".join(lines[j:m+1]):
                                    lines[m] = lines[m].replace("])", "]).select('id')", 1)
                                    break
                            # Change the return to include id
                            lines[k] = lines[k].replace(
                                "if (error) return { ok: false, error: error.message };",
                                "if (error) return { ok: false, error: error.message };"
                            )
                            lines[k+1] = lines[k+1].replace(
                                "await loadData(); return { ok: true };",
                                "const newId = data?.[0]?.id || null; await loadData(); return { ok: true, id: newId, reportNum };"
                            )
                            # Also fix the insert destructure to include data
                            for m in range(j-3, j+1):
                                if "const { error }" in lines[m] and "insert" in "".join(lines[m:j+2]):
                                    lines[m] = lines[m].replace("const { error }", "const { data, error }")
                                    break
                            changes += 1
                            print(f"BUG1 FIX: useDailyReports.add now returns id at L{k+2}")
                    break
            break

# ── BUG 1b FIX: handleSave — fix order and use res.id correctly ──────
# Current L3619-3625:
# const res = ...
# setSaving(false);
# const _dprId = res.id || (sel && sel.id);   ← res.id was always undefined for new
# if (_dprId && ...) saveAttendance(...)
# if (!res.ok) { return; }   ← error check AFTER attendance save (wrong!)
dr = find("const DailyReports = ({")
for j in range(dr, min(dr+400, len(lines))):
    if "const _dprId = res.id || (sel && sel.id);" in lines[j]:
        # Fix: also check res.dprId which might be set
        lines[j] = lines[j].replace(
            "const _dprId = res.id || (sel && sel.id);",
            "if (!res.ok) { showToast(res.error||\"Save failed\",\"error\"); setSaving(false); return; }\n    const _dprId = res.id || (sel && sel.id);"
        )
        changes += 1
        print(f"BUG1b FIX: error check moved before attendance save at L{j+1}")
        break

# Remove the duplicate if (!res.ok) that now comes after
for j in range(dr, min(dr+400, len(lines))):
    if 'if (!res.ok) { showToast(res.error||"Save failed","error"); return; }' in lines[j]:
        # Check if there's already an error check above it
        ctx = "".join(lines[max(0,j-5):j])
        if "if (!res.ok)" in ctx:
            lines[j] = "    // error already checked above\n"
            changes += 1
            print(f"BUG1c FIX: duplicate error check removed at L{j+1}")
            break

# ── BUG 2 FIX: Print CSS — use visibility instead of display ─────────
for i,l in enumerate(lines):
    if "body > * { display: none !important; }" in l:
        lines[i] = l.replace(
            "body > * { display: none !important; }\n",
            "* { visibility: hidden !important; }\n"
        )
        changes += 1
        print(f"BUG2a FIX: print CSS changed to visibility at L{i+1}")
        break

for i,l in enumerate(lines):
    if "dpr-print-overlay { display: block !important; }" in l:
        lines[i] = l.replace(
            "#dpr-print-overlay { display: block !important; }",
            "#dpr-print-overlay, #dpr-print-overlay * { visibility: visible !important; } #dpr-print-overlay { position:fixed;top:0;left:0;width:100%;background:white; }"
        )
        changes += 1
        print(f"BUG2b FIX: print overlay visibility fixed at L{i+1}")
        break

# ── BUG 3 FIX: Load Master — add debug toast if masters is empty ─────
dap = find("const DprAttendancePanel = ({")
if dap != -1:
    for j in range(dap, min(dap+60, len(lines))):
        if "loadFromMaster" in lines[j] and "const loadFromMaster" in lines[j]:
            # Find the no active employees toast
            for k in range(j, min(j+10, len(lines))):
                if "No active employees" in lines[k]:
                    lines[k] = lines[k].replace(
                        'showToast("No active employees for this subcontractor","error")',
                        'showToast("No active employees for this subcontractor. Add employees in Manpower Master module first.","error")'
                    )
                    changes += 1
                    print(f"BUG3 FIX: better error message for empty master at L{k+1}")
                    break
            break

# ── SAFETY CHECK AND WRITE ────────────────────────────────────────────
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","attRowsRef","printData"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL:", failed)
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print(f"\nSaved OK. Lines: {len(lines)}")

print(f"\nTOTAL CHANGES: {changes}")
print("\nRUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js && git commit -m "Fix: DPR new-record attendance + print CSS" && git push')
input("\nPress Enter...")
