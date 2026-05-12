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

# ══════════════════════════════════════════════════════════════════════
# FIX 1: Print CSS — add display:block to @media print for overlay
# Current: #dpr-print-overlay { display: none; }  ← no print override
# Fix: add display:block!important inside @media print block
# ══════════════════════════════════════════════════════════════════════
for i,l in enumerate(lines):
    if "#dpr-print-overlay { display: none; }" in l:
        lines[i] = l.replace(
            "#dpr-print-overlay { display: none; }",
            "#dpr-print-overlay { display: none; }"  # keep same
        )
        # Find the @media print block and add display:block to it
        # Look backwards for the visibility rule
        for k in range(i-1, max(0,i-10), -1):
            if "visibility: visible !important;" in lines[k] and "dpr-print-overlay" in lines[k]:
                # This line: #dpr-print-overlay, #dpr-print-overlay * { visibility: visible !important; }
                # Add display:block to the overlay rule
                lines[k] = lines[k].replace(
                    "#dpr-print-overlay, #dpr-print-overlay * { visibility: visible !important; }",
                    "#dpr-print-overlay { display: block !important; } #dpr-print-overlay, #dpr-print-overlay * { visibility: visible !important; }"
                )
                changes += 1
                print(f"FIX 1: display:block added to print CSS at L{k+1}")
                break
        break

# ══════════════════════════════════════════════════════════════════════
# FIX 2: Pre-load attendance into attRowsRef when opening edit
# Find openEdit in DailyReports and add loadAttendance call
# ══════════════════════════════════════════════════════════════════════
dr = find("const DailyReports = ({")
if dr != -1:
    for j in range(dr, min(dr+200, len(lines))):
        l = lines[j]
        # Find: const openEdit = rpt => { or const openEdit = (rpt) => {
        if "openEdit" in l and "=>" in l and "setSel" in "".join(lines[j:j+5]):
            # Check it's inside DailyReports (not another component)
            print(f"Found openEdit at L{j+1}: {s(l.rstrip())[:80]}")
            # Find where openEdit sets mode to "form"
            for k in range(j, min(j+15, len(lines))):
                if 'setMode("form")' in lines[k] or "setMode('form')" in lines[k]:
                    # Insert pre-load after this line
                    preload = '      loadAttendance((rpt&&rpt.id)||"").then(att => { if(att&&att.length) attRowsRef.current=att; });\n'
                    if "loadAttendance" not in "".join(lines[k:k+3]):
                        lines.insert(k+1, preload)
                        changes += 1
                        print(f"FIX 2: attendance pre-load added to openEdit at L{k+2}")
                    break
            break

# ══════════════════════════════════════════════════════════════════════
# FIX 3: Print timeout — increase from 300ms to 800ms for React render
# ══════════════════════════════════════════════════════════════════════
for i,l in enumerate(lines):
    if "setTimeout(() => window.print(), 300)" in l:
        lines[i] = l.replace("setTimeout(() => window.print(), 300)", "setTimeout(() => window.print(), 800)")
        changes += 1
        print(f"FIX 3: print timeout increased to 800ms at L{i+1}")
        break

# ══════════════════════════════════════════════════════════════════════
# FIX 4: The "Total Manpower" card in View mode — read from attendance
# L3651: const totalMP = (sel.manpower||[]).reduce(...)
# Change to also check sel.manpowerTotal which is updated in DB
# ══════════════════════════════════════════════════════════════════════
if dr != -1:
    for j in range(dr, min(dr+800, len(lines))):
        if "const totalMP = (sel.manpower||[]).reduce" in lines[j]:
            lines[j] = lines[j].replace(
                "const totalMP = (sel.manpower||[]).reduce((s,r)=>s+(Number(r.count)||0),0);",
                "const totalMP = sel.manpowerTotal || (sel.manpower||[]).reduce((s,r)=>s+(Number(r.count)||0),0);"
            )
            changes += 1
            print(f"FIX 4: View totalMP now uses manpowerTotal from DB at L{j+1}")
            break

# ══════════════════════════════════════════════════════════════════════
# FIX 5: List row manpower count — find mp variable
# ══════════════════════════════════════════════════════════════════════
if dr != -1:
    for j in range(dr, min(dr+1000, len(lines))):
        if "const mp=" in lines[j] or "const mp =" in lines[j]:
            if "manpower" in lines[j].lower() or "reduce" in lines[j]:
                print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")
        if "workers" in lines[j] and ("mp}" in lines[j] or "{mp}" in lines[j]):
            print(f"LIST ROW L{j+1}: {s(lines[j].rstrip())[:120]}")

# ══════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════
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

print(f"TOTAL CHANGES: {changes}")
print("\nRUN: set CI=false && npm run build")
input("\nPress Enter...")
