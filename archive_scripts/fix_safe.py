import shutil, os
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

print("Lines loaded:", len(lines))
changes = 0

def find(t):
    for i,l in enumerate(lines): 
        if t in l: return i
    return -1

# ================================================================
# FIX 1: saveAttendance - add manpower_total update after L11975
# Line 11975 (0-based: 11974): if (error) return { ok: false...
# Line 11976 (0-based: 11975): return { ok: true };
# Insert 2 new lines between them
# ================================================================
sa = find("saveAttendance = async")
if sa != -1:
    for j in range(sa, min(sa+20, len(lines))):
        if "return { ok: true };" in lines[j] and j > sa+5:
            # Insert update before the return
            new1 = "      const presentCount = valid.filter(r => r.am===\"P\" || r.pm===\"P\").length;\n"
            new2 = "      await supabase.from(\"daily_reports\").update({ manpower_total: presentCount }).eq(\"id\", dprId);\n"
            if "presentCount" not in lines[j-1]:
                lines.insert(j, new2)
                lines.insert(j, new1)
                changes += 1
                print(f"FIX 1: manpower_total update added at L{j+1}")
            else:
                print("SKIP 1: already inserted")
            break

# ================================================================
# FIX 2: Add Print button before Edit Report button (L3712 area)
# ================================================================
dr = find("const DailyReports = ({")
view_edit_line = -1
if dr != -1:
    for j in range(dr+500, min(dr+1500, len(lines))):
        if 'openEdit(sel)' in lines[j] and '"Edit Report"' in lines[j] and 'Btn' in lines[j]:
            view_edit_line = j
            break

if view_edit_line != -1:
    if "handlePrintDPR" not in lines[view_edit_line-1]:
        print_btn = '              <button onClick={()=>handlePrintDPR(sel)} className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-xl text-sm font-semibold transition-colors">Print DPR</button>\n'
        lines.insert(view_edit_line, print_btn)
        changes += 1
        print(f"FIX 2: Print DPR button added at L{view_edit_line+1}")
    else:
        print("SKIP 2: Print button already exists")
else:
    print("WARN 2: Edit Report button not found")

# ================================================================
# FIX 3: Add handlePrintDPR function before return( in DailyReports
# Find the top-level return( inside DailyReports
# ================================================================
dr2 = find("const DailyReports = ({")
ret_line = -1
if dr2 != -1:
    depth = 0
    for j in range(dr2, min(dr2+1600, len(lines))):
        depth += lines[j].count('{') - lines[j].count('}')
        if depth == 1 and lines[j].strip().startswith('return (') and j > dr2+100:
            ret_line = j
            break

if ret_line != -1 and find("handlePrintDPR") == -1:
    print_fn = [
        "\n",
        "      const handlePrintDPR = async (rpt) => {\n",
        "        const proj = projects.find(p => p.id === rpt.pid);\n",
        "        const att  = await loadAttendance(rpt.id);\n",
        "        const presentAM = att.filter(r => r.am === \"P\").length;\n",
        "        const presentPM = att.filter(r => r.pm === \"P\").length;\n",
        "\n",
        "        const mkRow = (r, i) => [\n",
        "          '<tr style=\"border-bottom:1px solid #e2e8f0\">',\n",
        "          '<td style=\"padding:4px 6px;text-align:center;color:#94a3b8\">' + (i+1) + '</td>',\n",
        "          '<td style=\"padding:4px 6px;font-weight:700;color:#1d4ed8\">' + (r.empId||'--') + '</td>',\n",
        "          '<td style=\"padding:4px 6px;font-weight:600\">' + (r.name||'--') + '</td>',\n",
        "          '<td style=\"padding:4px 6px;color:#64748b\">' + (r.designation||'--') + '</td>',\n",
        "          '<td style=\"padding:4px 6px;text-align:center;color:#7c3aed;font-weight:700\">' + (r.teamNo||'--') + '</td>',\n",
        "          '<td style=\"padding:4px 6px;text-align:center;font-weight:900;color:' + (r.am===\"P\"?'#15803d':'#b91c1c') + '\">' + r.am + '</td>',\n",
        "          '<td style=\"padding:4px 6px;text-align:center;font-weight:900;color:' + (r.pm===\"P\"?'#15803d':'#b91c1c') + '\">' + r.pm + '</td>',\n",
        "          '<td style=\"padding:4px 6px;text-align:center;color:#d97706\">' + (r.ot&&r.ot!==\"0\"?r.ot:'--') + '</td>',\n",
        "          '<td style=\"padding:4px 6px;color:#475569\">' + (r.description||'--') + '</td>',\n",
        "          '</tr>'\n",
        "        ].join('');\n",
        "\n",
        "        const secTbl = (title, rows, heads, cols) => {\n",
        "          if (!rows || !rows.length) return '';\n",
        "          return '<div style=\"margin-top:12px\">' +\n",
        "            '<div style=\"background:#1e293b;color:white;padding:5px 10px;font-weight:700;font-size:11px\">' + title + '</div>' +\n",
        "            '<table style=\"width:100%;border-collapse:collapse;font-size:10px\">' +\n",
        "            '<thead><tr style=\"background:#f1f5f9\">' + heads.map(h => '<th style=\"padding:4px 8px;text-align:left;font-weight:700;color:#64748b;border-bottom:1px solid #e2e8f0\">' + h + '</th>').join('') + '</tr></thead>' +\n",
        "            '<tbody>' + rows.map(r => '<tr>' + cols.map(c => '<td style=\"padding:3px 8px;color:#374151;border-bottom:1px solid #f1f5f9\">' + (r[c]||'--') + '</td>').join('') + '</tr>').join('') + '</tbody>' +\n",
        "            '</table></div>';\n",
        "        };\n",
        "\n",
        "        const html = [\n",
        "          '<!DOCTYPE html><html><head><title>' + (rpt.reportNum||'DPR') + '</title>',\n",
        "          '<style>',\n",
        "          'body{font-family:Arial,sans-serif;font-size:12px;color:#1e293b;margin:0;padding:16px}',\n",
        "          '@page{size:A4 landscape;margin:12mm}',\n",
        "          '@media print{.noprint{display:none}}',\n",
        "          '</style></head><body>',\n",
        "          '<div style=\"text-align:center;border-bottom:3px double #1e293b;padding-bottom:8px;margin-bottom:10px\">',\n",
        "          '<div style=\"font-size:16px;font-weight:900\">AL GHAITH BUILDING CONSTRUCTION LLC</div>',\n",
        "          '<div style=\"font-size:12px;font-weight:700;color:#d97706\">SITE DAILY REPORT</div>',\n",
        "          '</div>',\n",
        "          '<table style=\"width:100%;border:1px solid #e2e8f0;border-collapse:collapse;margin-bottom:10px\">',\n",
        "          '<tr style=\"background:#f8fafc\">',\n",
        "          '<td style=\"padding:4px 8px\"><b>Site No:</b> ' + (proj?proj.number:'--') + '</td>',\n",
        "          '<td style=\"padding:4px 8px\"><b>Project:</b> ' + (proj?proj.name:'--') + '</td>',\n",
        "          '<td style=\"padding:4px 8px\"><b>Date:</b> ' + (rpt.date||'--') + '</td>',\n",
        "          '<td style=\"padding:4px 8px\"><b>Report No:</b> ' + (rpt.reportNum||'--') + '</td>',\n",
        "          '</tr><tr>',\n",
        "          '<td style=\"padding:4px 8px\"><b>Prepared By:</b> ' + (rpt.preparedBy||'--') + '</td>',\n",
        "          '<td style=\"padding:4px 8px\"><b>Weather:</b> ' + (rpt.weather||'--') + ' ' + (rpt.temp?rpt.temp+'C':'') + '</td>',\n",
        "          '<td style=\"padding:4px 8px\"><b>Work Hours:</b> ' + (rpt.workHours||'8') + 'h</td>',\n",
        "          '<td style=\"padding:4px 8px\"><b>Status:</b> ' + (rpt.status||'--') + '</td>',\n",
        "          '</tr></table>',\n",
        "          att.length > 0 ? [\n",
        "            '<div style=\"margin-bottom:12px\">',\n",
        "            '<div style=\"background:#1e293b;color:white;padding:5px 10px;font-weight:700;font-size:11px\">',\n",
        "            'MANPOWER ATTENDANCE | Total: ' + att.length + ' | AM Present: ' + presentAM + ' | PM Present: ' + presentPM,\n",
        "            '</div>',\n",
        "            '<table style=\"width:100%;border-collapse:collapse;font-size:10px\">',\n",
        "            '<thead><tr style=\"background:#f1f5f9\">',\n",
        "            ['S.No','ID No','Name','Designation','Team','A.M','P.M','O.T','Description of Work'].map(h => '<th style=\"padding:4px 6px;text-align:left;font-weight:700;color:#475569;border-bottom:2px solid #e2e8f0\">' + h + '</th>').join(''),\n",
        "            '</tr></thead>',\n",
        "            '<tbody>' + att.map((r,i) => mkRow(r,i)).join('') + '</tbody>',\n",
        "            '<tfoot><tr style=\"background:#1e293b;color:white\">',\n",
        "            '<td colspan=\"5\" style=\"padding:4px 8px;font-weight:700;font-size:10px\">TOTAL PRESENT</td>',\n",
        "            '<td style=\"padding:4px 6px;font-weight:900;color:#86efac;text-align:center\">' + presentAM + '</td>',\n",
        "            '<td style=\"padding:4px 6px;font-weight:900;color:#93c5fd;text-align:center\">' + presentPM + '</td>',\n",
        "            '<td colspan=\"2\" style=\"padding:4px 8px;color:#cbd5e1;font-size:10px\">Absent: ' + att.filter(r=>r.am===\"A\"&&r.pm===\"A\").length + '</td>',\n",
        "            '</tr></tfoot></table></div>'\n",
        "          ].join('') : '',\n",
        "          secTbl('EQUIPMENT', rpt.equipment||[], ['Equipment','Qty','Status','Operator','Remarks'], ['name','qty','status','operator','remarks']),\n",
        "          secTbl('WORK ACTIVITIES', rpt.activities||[], ['Location','Activity','Trade','Progress %','Remarks'], ['location','activity','trade','progress','remarks']),\n",
        "          secTbl('MATERIALS', rpt.materials||[], ['Material','Qty','Unit','Supplier','DN No.'], ['material','qty','unit','supplier','dn']),\n",
        "          secTbl('SAFETY', rpt.safety||[], ['Observation','Severity','Action','Responsible','Status'], ['obs','severity','action','responsible','status']),\n",
        "          rpt.issues ? '<div style=\"margin-top:10px;padding:6px 10px;background:#fff5f5;border:1px solid #fecaca\"><b style=\"color:#dc2626\">Issues:</b> ' + rpt.issues + '</div>' : '',\n",
        "          rpt.remarks ? '<div style=\"margin-top:6px;padding:6px 10px;background:#f8fafc;border:1px solid #e2e8f0\"><b>Remarks:</b> ' + rpt.remarks + '</div>' : '',\n",
        "          '<div style=\"margin-top:28px;display:flex;justify-content:space-between;border-top:1px solid #e2e8f0;padding-top:10px\">',\n",
        "          '<div style=\"width:180px;text-align:center\"><div style=\"border-top:1px solid #374151;padding-top:3px;font-size:10px\">Signature Site Engineer</div></div>',\n",
        "          '<div style=\"width:180px;text-align:center\"><div style=\"border-top:1px solid #374151;padding-top:3px;font-size:10px\">Signature Site Incharge</div></div>',\n",
        "          '</div>',\n",
        "          '<div class=\"noprint\" style=\"text-align:center;margin-top:14px\">',\n",
        "          '<button onclick=\"window.print()\" style=\"padding:8px 24px;background:#1e293b;color:white;border:none;border-radius:6px;font-size:13px;font-weight:700;cursor:pointer\">Print</button>',\n",
        "          '<button onclick=\"window.close()\" style=\"margin-left:10px;padding:8px 16px;background:#e2e8f0;color:#374151;border:none;border-radius:6px;font-size:13px;cursor:pointer\">Close</button>',\n",
        "          '</div></body></html>'\n",
        "        ].join('');\n",
        "\n",
        "        const pw = window.open('', '_blank', 'width=1100,height=800');\n",
        "        if (pw) { pw.document.write(html); pw.document.close(); pw.focus(); }\n",
        "      };\n",
        "\n",
    ]
    for k, ln in enumerate(reversed(print_fn)):
        lines.insert(ret_line, ln)
    changes += 1
    print(f"FIX 3: handlePrintDPR inserted before return at L{ret_line+1}")
elif find("handlePrintDPR") != -1:
    print("SKIP 3: handlePrintDPR already exists")
else:
    print("WARN 3: Could not find return( in DailyReports")

# ================================================================
# WRITE - safe write with verification
# ================================================================
out = "".join(lines)
# Safety check - must contain key functions
checks = ["const DailyReports", "function useManpowerMaster", "DprAttendancePanel", "handlePrintDPR"]
failed = [c for c in checks if c not in out]
if failed:
    print("ERROR: Safety check failed! Missing:", failed)
    print("NOT writing file - restoring from backup")
    shutil.copy2(bk, APP)
else:
    with open(APP, "w", encoding="utf-8") as f:
        f.write(out)
    print("\nFile written successfully")
    print("Lines now:", len(lines))

print()
print("="*55)
print("TOTAL FIXES:", changes)
print()
print("RUN NOW:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js')
print('  git commit -m "feat: DPR print + manpower count fix"')
print('  git push')
print("="*55)
input("Press Enter...")
