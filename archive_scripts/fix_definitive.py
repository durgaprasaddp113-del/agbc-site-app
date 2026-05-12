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

# Show full useEffect and mp definition
print("── Full useEffect L3574 ──")
print(s(lines[3573].rstrip()))

print("\n── mp definition in list ──")
dr = find("const DailyReports = ({")
if dr != -1:
    for j in range(dr, min(dr+900,len(lines))):
        if "const mp" in lines[j] or ("mp=" in lines[j] and "manpower" in lines[j].lower()):
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:120])

print("\n── useDailyReports hook return ──")
udr = find("function useDailyReports()")
if udr != -1:
    for j in range(udr, min(udr+200,len(lines))):
        if "return { reports" in lines[j] or ("return {" in lines[j] and j > udr+50):
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:160])
            break

print("\n── Print CSS ──")
for i,l in enumerate(lines):
    if "dpr-print-overlay" in l and ("media" in l or "display" in l or "visibility" in l):
        print("L"+str(i+1)+": "+s(l.rstrip())[:120])

print("\n── Print overlay in view return ──")
for i,l in enumerate(lines):
    if "dpr-print-overlay" in l and "div id" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:80])

# ══════════════════════════════════════════════════════════════════════
# FIX A: PRINT — replace useEffect+window.print with window.open sync
# Open window SYNCHRONOUSLY in handlePrintDPR, populate ASYNC
# This bypasses ALL popup/print blockers
# ══════════════════════════════════════════════════════════════════════

# Step 1: Replace handlePrintDPR (L3955) with window.open approach
hp = 3954  # 0-based
if "handlePrintDPR = " in lines[hp]:
    depth=0; end=hp
    for j in range(hp, min(hp+10,len(lines))):
        depth += lines[j].count('{') - lines[j].count('}')
        if depth<=0 and j>hp: end=j; break
    
    new_fn = [
        "      const handlePrintDPR = (rpt) => {\n",
        "        const proj = projects.find(p => p.id === rpt.pid);\n",
        "        const pw = window.open('','_blank','width=1100,height=800');\n",
        "        if (!pw) { showToast('Allow popups to print','error'); return; }\n",
        "        pw.document.write('<html><head><title>Loading...</title></head><body style=\"font-family:Arial;padding:20px\">Loading DPR...</body></html>');\n",
        "        loadAttendance(rpt.id).then(att => {\n",
        "          const presentAM = att.filter(r=>r.am==='P').length;\n",
        "          const presentPM = att.filter(r=>r.pm==='P').length;\n",
        "          const rows = att.map((r,i) => '<tr style=\"border-bottom:1px solid #e2e8f0\"><td style=\"padding:3px 6px;text-align:center;color:#94a3b8\">'+(i+1)+'</td><td style=\"padding:3px 6px;font-weight:700;color:#1d4ed8\">'+(r.empId||'--')+'</td><td style=\"padding:3px 6px;font-weight:600\">'+(r.name||'--')+'</td><td style=\"padding:3px 6px;color:#64748b\">'+(r.designation||'--')+'</td><td style=\"padding:3px 6px;text-align:center;color:#7c3aed;font-weight:700\">'+(r.teamNo||'--')+'</td><td style=\"padding:3px 6px;text-align:center;font-weight:900;color:'+(r.am===\"P\"?'#15803d':'#b91c1c')+'\">'+(r.am||'P')+'</td><td style=\"padding:3px 6px;text-align:center;font-weight:900;color:'+(r.pm===\"P\"?'#15803d':'#b91c1c')+'\">'+(r.pm||'P')+'</td><td style=\"padding:3px 6px;text-align:center;color:#d97706\">'+(r.ot&&r.ot!=='0'?r.ot:'--')+'</td><td style=\"padding:3px 6px;color:#475569\">'+(r.description||'--')+'</td></tr>').join('');\n",
        "          const html = '<!DOCTYPE html><html><head><title>'+rpt.reportNum+'</title>'\n",
        "            +'<style>body{font-family:Arial,sans-serif;font-size:12px;color:#1e293b;margin:0;padding:16px}'\n",
        "            +'@page{size:A4 landscape;margin:12mm}table{border-collapse:collapse;width:100%}</style></head><body>'\n",
        "            +'<div style=\"text-align:center;border-bottom:3px double #1e293b;padding-bottom:8px;margin-bottom:10px\">'\n",
        "            +'<div style=\"font-size:16px;font-weight:900\">AL GHAITH BUILDING CONSTRUCTION LLC</div>'\n",
        "            +'<div style=\"font-size:12px;font-weight:700;color:#d97706\">SITE DAILY REPORT</div></div>'\n",
        "            +'<table style=\"margin-bottom:10px;border:1px solid #e2e8f0\"><tr style=\"background:#f8fafc\">'\n",
        "            +'<td style=\"padding:4px 8px\"><b>Site:</b> '+(proj?proj.number:'--')+'</td>'\n",
        "            +'<td style=\"padding:4px 8px\"><b>Project:</b> '+(proj?proj.name:'--')+'</td>'\n",
        "            +'<td style=\"padding:4px 8px\"><b>Date:</b> '+(rpt.date||'--')+'</td>'\n",
        "            +'<td style=\"padding:4px 8px\"><b>Report No:</b> '+(rpt.reportNum||'--')+'</td>'\n",
        "            +'</tr><tr>'\n",
        "            +'<td style=\"padding:4px 8px\"><b>Prepared By:</b> '+(rpt.preparedBy||'--')+'</td>'\n",
        "            +'<td style=\"padding:4px 8px\"><b>Weather:</b> '+(rpt.weather||'--')+' '+(rpt.temp?rpt.temp+'C':'')+'</td>'\n",
        "            +'<td style=\"padding:4px 8px\"><b>Work Hours:</b> '+(rpt.workHours||'8')+'h</td>'\n",
        "            +'<td style=\"padding:4px 8px\"><b>Status:</b> '+(rpt.status||'--')+'</td>'\n",
        "            +'</tr></table>'\n",
        "            +(att.length>0?'<div style=\"margin-bottom:12px\">'\n",
        "            +'<div style=\"background:#1e293b;color:white;padding:5px 10px;font-weight:700;font-size:11px\">MANPOWER ATTENDANCE | Total: '+att.length+' | AM Present: '+presentAM+' | PM Present: '+presentPM+'</div>'\n",
        "            +'<table style=\"font-size:10px\"><thead><tr style=\"background:#f1f5f9\">'\n",
        "            +['S.No','ID No','Name','Designation','Team','A.M','P.M','O.T','Description of Work'].map(h=>'<th style=\"padding:4px 6px;text-align:left;font-weight:700;color:#475569;border-bottom:2px solid #e2e8f0\">'+h+'</th>').join('')\n",
        "            +'</tr></thead><tbody>'+rows+'</tbody>'\n",
        "            +'<tfoot><tr style=\"background:#1e293b;color:white\">'\n",
        "            +'<td colspan=\"5\" style=\"padding:4px 8px;font-weight:700;font-size:10px\">TOTAL PRESENT</td>'\n",
        "            +'<td style=\"padding:4px 6px;font-weight:900;color:#86efac;text-align:center\">'+presentAM+'</td>'\n",
        "            +'<td style=\"padding:4px 6px;font-weight:900;color:#93c5fd;text-align:center\">'+presentPM+'</td>'\n",
        "            +'<td colspan=\"2\" style=\"padding:4px 8px;color:#cbd5e1;font-size:10px\">Absent: '+att.filter(r=>r.am==='A'&&r.pm==='A').length+'</td>'\n",
        "            +'</tr></tfoot></table></div>':'')\n",
        "            +'<div style=\"margin-top:28px;display:flex;justify-content:space-between;border-top:1px solid #e2e8f0;padding-top:10px\">'\n",
        "            +'<div style=\"width:180px;text-align:center\"><div style=\"border-top:1px solid #374151;padding-top:3px;font-size:10px\">Signature Site Engineer</div></div>'\n",
        "            +'<div style=\"width:180px;text-align:center\"><div style=\"border-top:1px solid #374151;padding-top:3px;font-size:10px\">Signature Site Incharge</div></div>'\n",
        "            +'</div>'\n",
        "            +'<div style=\"text-align:center;margin-top:14px\">'\n",
        "            +'<button onclick=\"window.print()\" style=\"padding:8px 24px;background:#1e293b;color:white;border:none;border-radius:6px;font-size:13px;font-weight:700;cursor:pointer\">Print</button>'\n",
        "            +'<button onclick=\"window.close()\" style=\"margin-left:10px;padding:8px 16px;background:#e2e8f0;color:#374151;border:none;border-radius:6px;font-size:13px;cursor:pointer\">Close</button>'\n",
        "            +'</div></body></html>';\n",
        "          pw.document.open(); pw.document.write(html); pw.document.close();\n",
        "        });\n",
        "      };\n",
    ]
    lines[hp:end+1] = new_fn
    changes += 1
    print("\nFIX A: handlePrintDPR uses window.open sync approach")

# ══════════════════════════════════════════════════════════════════════
# FIX B: MANPOWER COUNT
# Expose reload from useDailyReports and call after saveAttendance
# ══════════════════════════════════════════════════════════════════════

# Step B1: Add reload to useDailyReports return
udr = find("function useDailyReports()")
if udr != -1:
    for j in range(udr, min(udr+200,len(lines))):
        if "return { reports, loading, add, update" in lines[j]:
            if "reload" not in lines[j]:
                lines[j] = lines[j].replace(
                    "return { reports, loading, add, update",
                    "return { reports, loading, add, update, reload: loadData"
                )
                changes += 1
                print("FIX B1: reload exposed from useDailyReports at L"+str(j+1))
            break

# Step B2: Destructure reload in App()
for i,l in enumerate(lines):
    if "useDailyReports()" in l and "rlLoad" in l and "reload" not in l:
        lines[i] = l.replace("remove: delR }", "remove: delR, reload: reloadDpr }")
        changes += 1
        print("FIX B2: reloadDpr added to App destructure at L"+str(i+1))
        break

# Step B3: Pass reloadDpr to DailyReports component in App
for i,l in enumerate(lines):
    if 'case "reports"' in l and "DailyReports" in l and "reloadDpr" not in l:
        lines[i] = l.replace("onDelete={delR}", "onDelete={delR} onReload={reloadDpr}")
        changes += 1
        print("FIX B3: onReload passed to DailyReports at L"+str(i+1))
        break

# Step B4: Accept onReload in DailyReports props
dr = find("const DailyReports = ({")
if dr != -1 and "onReload" not in lines[dr]:
    lines[dr] = lines[dr].replace(
        "subcontractors = [], onReload",
        "subcontractors = [], onReload"  # already there?
    )
    if "onReload" not in lines[dr]:
        lines[dr] = lines[dr].replace(
            "subcontractors = []",
            "subcontractors = [], onReload"
        )
        changes += 1
        print("FIX B4: onReload prop in DailyReports at L"+str(dr+1))
    else:
        print("SKIP B4: onReload already in DailyReports props")

# Step B5: Call onReload after saveAttendance in handleSave
if dr != -1:
    for j in range(dr, min(dr+450,len(lines))):
        if "saveAttendance(_dprId, _attRows)" in lines[j]:
            if "onReload" not in lines[j]:
                lines[j] = lines[j].replace(
                    ".catch(()=>{});",
                    ".then(()=>{ setTimeout(()=>{ if(onReload) onReload(); },500); }).catch(()=>{});"
                )
                changes += 1
                print("FIX B5: onReload called after saveAttendance at L"+str(j+1))
            else:
                print("SKIP B5: onReload already in chain")
            break

# WRITE
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","window.open"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL: "+str(failed))
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("\nSaved OK. Lines: "+str(len(lines)))

print("TOTAL CHANGES: "+str(changes))
print("\nRUN: set CI=false && npm run build")
input("\nPress Enter...")
