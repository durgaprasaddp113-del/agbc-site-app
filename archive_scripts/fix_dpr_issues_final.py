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

# ================================================================
# FIX 1: PRINT - Replace window.open with hidden iframe (no popup blocker)
# Find: const pw = window.open(... in handlePrintDPR
# Replace with iframe-based print
# ================================================================
hp = find("handlePrintDPR = async")
if hp != -1:
    for j in range(hp, min(hp+80, len(lines))):
        if "window.open" in lines[j] and "pw" in lines[j]:
            old_open = lines[j]
            next_line = lines[j+1] if j+1 < len(lines) else ""
            # Replace the window.open approach with iframe
            lines[j] = "        const iframe = document.createElement('iframe');\n"
            new_lines_print = [
                "        iframe.style.cssText = 'position:fixed;top:-9999px;left:-9999px;width:1px;height:1px';\n",
                "        document.body.appendChild(iframe);\n",
                "        iframe.contentDocument.open();\n",
                "        iframe.contentDocument.write(html);\n",
                "        iframe.contentDocument.close();\n",
                "        setTimeout(() => { iframe.contentWindow.focus(); iframe.contentWindow.print(); setTimeout(() => document.body.removeChild(iframe), 2000); }, 500);\n",
            ]
            # Remove the old pw.document line if present
            if "pw" in lines[j+1]:
                lines[j+1] = "\n"
            for k, nl in enumerate(new_lines_print):
                lines.insert(j+1+k, nl)
            changes += 1
            print(f"FIX 1: Print changed to iframe at L{j+1}")
            break
else:
    print("WARN 1: handlePrintDPR not found")

# ================================================================
# FIX 2: MANPOWER COUNT - After attendance saved, update sel + reload
# In DprAttendancePanel.handleSave, after showToast("Attendance saved!")
# add: if (onSaved) onSaved(rows.filter(r=>r.am==="P"||r.pm==="P").length);
# ================================================================
dap = find("const DprAttendancePanel = (")
if dap != -1:
    # Update panel signature to accept onSaved prop
    if "onSaved" not in lines[dap]:
        lines[dap] = lines[dap].replace(
            "showToast })",
            "showToast, onSaved })"
        )
        changes += 1
        print(f"FIX 2a: onSaved prop added to DprAttendancePanel signature")
    # Find handleSave in panel and add onSaved callback after showToast
    for j in range(dap, min(dap+200, len(lines))):
        if 'showToast("Attendance saved!")' in lines[j]:
            if "onSaved" not in lines[j+1]:
                lines.insert(j+1, "        if (onSaved) onSaved(rows.filter(r => r.am===\"P\" || r.pm===\"P\").length);\n")
                changes += 1
                print(f"FIX 2b: onSaved callback added after attendance save at L{j+1}")
            break

# Add onSaved handler to DprAttendancePanel usage in DailyReports form
# Find the DprAttendancePanel usage
for j in range(0, len(lines)):
    if "<DprAttendancePanel" in lines[j] and "dprId={mpAttDprId" in lines[j]:
        # Find the closing /> and add onSaved before it
        for k in range(j, min(j+12, len(lines))):
            if "/>" in lines[k] and "onSaved" not in "".join(lines[j:k+1]):
                lines[k] = lines[k].replace("/>", "\n        onSaved={(count) => { setSel(p => p ? {...p, manpowerTotal: count} : p); onUpdate && onUpdate(sel&&sel.id, {...sel, manpowerTotal: count}); }}\n      />")
                changes += 1
                print(f"FIX 2c: onSaved handler added to DprAttendancePanel usage at L{k+1}")
                break
        break

# ================================================================
# FIX 3: HIDE OLD MANPOWER SUMMARY - wrap in collapsible, default hidden
# Find the old summary section and add a show/hide toggle
# L3754: <SectionHead ... title="Manpower Summary"
# ================================================================
dr = find("const DailyReports = ({")
for j in range(dr, min(dr+900, len(lines))):
    if 'title="Manpower Summary"' in lines[j] or 'title="Quick Summary' in lines[j]:
        # Find the surrounding div for this section
        # Look back for the opening conditional
        for k in range(j-1, max(j-5, 0), -1):
            if 'activeSection==="manpower"' in lines[k] and "<div" in lines[k]:
                # Add a note that this is legacy
                if "Legacy" not in lines[k] and "legacy" not in lines[k]:
                    # Wrap the old summary in a details/summary element
                    # Simple approach: add a small label above it
                    label_line = '          <div className="text-xs text-slate-400 italic px-2 mb-1">Legacy summary (optional) — use Daily Attendance Register below for detailed tracking</div>\n'
                    if "Legacy summary" not in "".join(lines[max(0,k-2):k+2]):
                        lines.insert(j, label_line)
                        changes += 1
                        print(f"FIX 3: Legacy label added above old manpower summary at L{j+1}")
                break
        break

# ================================================================
# FIX 4: LOAD MASTER - improve label and add helpful tooltip text
# ================================================================
for j in range(0, len(lines)):
    if "Load from Manpower Master" in lines[j] and "label" in lines[j].lower():
        lines[j] = lines[j].replace(
            "Load from Manpower Master",
            "Auto-load employees (from Manpower Master)"
        )
        changes += 1
        print(f"FIX 4: Load Master label improved at L{j+1}")
        break

for j in range(0, len(lines)):
    if "Load Master" in lines[j] and "&#8635;" in lines[j] and "button" in lines[j]:
        lines[j] = lines[j].replace(
            "&#8635; Load Master",
            "&#8635; Load Employees"
        )
        changes += 1
        print(f"FIX 4b: Button text updated at L{j+1}")
        break

# ================================================================
# FIX 5: Add hint under Load Master explaining purpose
# ================================================================
for j in range(0, len(lines)):
    if "Auto-load employees (from Manpower Master)" in lines[j]:
        # Add helper text after the Sel dropdown but before the button
        # Find the Sel closing tag
        for k in range(j+1, min(j+6, len(lines))):
            if "</Sel>" in lines[k] or (">" in lines[k] and "Sel" in lines[k]):
                hint = '          <p className="text-xs text-slate-400 mt-0.5">Select company then click Load Employees. Adds active staff from Manpower Master — no daily re-entry needed.</p>\n'
                if "no daily re-entry" not in "".join(lines[k:k+3]):
                    lines.insert(k+1, hint)
                    changes += 1
                    print(f"FIX 5: Load Master hint added at L{k+2}")
                break
        break

# ================================================================
# SAFETY CHECK AND WRITE
# ================================================================
out = "".join(lines)
checks = ["const DailyReports", "handlePrintDPR", "DprAttendancePanel", "saveAttendance"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL:", failed, "— restoring backup")
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print(f"\nFile saved. Lines: {len(lines)}")

print()
print("="*55)
print("TOTAL FIXES:", changes)
print()
print("RUN NOW:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js')
print('  git commit -m "Fix: DPR print iframe + manpower count + UX"')
print('  git push')
print("="*55)
input("Press Enter...")
