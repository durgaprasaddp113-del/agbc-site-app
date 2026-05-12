import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def find(t):
    for i,l in enumerate(lines): 
        if t in l: return i
    return -1

changes = 0

# ── Show current window.open and DprAttendancePanel usage ────────────
print("── Searching for window.open in handlePrintDPR ──")
hp = find("handlePrintDPR = async")
if hp != -1:
    for j in range(hp, min(hp+90, len(lines))):
        if "window.open" in lines[j] or "pw." in lines[j] or "pw)" in lines[j]:
            print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

print("\n── Searching for DprAttendancePanel usage ──")
for i,l in enumerate(lines):
    if "DprAttendancePanel" in l and ("dprId" in l or "onSaved" in l or "/>" in l):
        print(f"L{i+1}: {s(l.rstrip())[:120]}")

# ── FIX 1: Replace window.open with iframe ───────────────────────────
if hp != -1:
    for j in range(hp, min(hp+90, len(lines))):
        if "window.open(" in lines[j]:
            # Replace the window.open line and any following pw. lines
            lines[j] = "        const _pf = document.createElement('iframe');\n"
            insert_after = [
                "        _pf.style.cssText = 'position:fixed;top:-9999px;left:-9999px;width:0;height:0;border:0';\n",
                "        document.body.appendChild(_pf);\n",
                "        _pf.contentDocument.open();\n",
                "        _pf.contentDocument.write(html);\n",
                "        _pf.contentDocument.close();\n",
                "        setTimeout(function(){ _pf.contentWindow.focus(); _pf.contentWindow.print(); setTimeout(function(){ document.body.removeChild(_pf); }, 2000); }, 400);\n",
            ]
            # Remove following pw.document lines
            k = j + 1
            while k < len(lines) and ("pw." in lines[k] or "pw )" in lines[k] or (lines[k].strip().startswith("if (pw)") or lines[k].strip().startswith("if(pw)"))):
                lines[k] = "\n"
                k += 1
            for idx, nl in enumerate(insert_after):
                lines.insert(j+1+idx, nl)
            changes += 1
            print(f"\nFIX 1: iframe print inserted at L{j+1}")
            break

# ── FIX 2c: Add onSaved to DprAttendancePanel usage ─────────────────
# Find the panel usage block (multi-line)
panel_start = -1
for i,l in enumerate(lines):
    if "<DprAttendancePanel" in l and "activeSection" in "".join(lines[max(0,i-2):i+1]):
        panel_start = i
        break

if panel_start != -1:
    # Find the closing /> of this panel usage
    for j in range(panel_start, min(panel_start+15, len(lines))):
        if "/>}" in lines[j] or (lines[j].strip() == "/>}" ) or "/>" in lines[j]:
            if "onSaved" not in "".join(lines[panel_start:j+1]):
                old = lines[j]
                lines[j] = old.replace(
                    "/>",
                    "\n        onSaved={(cnt) => setSel(p => p ? {...p, manpowerTotal: cnt} : p)}\n      />"
                )
                changes += 1
                print(f"FIX 2c: onSaved added to DprAttendancePanel at L{j+1}")
            else:
                print(f"SKIP 2c: onSaved already exists")
            break

# ── Safety check and write ───────────────────────────────────────────
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","saveAttendance"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL:", failed, "— restoring")
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print(f"\nSaved. Lines: {len(lines)}")

print(f"TOTAL FIXES: {changes}")
print("\nRUN: set CI=false && npm run build")
input("Press Enter...")
