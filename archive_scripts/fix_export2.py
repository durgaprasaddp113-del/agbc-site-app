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

# Show current handlePrintDPR
hp = find("const handlePrintDPR =")
print("handlePrintDPR at L"+str(hp+1) if hp!=-1 else "NOT FOUND")
if hp != -1:
    for j in range(hp, min(hp+5,len(lines))):
        print("  L"+str(j+1)+": "+s(lines[j].rstrip())[:100])

# ── Replace handlePrintDPR with HTML download (opens in browser, printable) ─
if hp != -1:
    depth=0; end=hp
    for j in range(hp, min(hp+60,len(lines))):
        depth += lines[j].count('{') - lines[j].count('}')
        if depth<=0 and j>hp: end=j; break

    # Use HTML file download - opens in any browser, user can print from there
    new_fn = [
        "      const handlePrintDPR = async (rpt) => {\n",
        "        showToast('Preparing report...');\n",
        "        const proj = projects.find(p => p.id === rpt.pid);\n",
        "        const att = await loadAttendance(rpt.id);\n",
        "        const pAM = att.filter(r=>r.am==='P').length;\n",
        "        const pPM = att.filter(r=>r.pm==='P').length;\n",
        "        const attHTML = att.length===0 ? '<p>No attendance records</p>' : (\n",
        "          '<table border=1 cellpadding=4 cellspacing=0 style=\"border-collapse:collapse;width:100%;font-size:11px\">'\n",
        "          +'<tr style=\"background:#1e293b;color:white\"><th>S.No</th><th>ID No</th><th>Name</th><th>Designation</th><th>Team</th><th>A.M</th><th>P.M</th><th>O.T</th><th>Description of Work</th></tr>'\n",
        "          +att.map((r,i)=>'<tr style=\"background:'+(r.am===\"A\"&&r.pm===\"A\"?\"#fff5f5\":i%2===0?\"#fff\":\"#f8fafc\")+'\">'\n",
        "            +'<td align=center>'+(i+1)+'</td>'\n",
        "            +'<td><b>'+(r.empId||'--')+'</b></td>'\n",
        "            +'<td><b>'+(r.name||'--')+'</b></td>'\n",
        "            +'<td>'+(r.designation||'--')+'</td>'\n",
        "            +'<td align=center><b>'+(r.teamNo||'--')+'</b></td>'\n",
        "            +'<td align=center style=\"color:'+(r.am===\"P\"?'green':'red')+';font-weight:bold\">'+(r.am||'P')+'</td>'\n",
        "            +'<td align=center style=\"color:'+(r.pm===\"P\"?'green':'red')+';font-weight:bold\">'+(r.pm||'P')+'</td>'\n",
        "            +'<td align=center>'+(r.ot&&r.ot!=='0'?r.ot:'--')+'</td>'\n",
        "            +'<td>'+(r.description||'--')+'</td>'\n",
        "            +'</tr>'\n",
        "          ).join('')\n",
        "          +'<tr style=\"background:#1e293b;color:white\"><td colspan=5><b>TOTAL PRESENT</b></td><td align=center><b>'+pAM+'</b></td><td align=center><b>'+pPM+'</b></td><td colspan=2>Absent: '+att.filter(r=>r.am===\"A\"&&r.pm===\"A\").length+'</td></tr>'\n",
        "          +'</table>'\n",
        "        );\n",
        "        const secHTML = (title,rows,heads,cols) => {\n",
        "          if(!rows||!rows.length) return '';\n",
        "          return '<h3 style=\"margin:16px 0 4px;color:#1e293b\">'+title+'</h3>'\n",
        "            +'<table border=1 cellpadding=4 cellspacing=0 style=\"border-collapse:collapse;width:100%;font-size:11px\">'\n",
        "            +'<tr style=\"background:#f1f5f9\">'+heads.map(h=>'<th>'+h+'</th>').join('')+'</tr>'\n",
        "            +rows.map(r=>'<tr>'+cols.map(c=>'<td>'+(r[c]||'--')+'</td>').join('')+'</tr>').join('')\n",
        "            +'</table>';\n",
        "        };\n",
        "        const html = '<!DOCTYPE html><html><head><meta charset=UTF-8>'\n",
        "          +'<title>'+(rpt.reportNum||'DPR')+'</title>'\n",
        "          +'<style>body{font-family:Arial,sans-serif;padding:20px;color:#1e293b}'\n",
        "          +'h1{font-size:18px;margin:0}h2{font-size:13px;color:#d97706;margin:2px 0 12px}'\n",
        "          +'table{page-break-inside:avoid}@media print{button{display:none}}'\n",
        "          +'</style></head><body>'\n",
        "          +'<div style=\"text-align:center;border-bottom:3px double #1e293b;padding-bottom:8px;margin-bottom:12px\">'\n",
        "          +'<h1>AL GHAITH BUILDING CONSTRUCTION LLC</h1>'\n",
        "          +'<h2>SITE DAILY REPORT</h2></div>'\n",
        "          +'<table border=1 cellpadding=5 cellspacing=0 style=\"border-collapse:collapse;width:100%;margin-bottom:12px\">'\n",
        "          +'<tr style=\"background:#f8fafc\">'\n",
        "          +'<td><b>Site No:</b> '+(proj?proj.number:'--')+'</td>'\n",
        "          +'<td><b>Project:</b> '+(proj?proj.name:'--')+'</td>'\n",
        "          +'<td><b>Date:</b> '+(rpt.date||'--')+'</td>'\n",
        "          +'<td><b>Report No:</b> '+(rpt.reportNum||'--')+'</td></tr>'\n",
        "          +'<tr><td><b>Prepared By:</b> '+(rpt.preparedBy||'--')+'</td>'\n",
        "          +'<td><b>Weather:</b> '+(rpt.weather||'--')+' '+(rpt.temp?rpt.temp+'C':'')+'</td>'\n",
        "          +'<td><b>Work Hours:</b> '+(rpt.workHours||'8')+'h</td>'\n",
        "          +'<td><b>Status:</b> '+(rpt.status||'--')+'</td></tr></table>'\n",
        "          +'<h3 style=\"margin:12px 0 4px;color:#1e293b\">MANPOWER ATTENDANCE | Total: '+att.length+' | AM Present: '+pAM+' | PM Present: '+pPM+'</h3>'\n",
        "          +attHTML\n",
        "          +secHTML('EQUIPMENT',rpt.equipment||[],['Equipment','Qty','Status','Operator','Remarks'],['name','qty','status','operator','remarks'])\n",
        "          +secHTML('WORK ACTIVITIES',rpt.activities||[],['Location','Activity','Trade','Progress%','Remarks'],['location','activity','trade','progress','remarks'])\n",
        "          +secHTML('MATERIALS',rpt.materials||[],['Material','Qty','Unit','Supplier','DN No'],['material','qty','unit','supplier','dn'])\n",
        "          +(rpt.issues?'<p><b>Issues/Delays:</b> '+rpt.issues+'</p>':'')\n",
        "          +(rpt.remarks?'<p><b>Remarks:</b> '+rpt.remarks+'</p>':'')\n",
        "          +'<div style=\"margin-top:40px;display:flex;justify-content:space-between\">'\n",
        "          +'<div style=\"width:200px;text-align:center\"><div style=\"border-top:1px solid #000;padding-top:4px\">Site Engineer</div></div>'\n",
        "          +'<div style=\"width:200px;text-align:center\"><div style=\"border-top:1px solid #000;padding-top:4px\">Site Incharge</div></div>'\n",
        "          +'</div>'\n",
        "          +'<div style=\"text-align:center;margin-top:20px\">'\n",
        "          +'<button onclick=\"window.print()\" style=\"padding:10px 30px;background:#1e293b;color:white;border:none;border-radius:6px;font-size:14px;font-weight:bold;cursor:pointer;margin-right:10px\">Print</button>'\n",
        "          +'<button onclick=\"window.close()\" style=\"padding:10px 20px;background:#e2e8f0;border:none;border-radius:6px;font-size:14px;cursor:pointer\">Close</button>'\n",
        "          +'</div></body></html>';\n",
        "        const blob = new Blob([html], {type:'text/html;charset=utf-8'});\n",
        "        const url = URL.createObjectURL(blob);\n",
        "        const a = document.createElement('a');\n",
        "        a.href=url; a.target='_blank'; a.rel='noopener';\n",
        "        document.body.appendChild(a); a.click();\n",
        "        document.body.removeChild(a);\n",
        "        setTimeout(()=>URL.revokeObjectURL(url), 5000);\n",
        "        showToast('Report opened! Use Ctrl+P to print from the new tab.');\n",
        "      };\n",
    ]
    lines[hp:end+1] = new_fn
    changes += 1
    print("\nFIX 1: Export replaced with HTML download")

# Change button label
for i,l in enumerate(lines):
    if "handlePrintDPR(sel)" in l and "button" in l:
        old = lines[i]
        lines[i] = lines[i].replace("Export Excel","Export / Print")
        lines[i] = lines[i].replace("Print DPR","Export / Print")
        if lines[i] != old:
            changes += 1
            print("FIX 2: Button label updated at L"+str(i+1))
        break

# WRITE
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","showToast","DprAttendancePanel"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL: "+str(failed))
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("\nSaved OK. Lines: "+str(len(lines)))

print("TOTAL CHANGES: "+str(changes))
print("\nRUN: set CI=false && npm run build && npx vercel --prod --force")
input("\nPress Enter...")
