import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

content = "".join(lines)
changes = 0
def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# ── FIX 1: Emoji encoding — use ASCII-safe text instead ──────────────
for old,new in [
    ('\uD83D\uDCBE Save Attendance', 'Save Attendance'),
    ('\U0001F4BE Save Attendance',   'Save Attendance'),
    ('&#128190; Save Attendance',    'Save Attendance'),
]:
    if old in content:
        content = content.replace(old, new)
        changes += 1
        print("FIX 1: Emoji removed — now plain 'Save Attendance'")
        break

# ── FIX 3: Rename old Manpower Summary ───────────────────────────────
for old,new in [
    ('title="Manpower Summary"', 'title="Quick Summary (optional)"'),
    ("title='Manpower Summary'", "title='Quick Summary (optional)'"),
]:
    if old in content:
        content = content.replace(old, new, 1)
        changes += 1
        print("FIX 3: Old manpower section renamed")
        break
else:
    print("SKIP 3: Already renamed or not found")

# ── FIX 5: Add handlePrintDPR function before closing of DailyReports
# Strategy: insert just before "const DailyReports" return statement
# by finding the last "const handle" in DailyReports and inserting after it
# ─────────────────────────────────────────────────────────────────────
PRINT_FUNC = r"""
      const handlePrintDPR = async (rpt) => {
        const proj = projects.find(p => p.id === rpt.pid);
        const att  = await loadAttendance(rpt.id);
        const presentAM = att.filter(r => r.am === "P").length;
        const presentPM = att.filter(r => r.pm === "P").length;

        const paCell = v => '<span style="display:inline-block;width:22px;height:22px;border-radius:4px;font-weight:900;font-size:12px;text-align:center;line-height:22px;border:2px solid ' + (v==="P"?"#16a34a":"#dc2626") + ';color:' + (v==="P"?"#15803d":"#b91c1c") + ';background:' + (v==="P"?"#dcfce7":"#fee2e2") + '">' + v + '</span>';

        const attRows = att.map((r,i) =>
          '<tr style="border-bottom:1px solid #e2e8f0;background:' + (r.am==="A"&&r.pm==="A"?"#fff5f5":"") + '">' +
          '<td style="padding:4px 6px;text-align:center;color:#94a3b8">' + (i+1) + '</td>' +
          '<td style="padding:4px 6px;font-family:monospace;font-weight:700;color:#1d4ed8">' + (r.empId||"--") + '</td>' +
          '<td style="padding:4px 6px;font-weight:600">' + (r.name||"--") + '</td>' +
          '<td style="padding:4px 6px;color:#64748b">' + (r.designation||"--") + '</td>' +
          '<td style="padding:4px 6px;text-align:center;font-weight:700;color:#7c3aed">' + (r.teamNo||"--") + '</td>' +
          '<td style="padding:4px 6px;text-align:center">' + paCell(r.am) + '</td>' +
          '<td style="padding:4px 6px;text-align:center">' + paCell(r.pm) + '</td>' +
          '<td style="padding:4px 6px;text-align:center;color:#d97706;font-weight:600">' + (r.ot&&r.ot!=="0"?r.ot:"--") + '</td>' +
          '<td style="padding:4px 6px;color:#475569">' + (r.description||"--") + '</td></tr>'
        ).join("");

        const secTable = (title, rows, heads, cols) => {
          if (!rows || !rows.length) return "";
          return '<div style="margin-top:14px">' +
            '<div style="background:#1e293b;color:white;padding:5px 10px;font-weight:700;font-size:11px">' + title + '</div>' +
            '<table style="width:100%;border-collapse:collapse;font-size:10px">' +
            '<thead><tr style="background:#f1f5f9">' + heads.map(h => '<th style="padding:4px 8px;text-align:left;font-weight:700;color:#64748b;border-bottom:1px solid #e2e8f0">' + h + '</th>').join("") + '</tr></thead>' +
            '<tbody>' + rows.map(r => '<tr style="border-bottom:1px solid #f1f5f9">' + cols.map(c => '<td style="padding:3px 8px;color:#374151">' + (r[c]||"--") + '</td>').join("") + '</tr>').join("") + '</tbody>' +
            '</table></div>';
        };

        const html = '<!DOCTYPE html><html><head><title>' + (rpt.reportNum||"DPR") + ' - ' + (proj ? proj.number : "") + '</title>' +
          '<style>body{font-family:Arial,sans-serif;font-size:12px;color:#1e293b;margin:0;padding:16px}' +
          '@page{size:A4 landscape;margin:12mm}' +
          '@media print{.noprint{display:none}}</style></head><body>' +

          '<div style="text-align:center;border-bottom:3px double #1e293b;padding-bottom:8px;margin-bottom:10px">' +
          '<div style="font-size:16px;font-weight:900">AL GHAITH BUILDING CONSTRUCTION LLC</div>' +
          '<div style="font-size:12px;font-weight:700;color:#d97706">SITE DAILY REPORT</div></div>' +

          '<table style="width:100%;border:1px solid #e2e8f0;border-collapse:collapse;margin-bottom:10px">' +
          '<tr style="background:#f8fafc">' +
          '<td style="padding:4px 8px"><b>Site No:</b> ' + (proj ? proj.number : "--") + '</td>' +
          '<td style="padding:4px 8px"><b>Project:</b> ' + (proj ? proj.name : "--") + '</td>' +
          '<td style="padding:4px 8px"><b>Date:</b> ' + (rpt.date||"--") + '</td>' +
          '<td style="padding:4px 8px"><b>Report No:</b> ' + (rpt.reportNum||"--") + '</td></tr>' +
          '<tr><td style="padding:4px 8px"><b>Prepared By:</b> ' + (rpt.preparedBy||"--") + '</td>' +
          '<td style="padding:4px 8px"><b>Weather:</b> ' + (rpt.weather||"--") + ' ' + (rpt.temp ? rpt.temp+"C" : "") + '</td>' +
          '<td style="padding:4px 8px"><b>Work Hours:</b> ' + (rpt.workHours||"8") + 'h</td>' +
          '<td style="padding:4px 8px"><b>Status:</b> ' + (rpt.status||"--") + '</td></tr></table>' +

          (att.length > 0 ?
          '<div style="margin-bottom:14px">' +
          '<div style="background:#1e293b;color:white;padding:5px 10px;font-weight:700;font-size:11px">' +
          'MANPOWER ATTENDANCE | Total: ' + att.length + ' | AM Present: ' + presentAM + ' | PM Present: ' + presentPM + '</div>' +
          '<table style="width:100%;border-collapse:collapse;font-size:10px">' +
          '<thead><tr style="background:#f1f5f9">' +
          ['S.No','ID No','Name','Designation','Team','A.M','P.M','O.T','Description of Work'].map(h =>
            '<th style="padding:4px 6px;text-align:left;font-weight:700;color:#475569;border-bottom:2px solid #e2e8f0">' + h + '</th>'
          ).join("") + '</tr></thead>' +
          '<tbody>' + attRows + '</tbody>' +
          '<tfoot><tr style="background:#1e293b;color:white">' +
          '<td colspan="5" style="padding:4px 8px;font-weight:700;font-size:10px">TOTAL PRESENT</td>' +
          '<td style="padding:4px 6px;font-weight:900;color:#86efac;text-align:center">' + presentAM + '</td>' +
          '<td style="padding:4px 6px;font-weight:900;color:#93c5fd;text-align:center">' + presentPM + '</td>' +
          '<td colspan="2" style="padding:4px 8px;color:#cbd5e1;font-size:10px">Absent: ' + att.filter(r=>r.am==="A"&&r.pm==="A").length + '</td>' +
          '</tr></tfoot></table></div>' : "") +

          secTable("EQUIPMENT", rpt.equipment||[], ["Equipment","Qty","Status","Operator","Remarks"], ["name","qty","status","operator","remarks"]) +
          secTable("WORK ACTIVITIES", rpt.activities||[], ["Location","Activity","Trade","Progress %","Remarks"], ["location","activity","trade","progress","remarks"]) +
          secTable("MATERIALS RECEIVED", rpt.materials||[], ["Material","Qty","Unit","Supplier","DN No."], ["material","qty","unit","supplier","dn"]) +
          secTable("SAFETY", rpt.safety||[], ["Observation","Severity","Action","Responsible","Status"], ["obs","severity","action","responsible","status"]) +

          (rpt.issues ? '<div style="margin-top:10px;padding:6px 10px;background:#fff5f5;border:1px solid #fecaca"><b style="color:#dc2626">Issues / Delays:</b> ' + rpt.issues + '</div>' : "") +
          (rpt.remarks ? '<div style="margin-top:6px;padding:6px 10px;background:#f8fafc;border:1px solid #e2e8f0"><b>Remarks:</b> ' + rpt.remarks + '</div>' : "") +

          '<div style="margin-top:30px;display:flex;justify-content:space-between;border-top:1px solid #e2e8f0;padding-top:12px">' +
          '<div style="width:180px;text-align:center"><div style="border-top:1px solid #374151;padding-top:3px;font-size:10px">Signature Site Engineer</div></div>' +
          '<div style="width:180px;text-align:center"><div style="border-top:1px solid #374151;padding-top:3px;font-size:10px">Signature Site Incharge</div></div>' +
          '</div>' +

          '<div class="noprint" style="text-align:center;margin-top:16px">' +
          '<button onclick="window.print()" style="padding:8px 24px;background:#1e293b;color:white;border:none;border-radius:6px;font-size:13px;font-weight:700;cursor:pointer">Print</button>' +
          '<button onclick="window.close()" style="margin-left:10px;padding:8px 16px;background:#e2e8f0;color:#374151;border:none;border-radius:6px;font-size:13px;cursor:pointer">Close</button>' +
          '</div></body></html>';

        const pw = window.open("","_blank","width=1100,height=800");
        if (pw) { pw.document.write(html); pw.document.close(); pw.focus(); }
      };
"""

# Find DailyReports component and insert handlePrintDPR
# after the last handleXxx function before the return statement
lns = content.split('\n')
dr_idx = -1
for i,l in enumerate(lns):
    if 'const DailyReports = ({' in l: dr_idx=i; break

if dr_idx != -1:
    # Find "const handleApprove" or "return (" in DailyReports
    # Insert handlePrintDPR just before "return ("
    depth = 0
    ret_line = -1
    in_comp = False
    brace_count = 0
    for j in range(dr_idx, min(dr_idx+1500, len(lns))):
        brace_count += lns[j].count('{') - lns[j].count('}')
        # The return of the DailyReports component (top-level return, not nested)
        if brace_count == 1 and lns[j].strip().startswith('return (') and j > dr_idx+100:
            ret_line = j
            break

    if ret_line != -1:
        # Check if handlePrintDPR already exists
        existing = any('handlePrintDPR' in lns[k] for k in range(dr_idx, ret_line))
        if not existing:
            lns.insert(ret_line, PRINT_FUNC)
            content = '\n'.join(lns)
            changes += 1
            print(f"FIX 5: handlePrintDPR inserted at L{ret_line+1}")
        else:
            print("SKIP 5: handlePrintDPR already exists")
    else:
        print("WARN 5: Could not find return statement in DailyReports")
else:
    print("WARN 5: DailyReports not found")

# ── FIX 4: Fix print button — remove wrong one, add correct one ───────
# Remove print button added to wrong module (Drawings at L4652 area)
lns2 = content.split('\n')
removed = 0
for i,l in enumerate(lns2):
    if 'handlePrintDPR' in l and 'Print DPR' in l and 'onClick' in l:
        # Check if this is in DailyReports view (not Drawings)
        # Find what module this is in
        for k in range(i-1, max(0,i-200), -1):
            if 'const DailyReports' in lns2[k]:
                # Good - inside DailyReports, keep it
                print(f"INFO 4: Print button at L{i+1} is inside DailyReports - OK")
                break
            if 'const Drawings' in lns2[k] or 'const NOCModule' in lns2[k]:
                # Wrong module - remove
                lns2[i] = ''
                removed += 1
                print(f"FIX 4b: Removed wrong print button from non-DPR module at L{i+1}")
                break

content = '\n'.join(lns2)

# Add print button in correct location - inside DPR view mode action buttons
# Find the DPR view buttons (Edit Report / Delete buttons)
lns3 = content.split('\n')
dr3 = -1
for i,l in enumerate(lns3):
    if 'const DailyReports = ({' in l: dr3=i; break

if dr3 != -1:
    for j in range(dr3+400, min(dr3+1400, len(lns3))):
        l = lns3[j]
        # Find "Edit Report" button inside view mode (not edit mode)
        if ('openEdit(sel)' in l or '"Edit Report"' in l) and ('Btn' in l or 'button' in l):
            # Check we're in view mode context (within 200 lines of mode==="view")
            ctx = '\n'.join(lns3[max(0,j-50):j])
            if 'mode==="view"' in ctx or 'View' in '\n'.join(lns3[max(0,j-200):j]):
                # Check if print button already exists nearby
                nearby = '\n'.join(lns3[max(0,j-5):j+5])
                if 'handlePrintDPR' not in nearby:
                    print_btn = '              <button onClick={()=>handlePrintDPR(sel)} className="flex items-center gap-1.5 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-colors">Print DPR</button>'
                    lns3.insert(j, print_btn)
                    content = '\n'.join(lns3)
                    changes += 1
                    print(f"FIX 4: Print DPR button added at L{j+1}")
                else:
                    print(f"INFO 4: Print button already near L{j+1}")
                break

# ── WRITE ────────────────────────────────────────────────────────────
with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print()
print("="*55)
print("TOTAL FIXES:", changes)
print()
print("RUN NOW:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js')
print('  git commit -m "feat: DPR print + manpower fixes"')
print('  git push')
print("="*55)
input("Press Enter...")
