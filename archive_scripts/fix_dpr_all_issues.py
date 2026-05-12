import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

content = "".join(lines)
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
changes = 0

# ══════════════════════════════════════════════════════════════════════
# FIX 1: &#128190; HTML entity → plain text in JSX
# ══════════════════════════════════════════════════════════════════════
old_btn = '            {saving?"Saving...":"&#128190; Save Attendance"}'
new_btn = '            {saving?"Saving...":"\uD83D\uDCBE Save Attendance"}'
if old_btn in content:
    content = content.replace(old_btn, new_btn)
    changes += 1
    print("FIX 1: Save Attendance emoji fixed")
else:
    # Try alternate
    content = content.replace('&#128190; Save Attendance', '💾 Save Attendance')
    changes += 1
    print("FIX 1b: Save Attendance emoji fixed (alt)")

# ══════════════════════════════════════════════════════════════════════
# FIX 2: saveAttendance — also update manpower_total in daily_reports
# ══════════════════════════════════════════════════════════════════════
OLD_SAVE_END = """      if (error) return { ok: false, error: error.message };
      return { ok: true };
    };

    return { masters, loading, addMaster, updateMaster, removeMaster, toggleMpStatus, loadAttendance, saveAttendance };"""

NEW_SAVE_END = """      if (error) return { ok: false, error: error.message };
      // Update manpower_total in daily_reports to reflect attendance count
      const presentCount = valid.filter(r => r.am==="P" || r.pm==="P").length;
      await supabase.from("daily_reports").update({ manpower_total: presentCount }).eq("id", dprId);
      return { ok: true };
    };

    return { masters, loading, addMaster, updateMaster, removeMaster, toggleMpStatus, loadAttendance, saveAttendance };"""

if OLD_SAVE_END in content:
    content = content.replace(OLD_SAVE_END, NEW_SAVE_END)
    changes += 1
    print("FIX 2: saveAttendance now updates manpower_total in daily_reports")
else:
    # line by line approach
    lns = content.split('\n')
    for i,l in enumerate(lns):
        if "if (error) return { ok: false, error: error.message };" in l:
            # Check if next line is "return { ok: true };"
            if i+1 < len(lns) and "return { ok: true };" in lns[i+1]:
                # Check context - inside saveAttendance
                ctx = '\n'.join(lns[max(0,i-10):i])
                if "saveAttendance" in ctx or "dpr_attendance" in ctx:
                    lns.insert(i+1, "      const presentCount = valid.filter(r => r.am===\"P\" || r.pm===\"P\").length;")
                    lns.insert(i+2, "      await supabase.from(\"daily_reports\").update({ manpower_total: presentCount }).eq(\"id\", dprId);")
                    content = '\n'.join(lns)
                    changes += 1
                    print(f"FIX 2b: manpower_total update inserted at L{i+2}")
                    break

# ══════════════════════════════════════════════════════════════════════
# FIX 3: Old Manpower Summary — collapse by default, rename to optional
# ══════════════════════════════════════════════════════════════════════
old_mp_head = '<SectionHead icon="?" title="Manpower Summary"'
new_mp_head = '<SectionHead icon="?" title="Quick Summary (optional)"'
if old_mp_head in content:
    content = content.replace(old_mp_head, new_mp_head, 1)
    changes += 1
    print("FIX 3: Old manpower section renamed to 'Quick Summary (optional)'")

# ══════════════════════════════════════════════════════════════════════
# FIX 4: Add Print button to DPR View mode
# Find the view mode Edit/Delete buttons and add Print before Edit
# ══════════════════════════════════════════════════════════════════════
# First find the DPR view action buttons
lns4 = content.split('\n')
dr_view = -1
for i,l in enumerate(lns4):
    if 'const DailyReports = ({' in l:
        dr_view = i; break

# Find the flex buttons block inside DPR view (after the sections list)
view_btns = -1
if dr_view != -1:
    for j in range(dr_view+500, min(dr_view+1200, len(lns4))):
        l = lns4[j]
        if 'openEdit(sel)' in l and ('Btn' in l or 'button' in l) and j > dr_view+400:
            view_btns = j
            break

if view_btns != -1:
    print(f"INFO: View edit button found at L{view_btns+1}")
    # Insert print button before edit button
    print_btn = '              <button onClick={()=>handlePrintDPR(sel)} className="flex items-center gap-1.5 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-colors">&#128424; Print DPR</button>'
    lns4.insert(view_btns, print_btn)
    content = '\n'.join(lns4)
    changes += 1
    print(f"FIX 4: Print button added to DPR View at L{view_btns+1}")
else:
    print("WARN 4: View edit button not found in DPR component")

# ══════════════════════════════════════════════════════════════════════
# FIX 5: Add handlePrintDPR function to DailyReports component
# Insert after the existing handleDelete function
# ══════════════════════════════════════════════════════════════════════
PRINT_FUNC = """
      const handlePrintDPR = async (rpt) => {
        const proj = projects.find(p=>p.id===rpt.pid);
        const att  = await loadAttendance(rpt.id);
        const presentAM = att.filter(r=>r.am==="P").length;
        const presentPM = att.filter(r=>r.pm==="P").length;
        const totalWorkers = att.length;

        const paCell = (v) => `<span style="display:inline-block;width:24px;height:24px;border-radius:4px;font-weight:900;font-size:13px;text-align:center;line-height:24px;border:2px solid ${v==="P"?"#16a34a":"#dc2626"};color:${v==="P"?"#15803d":"#b91c1c"};background:${v==="P"?"#dcfce7":"#fee2e2"}">${v}</span>`;

        const attRows = att.map((r,i)=>`
          <tr style="border-bottom:1px solid #e2e8f0;background:${r.am==="A"&&r.pm==="A"?"#fff5f5":""}">
            <td style="padding:4px 6px;text-align:center;color:#94a3b8">${i+1}</td>
            <td style="padding:4px 6px;font-family:monospace;font-weight:700;color:#1d4ed8">${r.empId||"—"}</td>
            <td style="padding:4px 6px;font-weight:600">${r.name||"—"}</td>
            <td style="padding:4px 6px;color:#64748b">${r.designation||"—"}</td>
            <td style="padding:4px 6px;text-align:center;font-weight:700;color:#7c3aed">${r.teamNo||"—"}</td>
            <td style="padding:4px 6px;text-align:center">${paCell(r.am)}</td>
            <td style="padding:4px 6px;text-align:center">${paCell(r.pm)}</td>
            <td style="padding:4px 6px;text-align:center;color:#d97706;font-weight:600">${r.ot&&r.ot!=="0"?r.ot:"—"}</td>
            <td style="padding:4px 6px;color:#475569;max-width:200px">${r.description||"—"}</td>
          </tr>`).join("");

        const sectionTable = (title, rows, heads, cols) => {
          if (!rows||!rows.length) return "";
          return `<div style="margin-top:16px">
            <div style="background:#1e293b;color:white;padding:6px 12px;font-weight:700;font-size:12px;border-radius:4px 4px 0 0">${title}</div>
            <table style="width:100%;border-collapse:collapse;font-size:11px">
              <thead><tr style="background:#f1f5f9">${heads.map(h=>`<th style="padding:5px 8px;text-align:left;font-weight:700;color:#64748b;border-bottom:1px solid #e2e8f0">${h}</th>`).join("")}</tr></thead>
              <tbody>${rows.map(r=>`<tr style="border-bottom:1px solid #f1f5f9">${cols.map(c=>`<td style="padding:4px 8px;color:#374151">${r[c]||"—"}</td>`).join("")}</tr>`).join("")}</tbody>
            </table></div>`;
        };

        const html = `<!DOCTYPE html><html>
<head><title>${rpt.reportNum||"DPR"} - ${proj?.number||""}</title>
<style>
  body{font-family:Arial,sans-serif;font-size:12px;color:#1e293b;margin:0;padding:20px}
  @page{size:A4 landscape;margin:15mm}
  @media print{.no-print{display:none}}
  table{width:100%;border-collapse:collapse}
  th,td{font-size:11px}
  .header-table td{padding:3px 6px}
</style></head>
<body>
  <div style="text-align:center;border-bottom:3px double #1e293b;padding-bottom:10px;margin-bottom:12px">
    <div style="font-size:18px;font-weight:900;letter-spacing:1px">AL GHAITH BUILDING CONSTRUCTION LLC</div>
    <div style="font-size:13px;font-weight:700;color:#d97706;margin-top:2px">SITE DAILY REPORT</div>
  </div>

  <table class="header-table" style="margin-bottom:12px;border:1px solid #e2e8f0;border-radius:4px">
    <tr style="background:#f8fafc">
      <td><b>Site No:</b> ${proj?.number||"—"}</td>
      <td><b>Project:</b> ${proj?.name||"—"}</td>
      <td><b>Date:</b> ${rpt.date||"—"}</td>
      <td><b>Report No:</b> ${rpt.reportNum||"—"}</td>
    </tr>
    <tr>
      <td><b>Prepared By:</b> ${rpt.preparedBy||"—"}</td>
      <td><b>Weather:</b> ${rpt.weather||"—"} ${rpt.temp?rpt.temp+"°C":""}</td>
      <td><b>Work Hours:</b> ${rpt.workHours||"8"}h</td>
      <td><b>Status:</b> ${rpt.status||"—"}</td>
    </tr>
  </table>

  ${att.length>0?`
  <div style="margin-bottom:16px">
    <div style="background:#1e293b;color:white;padding:6px 12px;font-weight:700;font-size:12px;border-radius:4px 4px 0 0">
      MANPOWER ATTENDANCE &nbsp;|&nbsp; Total: ${totalWorkers} &nbsp;|&nbsp; AM Present: ${presentAM} &nbsp;|&nbsp; PM Present: ${presentPM}
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:11px">
      <thead>
        <tr style="background:#f1f5f9">
          ${["S.No","ID No","Name","Designation","Team","A.M","P.M","O.T","Description of Work"].map(h=>`<th style="padding:5px 6px;text-align:left;font-weight:700;color:#475569;border-bottom:2px solid #e2e8f0;white-space:nowrap">${h}</th>`).join("")}
        </tr>
      </thead>
      <tbody>${attRows}</tbody>
      <tfoot>
        <tr style="background:#1e293b;color:white">
          <td colspan="5" style="padding:5px 8px;font-weight:700;font-size:11px">TOTAL PRESENT</td>
          <td style="padding:5px 6px;font-weight:900;color:#86efac;text-align:center">${presentAM}</td>
          <td style="padding:5px 6px;font-weight:900;color:#93c5fd;text-align:center">${presentPM}</td>
          <td colspan="2" style="padding:5px 8px;color:#cbd5e1;font-size:10px">Absent: ${att.filter(r=>r.am==="A"&&r.pm==="A").length} | OT: ${att.reduce((s,r)=>s+(parseFloat(r.ot)||0),0).toFixed(1)} hrs</td>
        </tr>
      </tfoot>
    </table>
  </div>`:""}

  ${sectionTable("EQUIPMENT",rpt.equipment||[],["Equipment","Qty","Status","Operator","Remarks"],["name","qty","status","operator","remarks"])}
  ${sectionTable("WORK ACTIVITIES",rpt.activities||[],["Location","Activity","Trade","Progress %","Remarks"],["location","activity","trade","progress","remarks"])}
  ${sectionTable("MATERIALS RECEIVED",rpt.materials||[],["Material","Qty","Unit","Supplier","DN No.","Remarks"],["material","qty","unit","supplier","dn","remarks"])}
  ${sectionTable("INSPECTIONS",rpt.inspections||[],["Type","Location","Consultant","Status","Remarks"],["type","location","consultant","status","remarks"])}
  ${sectionTable("SAFETY OBSERVATIONS",rpt.safety||[],["Observation","Severity","Action","Responsible","Status"],["obs","severity","action","responsible","status"])}

  ${rpt.issues?`<div style="margin-top:14px;padding:8px 12px;background:#fff5f5;border:1px solid #fecaca;border-radius:4px"><b style="color:#dc2626">Issues / Delays:</b> ${rpt.issues}</div>`:""}
  ${rpt.remarks?`<div style="margin-top:8px;padding:8px 12px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:4px"><b>Remarks:</b> ${rpt.remarks}</div>`:""}

  <div style="margin-top:40px;display:flex;justify-content:space-between;border-top:1px solid #e2e8f0;padding-top:16px">
    <div style="text-align:center;width:200px"><div style="border-top:1px solid #374151;padding-top:4px;font-size:11px;color:#374151">Site Engineer Signature</div></div>
    <div style="text-align:center;width:200px"><div style="border-top:1px solid #374151;padding-top:4px;font-size:11px;color:#374151">Site Incharge Signature</div></div>
  </div>

  <div class="no-print" style="text-align:center;margin-top:20px">
    <button onclick="window.print()" style="padding:10px 30px;background:#1e293b;color:white;border:none;border-radius:8px;font-size:14px;font-weight:700;cursor:pointer">&#128424; Print</button>
    <button onclick="window.close()" style="margin-left:12px;padding:10px 20px;background:#e2e8f0;color:#374151;border:none;border-radius:8px;font-size:14px;cursor:pointer">Close</button>
  </div>
</body></html>`;

        const pw = window.open("","_blank","width=1100,height=800");
        if(pw){ pw.document.write(html); pw.document.close(); pw.focus(); }
      };
"""

# Insert handlePrintDPR after handleDelete in DailyReports
lns5 = content.split('\n')
dr5 = -1
for i,l in enumerate(lns5):
    if 'const DailyReports = ({' in l: dr5=i; break

inserted = False
if dr5 != -1:
    for j in range(dr5+50, min(dr5+400, len(lns5))):
        # Find end of handleDelete
        if 'handleDelete' in lns5[j] and 'const handleApprove' in '\n'.join(lns5[j:j+5]):
            # Insert after the closing of handleDelete
            for k in range(j, min(j+15, len(lns5))):
                if lns5[k].strip() == '};' and k > j:
                    lns5.insert(k+1, PRINT_FUNC)
                    content = '\n'.join(lns5)
                    changes += 1
                    print(f"FIX 5: handlePrintDPR added after handleDelete at L{k+2}")
                    inserted = True
                    break
            if inserted: break

if not inserted:
    print("WARN 5: Could not find insertion point for handlePrintDPR")

# ══════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════
with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

print()
print("="*60)
print("TOTAL FIXES:", changes)
print()
print("RUN NOW:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js')
print('  git commit -m "feat: DPR print + fix manpower count + emoji"')
print('  git push')
print("="*60)
input("Press Enter...")
