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
# FIX 1: useDailyReports.add — return new record ID
# Find: const { error } = await supabase.from("daily_reports").insert
# Change to: const { data, error } = ... .select("id").single()
# Change return to: { ok: true, id: data?.id, reportNum }
# ================================================================
udr = find("function useDailyReports()")
if udr != -1:
    for j in range(udr, min(udr+60, len(lines))):
        l = lines[j]
        # Find the insert line for add function (not update)
        if 'supabase.from("daily_reports").insert' in l and "const { error }" in l:
            lines[j] = l.replace(
                'const { error } = await supabase.from("daily_reports").insert([{',
                'const { data: insData, error } = await supabase.from("daily_reports").insert([{'
            )
            if 'select' not in lines[j]:
                # Add .select("id").single() before the semicolon
                lines[j] = lines[j].rstrip()
                # Find closing of insert - might span multiple lines
                pass
            changes += 1
            print(f"FIX 1a: insert returns data at L{j+1}")
            break

    # Find the return { ok: true } inside the add function (before update function)
    in_add = False
    for j in range(udr, min(udr+80, len(lines))):
        if "const add = async" in lines[j]: in_add = True
        if in_add and "const update = async" in lines[j]: break
        if in_add and "return { ok: true };" in lines[j] and "reportNum" not in lines[j]:
            lines[j] = lines[j].replace(
                "return { ok: true };",
                "return { ok: true, id: insData?.id, reportNum };"
            )
            changes += 1
            print(f"FIX 1b: add returns id at L{j+1}")
            break

    # Also need to add .select() to the insert chain
    # Find the insert and add .select("id").single()
    for j in range(udr, min(udr+80, len(lines))):
        if "insData" in lines[j] and 'supabase.from("daily_reports").insert' in lines[j]:
            # Find the end of this insert statement (the closing ]));)
            for k in range(j, min(j+20, len(lines))):
                stripped = lines[k].rstrip()
                if stripped.endswith("]));") or stripped.endswith("]);"):
                    lines[k] = stripped.rstrip(";").rstrip(")").rstrip("]") + "]).select(\"id\").single();\n"
                    changes += 1
                    print(f"FIX 1c: .select('id').single() added at L{k+1}")
                    break
            break

# ================================================================
# FIX 2: Fix handlePrintDPR — open window BEFORE await
# Current: const pw = window.open AFTER await loadAttendance (blocked)
# Fix: open window first, fetch data, then write content
# ================================================================
hp = find("handlePrintDPR = async")
if hp != -1:
    func_end = -1
    depth = 0
    for j in range(hp, min(hp+15, len(lines))):
        depth += lines[j].count('{') - lines[j].count('}')
        if depth <= 0 and j > hp:
            func_end = j
            break

    if func_end != -1:
        new_fn = [
            "      const handlePrintDPR = async (rpt) => {\n",
            "        // Open window first (before await - keeps popup allowed by browser)\n",
            "        const pw = window.open('', '_blank', 'width=1150,height=850');\n",
            "        if (!pw) { showToast('Allow popups for this site to print', 'error'); setPrintData(null); return; }\n",
            "        pw.document.write('<html><body style=\"font-family:Arial;padding:20px\"><p>Loading report...</p></body></html>');\n",
            "        // Fetch attendance data\n",
            "        const proj = projects.find(p => p.id === rpt.pid);\n",
            "        const att = await loadAttendance(rpt.id);\n",
            "        const presAM = att.filter(r=>r.am==='P').length;\n",
            "        const presMP = att.filter(r=>r.pm==='P').length;\n",
            "        const mkR = (r,i) => '<tr style=\"border-bottom:1px solid #e2e8f0;background:'+(r.am===\"A\"&&r.pm===\"A\"?'#fff5f5':'')+'\">'\n",
            "          +'<td style=\"padding:4px 6px;text-align:center;color:#94a3b8\">'+(i+1)+'</td>'\n",
            "          +'<td style=\"padding:4px 6px;font-weight:700;color:#1d4ed8\">'+(r.empId||'--')+'</td>'\n",
            "          +'<td style=\"padding:4px 6px;font-weight:600\">'+(r.name||'--')+'</td>'\n",
            "          +'<td style=\"padding:4px 6px;color:#64748b\">'+(r.designation||'--')+'</td>'\n",
            "          +'<td style=\"padding:4px 6px;text-align:center;color:#7c3aed;font-weight:700\">'+(r.teamNo||'--')+'</td>'\n",
            "          +'<td style=\"padding:4px 6px;text-align:center;font-weight:900;color:'+(r.am===\"P\"?'#15803d':'#b91c1c')+'\">'+(r.am)+'</td>'\n",
            "          +'<td style=\"padding:4px 6px;text-align:center;font-weight:900;color:'+(r.pm===\"P\"?'#15803d':'#b91c1c')+'\">'+(r.pm)+'</td>'\n",
            "          +'<td style=\"padding:4px 6px;text-align:center;color:#d97706\">'+(r.ot&&r.ot!=='0'?r.ot:'--')+'</td>'\n",
            "          +'<td style=\"padding:4px 6px;color:#475569\">'+(r.description||'--')+'</td></tr>';\n",
            "        const html = '<!DOCTYPE html><html><head><title>'+(rpt.reportNum||'DPR')+'</title>'\n",
            "          +'<style>body{font-family:Arial,sans-serif;font-size:12px;color:#1e293b;margin:0;padding:16px}'\n",
            "          +'@page{size:A4 landscape;margin:12mm}table{border-collapse:collapse}th,td{font-size:11px}</style></head><body>'\n",
            "          +'<div style=\"text-align:center;border-bottom:3px double #1e293b;padding-bottom:8px;margin-bottom:10px\">'\n",
            "          +'<div style=\"font-size:16px;font-weight:900\">AL GHAITH BUILDING CONSTRUCTION LLC</div>'\n",
            "          +'<div style=\"font-size:12px;font-weight:700;color:#d97706\">SITE DAILY REPORT</div></div>'\n",
            "          +'<table style=\"width:100%;border:1px solid #e2e8f0;margin-bottom:10px\"><tbody>'\n",
            "          +'<tr style=\"background:#f8fafc\">'\n",
            "          +'<td style=\"padding:4px 8px\"><b>Site:</b> '+(proj?proj.number:'--')+'</td>'\n",
            "          +'<td style=\"padding:4px 8px\"><b>Project:</b> '+(proj?proj.name:'--')+'</td>'\n",
            "          +'<td style=\"padding:4px 8px\"><b>Date:</b> '+(rpt.date||'--')+'</td>'\n",
            "          +'<td style=\"padding:4px 8px\"><b>Report No:</b> '+(rpt.reportNum||'--')+'</td></tr><tr>'\n",
            "          +'<td style=\"padding:4px 8px\"><b>Prepared By:</b> '+(rpt.preparedBy||'--')+'</td>'\n",
            "          +'<td style=\"padding:4px 8px\"><b>Weather:</b> '+(rpt.weather||'--')+' '+(rpt.temp?rpt.temp+'C':'')+'</td>'\n",
            "          +'<td style=\"padding:4px 8px\"><b>Work Hours:</b> '+(rpt.workHours||'8')+'h</td>'\n",
            "          +'<td style=\"padding:4px 8px\"><b>Status:</b> '+(rpt.status||'--')+'</td>'\n",
            "          +'</tr></tbody></table>'\n",
            "          +(att.length>0?\n",
            "            '<div style=\"margin-bottom:12px\">'\n",
            "            +'<div style=\"background:#1e293b;color:white;padding:5px 10px;font-weight:700;font-size:11px\">'\n",
            "            +'MANPOWER ATTENDANCE | Total: '+att.length+' | AM Present: '+presAM+' | PM Present: '+presMP+'</div>'\n",
            "            +'<table style=\"width:100%\"><thead><tr style=\"background:#f1f5f9\">'\n",
            "            +['S.No','ID No','Name','Designation','Team','A.M','P.M','O.T','Description of Work'].map(h=>'<th style=\"padding:4px 6px;text-align:left;font-weight:700;color:#475569;border-bottom:2px solid #e2e8f0\">'+h+'</th>').join('')\n",
            "            +'</tr></thead><tbody>'+att.map((r,i)=>mkR(r,i)).join('')+'</tbody>'\n",
            "            +'<tfoot><tr style=\"background:#1e293b;color:white\">'\n",
            "            +'<td colspan=\"5\" style=\"padding:4px 8px;font-weight:700\">TOTAL PRESENT</td>'\n",
            "            +'<td style=\"padding:4px 6px;font-weight:900;color:#86efac;text-align:center\">'+presAM+'</td>'\n",
            "            +'<td style=\"padding:4px 6px;font-weight:900;color:#93c5fd;text-align:center\">'+presMP+'</td>'\n",
            "            +'<td colspan=\"2\" style=\"padding:4px 8px;color:#cbd5e1\">Absent: '+att.filter(r=>r.am==='A'&&r.pm==='A').length+'</td>'\n",
            "            +'</tr></tfoot></table></div>':'');\n",
            "        const fullHtml = html\n",
            "          +'<div style=\"margin-top:28px;display:flex;justify-content:space-between;border-top:1px solid #e2e8f0;padding-top:10px\">'\n",
            "          +'<div style=\"width:180px;text-align:center\"><div style=\"border-top:1px solid #374151;padding-top:3px;font-size:10px\">Signature Site Engineer</div></div>'\n",
            "          +'<div style=\"width:180px;text-align:center\"><div style=\"border-top:1px solid #374151;padding-top:3px;font-size:10px\">Signature Site Incharge</div></div>'\n",
            "          +'</div>'\n",
            "          +'<div style=\"text-align:center;margin-top:14px\">'\n",
            "          +'<button onclick=\"window.print()\" style=\"padding:8px 24px;background:#1e293b;color:white;border:none;border-radius:6px;font-size:13px;font-weight:700;cursor:pointer\">Print</button>'\n",
            "          +'<button onclick=\"window.close()\" style=\"margin-left:10px;padding:8px 16px;background:#e2e8f0;color:#374151;border:none;border-radius:6px;font-size:13px;cursor:pointer\">Close</button>'\n",
            "          +'</div></body></html>';\n",
            "        pw.document.open();\n",
            "        pw.document.write(fullHtml);\n",
            "        pw.document.close();\n",
            "        pw.focus();\n",
            "      };\n",
        ]
        lines[hp:func_end+1] = new_fn
        changes += 1
        print(f"FIX 2: handlePrintDPR rewritten - window.open BEFORE await")

# ================================================================
# FIX 3: handleSave - await the attendance save
# Change: saveAttendance(...).catch(()=>{})
# To: await saveAttendance(...);
# ================================================================
dr = find("const DailyReports = ({")
for j in range(dr, min(dr+200, len(lines))):
    if "_attRows.length > 0" in lines[j] and "saveAttendance" in lines[j] and ".catch" in lines[j]:
        lines[j] = lines[j].replace(
            "saveAttendance(_dprId, _attRows).catch(()=>{});",
            "await saveAttendance(_dprId, _attRows);"
        )
        changes += 1
        print(f"FIX 3: attendance save is now awaited at L{j+1}")
        break

# ================================================================
# SAFETY CHECK
# ================================================================
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","insData","attRowsRef"]
failed = [c for c in checks if c not in out]
if failed:
    print("\nSAFETY FAIL:", failed)
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print(f"\nSaved OK. Lines: {len(lines)}")

print(f"\nTOTAL CHANGES: {changes}")
print("\nRUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js && git commit -m "Fix: DPR print+attendance save+ID" && git push')
input("\nPress Enter...")
