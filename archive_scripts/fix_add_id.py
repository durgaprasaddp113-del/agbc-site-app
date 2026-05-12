import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# Show current useDailyReports add function
print("── Current useDailyReports add function ──")
udr = next((i for i,l in enumerate(lines) if "function useDailyReports()" in l), -1)
if udr != -1:
    for j in range(udr, min(udr+100, len(lines))):
        if "const add = async" in lines[j] or (j > udr+5 and "insert" in lines[j] and "daily_reports" in "".join(lines[max(0,j-3):j+1])):
            for k in range(j, min(j+20, len(lines))):
                print(f"L{k+1}: {s(lines[k].rstrip())[:120]}")
                if "return { ok: true" in lines[k]: break
            break

changes = 0

# Find the add function inside useDailyReports
if udr != -1:
    add_start = -1
    for j in range(udr, min(udr+100, len(lines))):
        if "const add = async" in lines[j]:
            add_start = j; break

    if add_start != -1:
        # Find the insert line
        for j in range(add_start, min(add_start+20, len(lines))):
            if ".insert([{" in lines[j]:
                # Add .select() to get the inserted ID
                if ".select(" not in lines[j]:
                    # The insert might span multiple lines - find the closing ]);
                    for k in range(j, min(j+10, len(lines))):
                        if "]);" in lines[k] or "]);}" in lines[k]:
                            lines[k] = lines[k].replace("]);", "]).select('id');")
                            lines[k] = lines[k].replace("]).select('id');}", "]).select('id')}")
                            print(f"FIX: .select('id') added to insert at L{k+1}")
                            changes += 1
                            break
                # Also fix const { error } to const { data, error }
                for k in range(max(0,j-5), j+3):
                    if "const { error }" in lines[k] and "insert" in "".join(lines[k:j+2]):
                        lines[k] = lines[k].replace("const { error }", "const { data, error }")
                        print(f"FIX: destructure data added at L{k+1}")
                        changes += 1
                        break
                # Fix return to include id
                for k in range(j, min(j+12, len(lines))):
                    if "return { ok: true" in lines[k] and "id:" not in lines[k]:
                        old = lines[k]
                        # Get reportNum var
                        lines[k] = lines[k].replace(
                            "return { ok: true };",
                            "const newId = (data && data[0]) ? data[0].id : null; return { ok: true, id: newId };"
                        ).replace(
                            "return { ok: true, reportNum };",
                            "const newId = (data && data[0]) ? data[0].id : null; return { ok: true, id: newId, reportNum };"
                        )
                        if lines[k] != old:
                            print(f"FIX: return now includes id at L{k+1}")
                            changes += 1
                        break
                break

# Also fix handleSave to properly get dprId for new records
# The BUG1b fix already moved error check. Now fix _dprId fallback
dr = next((i for i,l in enumerate(lines) if "const DailyReports = ({" in l), -1)
if dr != -1:
    for j in range(dr, min(dr+400, len(lines))):
        if "const _dprId = res.id || (sel && sel.id);" in lines[j]:
            lines[j] = lines[j].replace(
                "const _dprId = res.id || (sel && sel.id);",
                "const _dprId = res.id || res.dprId || (sel && sel.id);"
            )
            print(f"FIX: _dprId now checks res.dprId too at L{j+1}")
            changes += 1
            break

# Show updated add function
print("\n── Updated add function ──")
if udr != -1:
    for j in range(udr, min(udr+100, len(lines))):
        if "const add = async" in lines[j]:
            for k in range(j, min(j+20, len(lines))):
                print(f"L{k+1}: {s(lines[k].rstrip())[:120]}")
                if "return { ok:" in lines[k]: break
            break

# Safety + write
out = "".join(lines)
checks = ["const DailyReports","DprAttendancePanel","attRowsRef","printData"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL:", failed)
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print(f"\nSaved. Lines: {len(lines)}, Changes: {changes}")

print("\nRUN: set CI=false && npm run build")
input("Press Enter...")
