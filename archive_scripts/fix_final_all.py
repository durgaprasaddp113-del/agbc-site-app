import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

print("Lines:", len(lines))
changes = 0

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def find(t):
    for i,l in enumerate(lines): 
        if t in l: return i
    return -1

# ── SHOW CURRENT STATE ────────────────────────────────────────────────
print("\n── Save Attendance button ──")
for i,l in enumerate(lines):
    if "Save Attendance" in l and "button" in l:
        print(f"L{i+1}: {s(l.rstrip())[:120]}")

print("\n── window.open in handlePrintDPR ──")
hp = find("handlePrintDPR = async")
if hp != -1:
    for j in range(hp, min(hp+90, len(lines))):
        if "window.open" in lines[j] or "iframe" in lines[j]:
            print(f"L{j+1}: {s(lines[j].rstrip())[:100]}")

print("\n── onSaved in DprAttendancePanel usage ──")
for i,l in enumerate(lines):
    if "onSaved" in l:
        print(f"L{i+1}: {s(l.rstrip())[:120]}")

# ══════════════════════════════════════════════════════════════════════
# FIX A: Fix &#128190; HTML entity in Save Attendance button
# ══════════════════════════════════════════════════════════════════════
for i,l in enumerate(lines):
    if "&#128190;" in l and "Attendance" in l:
        lines[i] = l.replace("&#128190; Save Attendance", "Save Attendance")
        lines[i] = lines[i].replace("&#128190;Save Attendance", "Save Attendance")
        changes += 1
        print(f"\nFIX A: HTML entity removed from Save button at L{i+1}")
        break

# ══════════════════════════════════════════════════════════════════════
# FIX B: Replace window.open with hidden iframe in handlePrintDPR
# ══════════════════════════════════════════════════════════════════════
if hp != -1:
    for j in range(hp, min(hp+90, len(lines))):
        if "window.open(" in lines[j] and "_blank" in lines[j]:
            # Replace this line
            lines[j] = "        const _if = document.createElement('iframe');\n"
            # Build insert lines
            ins = [
                "        _if.style.cssText = 'position:fixed;top:-9999px;left:-9999px;width:0;height:0;border:0';\n",
                "        document.body.appendChild(_if);\n",
                "        _if.contentDocument.open();\n",
                "        _if.contentDocument.write(html);\n",
                "        _if.contentDocument.close();\n",
                "        setTimeout(function(){ _if.contentWindow.focus(); _if.contentWindow.print(); setTimeout(function(){ document.body.removeChild(_if); }, 2000); }, 400);\n",
            ]
            # Blank out old pw. lines
            k = j + 1
            while k < min(j+4, len(lines)):
                if "pw" in lines[k] or "pw." in lines[k]:
                    lines[k] = "\n"
                k += 1
            for idx, nl in enumerate(ins):
                lines.insert(j+1+idx, nl)
            changes += 1
            print(f"FIX B: iframe print at L{j+1}")
            break
    # Check if iframe already exists
    for j in range(hp, min(hp+90, len(lines))):
        if "_if" in lines[j] or "iframe" in lines[j]:
            print(f"INFO B: iframe already at L{j+1}")
            break

# ══════════════════════════════════════════════════════════════════════
# FIX C: onSaved handler — add onUpdate call to refresh list
# Find the onSaved line and update it to also call onUpdate
# ══════════════════════════════════════════════════════════════════════
dr = find("const DailyReports = ({")
for i,l in enumerate(lines):
    if "onSaved" in l and "setSel" in l and "manpowerTotal" in l:
        if "onUpdate" not in l:
            lines[i] = l.replace(
                "onSaved={(cnt) => setSel(p => p ? {...p, manpowerTotal: cnt} : p)}",
                "onSaved={(cnt) => { setSel(p => p ? {...p, manpowerTotal: cnt} : p); if(sel) onUpdate(sel.id,{pid:sel.pid,date:sel.date,reportNum:sel.reportNum,weather:sel.weather,temp:sel.temp,workHours:sel.workHours,manpower:sel.manpower||[],equipment:sel.equipment||[],activities:sel.activities||[],materials:sel.materials||[],inspections:sel.inspections||[],safety:sel.safety||[],manpowerTotal:cnt,issues:sel.issues,visitors:sel.visitors,remarks:sel.remarks,status:sel.status,preparedBy:sel.preparedBy}); }}"
            )
            changes += 1
            print(f"FIX C: onSaved now calls onUpdate to refresh list at L{i+1}")
        else:
            print(f"SKIP C: onUpdate already in onSaved")
        break

# If onSaved not found in usage, add it
panel_found = False
for i,l in enumerate(lines):
    if "onSaved" in l and "cnt" in l:
        panel_found = True
        break

if not panel_found:
    # Find DprAttendancePanel usage and add onSaved
    for i,l in enumerate(lines):
        if "<DprAttendancePanel" in l and "activeSection" in "".join(lines[max(0,i-2):i+1]):
            for j in range(i, min(i+15, len(lines))):
                ln = lines[j].rstrip()
                if ln.endswith("/>}") or ln.endswith("/>"):
                    new_line = lines[j].replace(
                        "/>}",
                        "\n        onSaved={(cnt) => { setSel(p => p ? {...p, manpowerTotal: cnt} : p); if(sel) onUpdate(sel.id,{pid:sel.pid,date:sel.date,reportNum:sel.reportNum,weather:sel.weather,temp:sel.temp,workHours:sel.workHours,manpower:sel.manpower||[],equipment:sel.equipment||[],activities:sel.activities||[],materials:sel.materials||[],inspections:sel.inspections||[],safety:sel.safety||[],manpowerTotal:cnt,issues:sel.issues,visitors:sel.visitors,remarks:sel.remarks,status:sel.status,preparedBy:sel.preparedBy});}}\n      />}"
                    )
                    if new_line != lines[j]:
                        lines[j] = new_line
                        changes += 1
                        print(f"FIX C2: onSaved added to panel usage at L{j+1}")
                    break
            break

# ══════════════════════════════════════════════════════════════════════
# FIX D: Hide old Manpower Summary section completely
# Wrap it in a <details> collapse so it's hidden by default
# ══════════════════════════════════════════════════════════════════════
for i,l in enumerate(lines):
    if ('title="Manpower Summary"' in l or 'title="Quick Summary' in l) and "SectionHead" in l:
        # Find the surrounding div block start
        for k in range(i-1, max(0,i-8), -1):
            if 'activeSection==="manpower"' in lines[k] and "<div" in lines[k]:
                # Replace the opening div with a collapsible details
                if "<details" not in lines[k]:
                    old = lines[k]
                    # Add a details wrapper around just the old section
                    lines[k] = lines[k].replace(
                        '<div className="bg-white rounded-xl border border-slate-200 overflow-x-auto">',
                        '<details className="bg-white rounded-xl border border-slate-200 overflow-x-auto"><summary className="px-4 py-2 text-xs text-slate-400 cursor-pointer select-none">Legacy summary (tap to expand)</summary>'
                    )
                    if lines[k] != old:
                        changes += 1
                        print(f"FIX D: Old manpower section wrapped in details at L{k+1}")
                break
        break

# ══════════════════════════════════════════════════════════════════════
# FIX E: "Manual Entry" label → show as "Direct Entry"
# In DprAttendancePanel category summary
# ══════════════════════════════════════════════════════════════════════
for i,l in enumerate(lines):
    if '"Manual Entry"' in l and "sid" in l:
        lines[i] = l.replace('"Manual Entry"', '"Direct Entry"')
        changes += 1
        print(f"FIX E: Manual Entry renamed to Direct Entry at L{i+1}")
        break

# ══════════════════════════════════════════════════════════════════════
# SAFETY CHECK AND WRITE
# ══════════════════════════════════════════════════════════════════════
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","saveAttendance","useManpowerMaster"]
failed = [c for c in checks if c not in out]
if failed:
    print("\nSAFETY FAIL:", failed, "— restoring")
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print(f"\nFile saved OK. Lines: {len(lines)}")

print(f"\nTOTAL FIXES: {changes}")
print()
print("RUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js && git commit -m "Fix: DPR print+count+emoji" && git push')
input("\nPress Enter...")
