import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# Replace the entire handlePrintDPR with a version that uses
# document.write on a hidden iframe - this bypasses ALL restrictions
old_fn_start = "      const handlePrintDPR = async (rpt) => {"
old_fn_end = "        showToast('Report downloaded! Open the file and press Ctrl+P to print.');\n      };"

start_idx = content.find(old_fn_start)
end_idx = content.find(old_fn_end)

if start_idx != -1 and end_idx != -1:
    end_idx += len(old_fn_end)
    
    new_fn = """      const handlePrintDPR = async (rpt) => {
        showToast('Loading report...');
        const proj = projects.find(p => p.id === rpt.pid);
        const att = await loadAttendance(rpt.id);
        const pAM = att.filter(r=>r.am==='P').length;
        const pPM = att.filter(r=>r.pm==='P').length;
        const rows = att.map((r,i)=>
          '<tr style="background:'+(i%2===0?'#fff':'#f8fafc')+'">'
          +'<td style="padding:4px;text-align:center;border:1px solid #e2e8f0">'+(i+1)+'</td>'
          +'<td style="padding:4px;border:1px solid #e2e8f0;font-weight:bold;color:#1d4ed8">'+(r.empId||'')+'</td>'
          +'<td style="padding:4px;border:1px solid #e2e8f0;font-weight:600">'+(r.name||'')+'</td>'
          +'<td style="padding:4px;border:1px solid #e2e8f0">'+(r.designation||'')+'</td>'
          +'<td style="padding:4px;border:1px solid #e2e8f0;text-align:center">'+(r.teamNo||'')+'</td>'
          +'<td style="padding:4px;border:1px solid #e2e8f0;text-align:center;font-weight:900;color:'+(r.am==='P'?'green':'red')+'">'+(r.am)+'</td>'
          +'<td style="padding:4px;border:1px solid #e2e8f0;text-align:center;font-weight:900;color:'+(r.pm==='P'?'green':'red')+'">'+(r.pm)+'</td>'
          +'<td style="padding:4px;border:1px solid #e2e8f0;text-align:center">'+(r.ot&&r.ot!=='0'?r.ot:'')+'</td>'
          +'<td style="padding:4px;border:1px solid #e2e8f0">'+(r.description||'')+'</td>'
          +'</tr>'
        ).join('');
        const html = '<!DOCTYPE html><html><head><meta charset=UTF-8><title>'+rpt.reportNum+'</title>'
          +'<style>*{box-sizing:border-box}body{font-family:Arial,sans-serif;font-size:12px;margin:0;padding:16px}'
          +'@page{size:A4 landscape;margin:10mm}@media print{.noprint{display:none}}'
          +'table{border-collapse:collapse;width:100%}th{background:#1e293b;color:white;padding:5px;font-size:11px}'
          +'</style></head><body>'
          +'<div style="text-align:center;border-bottom:3px double #333;padding-bottom:8px;margin-bottom:10px">'
          +'<div style="font-size:18px;font-weight:900">AL GHAITH BUILDING CONSTRUCTION (LLC)</div>'
          +'<div style="font-size:13px;font-weight:700;color:#b45309">SITE DAILY REPORT</div></div>'
          +'<table style="margin-bottom:10px"><tbody>'
          +'<tr><td style="padding:4px 8px;border:1px solid #e2e8f0"><b>Site No:</b> '+(proj?proj.number:'')+'</td>'
          +'<td style="padding:4px 8px;border:1px solid #e2e8f0"><b>Project:</b> '+(proj?proj.name:'')+'</td>'
          +'<td style="padding:4px 8px;border:1px solid #e2e8f0"><b>Date:</b> '+rpt.date+'</td>'
          +'<td style="padding:4px 8px;border:1px solid #e2e8f0"><b>Report No:</b> '+rpt.reportNum+'</td></tr>'
          +'<tr><td style="padding:4px 8px;border:1px solid #e2e8f0"><b>Prepared By:</b> '+(rpt.preparedBy||'')+'</td>'
          +'<td style="padding:4px 8px;border:1px solid #e2e8f0"><b>Weather:</b> '+(rpt.weather||'')+' '+(rpt.temp?rpt.temp+'C':'')+'</td>'
          +'<td style="padding:4px 8px;border:1px solid #e2e8f0"><b>Work Hours:</b> '+(rpt.workHours||'8')+'h</td>'
          +'<td style="padding:4px 8px;border:1px solid #e2e8f0"><b>Status:</b> '+rpt.status+'</td></tr>'
          +'</tbody></table>'
          +(att.length>0
            ?'<table><thead><tr><th>S.No</th><th>ID No</th><th>Name</th><th>Designation</th><th>Team</th><th>A.M</th><th>P.M</th><th>O.T</th><th>Description of Work</th></tr></thead>'
            +'<tbody>'+rows+'</tbody>'
            +'<tfoot><tr style="background:#1e293b;color:white"><td colspan=5 style="padding:4px 8px"><b>TOTAL PRESENT</b></td>'
            +'<td style="padding:4px;text-align:center"><b>'+pAM+'</b></td>'
            +'<td style="padding:4px;text-align:center"><b>'+pPM+'</b></td>'
            +'<td colspan=2 style="padding:4px 8px">Total: '+att.length+' | Absent: '+att.filter(r=>r.am==='A'&&r.pm==='A').length+'</td>'
            +'</tr></tfoot></table>'
            :'<p>No attendance records</p>')
          +'<div style="margin-top:40px;display:flex;justify-content:space-between;border-top:1px solid #333;padding-top:12px">'
          +'<div style="width:200px;text-align:center"><div style="border-top:1px solid #333;margin-top:30px;padding-top:4px;font-size:11px">Signature Site Engineer</div></div>'
          +'<div style="width:200px;text-align:center"><div style="border-top:1px solid #333;margin-top:30px;padding-top:4px;font-size:11px">Signature Site Incharge</div></div>'
          +'</div>'
          +'<div class=noprint style="text-align:center;margin-top:16px">'
          +'<button onclick="window.print()" style="padding:10px 32px;background:#1e293b;color:white;border:none;border-radius:6px;font-size:14px;font-weight:bold;cursor:pointer;margin-right:8px">&#128424; Print / Save PDF</button>'
          +'<button onclick="window.close()" style="padding:10px 20px;background:#e2e8f0;border:none;border-radius:6px;font-size:14px;cursor:pointer">Close</button>'
          +'</div></body></html>';
        const f = document.createElement('iframe');
        f.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;border:0;z-index:99999;background:white';
        f.srcdoc = html;
        document.body.appendChild(f);
        f.onload = () => {
          const closeBtn = f.contentDocument.querySelector('button:last-child');
          if(closeBtn) closeBtn.onclick = () => { document.body.removeChild(f); };
        };
        showToast('Report ready!');
      };"""
    
    content = content[:start_idx] + new_fn + content[end_idx:]
    changes += 1
    print("FIX: handlePrintDPR replaced with iframe approach")

with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print("Saved. Changes:", changes)
print("RUN: set CI=false && npm run build && npx vercel --prod --force")
input("Press Enter...")
