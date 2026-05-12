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

# ── Show current structure ────────────────────────────────────────────
dr = find("const DailyReports = ({")
print("DR at L" + str(dr+1))

# Find view mode return
view_ret = -1
for j in range(dr, min(dr+1600, len(lines))):
    if 'mode==="view"&&sel' in lines[j]:
        view_ret = j
        break
print("View mode at L" + str(view_ret+1))

# Find where view mode return ends (closing </div> before next return)
view_end = -1
if view_ret != -1:
    depth = 0
    in_return = False
    for j in range(view_ret, min(view_ret+600, len(lines))):
        if 'return (' in lines[j] and j > view_ret:
            in_return = True
        if in_return:
            depth += lines[j].count('(') - lines[j].count(')')
            if depth <= 0 and j > view_ret + 20:
                view_end = j
                break
print("View return ends at L" + str(view_end+1) if view_end!=-1 else "View end NOT FOUND")

# Find print overlay start
overlay_start = find("dpr-print-overlay")
print("Print overlay at L" + str(overlay_start+1) if overlay_start!=-1 else "Overlay NOT FOUND")

# ── FIX 1: Add CSS style tag just before view mode if block ──────────
# The <style> with @media print needs to be in DOM at all times
# Currently it's only inside the list return
# Fix: move it before the view return block

if view_ret != -1:
    # Check if style tag already exists near view return
    nearby = "".join(lines[max(0,view_ret-5):view_ret+5])
    if "dpr-print-overlay" not in nearby:
        # Insert the CSS style before the view mode block
        css_block = (
            '      <style dangerouslySetInnerHTML={{__html:`'
            '@media print {'
            ' * { visibility: hidden !important; }'
            ' #dpr-print-overlay { display: block !important; }'
            ' #dpr-print-overlay, #dpr-print-overlay * { visibility: visible !important; }'
            ' #dpr-print-overlay { position:fixed;top:0;left:0;width:100%;background:white; }'
            '}'
            ' #dpr-print-overlay { display: none; }'
            '`}}/>\n'
        )
        # We need to insert this as a Fragment wrapper
        # Actually the style tag needs to be inside JSX
        # Better: just insert the style and overlay INSIDE the view return
        print("Need to add overlay inside view return")
    else:
        print("Style already near view return")

# ── FIX 1 (REAL): Insert print overlay + style at START of view return
# Find the opening <div of view return
if view_ret != -1:
    # Find the return ( line
    for j in range(view_ret, min(view_ret+10, len(lines))):
        if 'return (' in lines[j]:
            # Find the opening <div of the return
            for k in range(j, min(j+5, len(lines))):
                if '<div' in lines[k] and 'className' in lines[k]:
                    # Insert after this opening div
                    check_ctx = "".join(lines[k:min(k+10,len(lines))])
                    if "dpr-print-overlay" not in "".join(lines[max(0,k-5):k+20]):
                        overlay_jsx = (
                            '            {/* Print Overlay - needed in view mode */}\n'
                            '            {printData&&<div id="dpr-print-overlay" style={{fontFamily:"Arial,sans-serif",fontSize:"12px",color:"#1e293b",padding:"16px"}}>\n'
                            '              <div style={{textAlign:"center",borderBottom:"3px double #1e293b",paddingBottom:"8px",marginBottom:"10px"}}>\n'
                            '                <div style={{fontSize:"16px",fontWeight:"900"}}>AL GHAITH BUILDING CONSTRUCTION LLC</div>\n'
                            '                <div style={{fontSize:"12px",fontWeight:"700",color:"#d97706"}}>SITE DAILY REPORT</div>\n'
                            '              </div>\n'
                            '              <table style={{width:"100%",borderCollapse:"collapse",marginBottom:"10px",border:"1px solid #e2e8f0"}}><tbody>\n'
                            '                <tr style={{background:"#f8fafc"}}>\n'
                            '                  <td style={{padding:"4px 8px"}}><b>Site No:</b> {printData.proj?.number||"--"}</td>\n'
                            '                  <td style={{padding:"4px 8px"}}><b>Project:</b> {printData.proj?.name||"--"}</td>\n'
                            '                  <td style={{padding:"4px 8px"}}><b>Date:</b> {printData.rpt.date||"--"}</td>\n'
                            '                  <td style={{padding:"4px 8px"}}><b>Report No:</b> {printData.rpt.reportNum||"--"}</td>\n'
                            '                </tr><tr>\n'
                            '                  <td style={{padding:"4px 8px"}}><b>Prepared By:</b> {printData.rpt.preparedBy||"--"}</td>\n'
                            '                  <td style={{padding:"4px 8px"}}><b>Weather:</b> {printData.rpt.weather||"--"}</td>\n'
                            '                  <td style={{padding:"4px 8px"}}><b>Work Hours:</b> {printData.rpt.workHours||"8"}h</td>\n'
                            '                  <td style={{padding:"4px 8px"}}><b>Status:</b> {printData.rpt.status||"--"}</td>\n'
                            '                </tr>\n'
                            '              </tbody></table>\n'
                            '              {printData.att&&printData.att.length>0&&<div style={{marginBottom:"12px"}}>\n'
                            '                <div style={{background:"#1e293b",color:"white",padding:"5px 10px",fontWeight:"700",fontSize:"11px"}}>MANPOWER ATTENDANCE | Total: {printData.att.length} | AM Present: {printData.att.filter(r=>r.am==="P").length} | PM Present: {printData.att.filter(r=>r.pm==="P").length}</div>\n'
                            '                <table style={{width:"100%",borderCollapse:"collapse",fontSize:"10px"}}><thead><tr style={{background:"#f1f5f9"}}>\n'
                            '                  {["S.No","ID","Name","Designation","Team","A.M","P.M","O.T","Description"].map(h=><th key={h} style={{padding:"4px 6px",textAlign:"left",fontWeight:"700",color:"#475569",borderBottom:"2px solid #e2e8f0"}}>{h}</th>)}\n'
                            '                </tr></thead><tbody>\n'
                            '                  {printData.att.map((r,i)=><tr key={i} style={{borderBottom:"1px solid #e2e8f0",background:r.am==="A"&&r.pm==="A"?"#fff5f5":""}}>\n'
                            '                    <td style={{padding:"3px 6px",textAlign:"center",color:"#94a3b8"}}>{i+1}</td>\n'
                            '                    <td style={{padding:"3px 6px",fontWeight:"700",color:"#1d4ed8"}}>{r.empId||"--"}</td>\n'
                            '                    <td style={{padding:"3px 6px",fontWeight:"600"}}>{r.name||"--"}</td>\n'
                            '                    <td style={{padding:"3px 6px",color:"#64748b"}}>{r.designation||"--"}</td>\n'
                            '                    <td style={{padding:"3px 6px",textAlign:"center",color:"#7c3aed",fontWeight:"700"}}>{r.teamNo||"--"}</td>\n'
                            '                    <td style={{padding:"3px 6px",textAlign:"center",fontWeight:"900",color:r.am==="P"?"#15803d":"#b91c1c"}}>{r.am}</td>\n'
                            '                    <td style={{padding:"3px 6px",textAlign:"center",fontWeight:"900",color:r.pm==="P"?"#15803d":"#b91c1c"}}>{r.pm}</td>\n'
                            '                    <td style={{padding:"3px 6px",textAlign:"center",color:"#d97706"}}>{r.ot&&r.ot!=="0"?r.ot:"--"}</td>\n'
                            '                    <td style={{padding:"3px 6px",color:"#475569"}}>{r.description||"--"}</td>\n'
                            '                  </tr>)}\n'
                            '                </tbody><tfoot><tr style={{background:"#1e293b",color:"white"}}>\n'
                            '                  <td colSpan={5} style={{padding:"4px 8px",fontWeight:"700",fontSize:"10px"}}>TOTAL PRESENT</td>\n'
                            '                  <td style={{padding:"4px 6px",fontWeight:"900",color:"#86efac",textAlign:"center"}}>{printData.att.filter(r=>r.am==="P").length}</td>\n'
                            '                  <td style={{padding:"4px 6px",fontWeight:"900",color:"#93c5fd",textAlign:"center"}}>{printData.att.filter(r=>r.pm==="P").length}</td>\n'
                            '                  <td colSpan={2} style={{padding:"4px 8px",color:"#cbd5e1",fontSize:"10px"}}>Absent: {printData.att.filter(r=>r.am==="A"&&r.pm==="A").length}</td>\n'
                            '                </tr></tfoot></table>\n'
                            '              </div>}\n'
                            '              <div style={{marginTop:"28px",display:"flex",justifyContent:"space-between",borderTop:"1px solid #e2e8f0",paddingTop:"10px"}}>\n'
                            '                <div style={{width:"180px",textAlign:"center"}}><div style={{borderTop:"1px solid #374151",paddingTop:"3px",fontSize:"10px"}}>Signature Site Engineer</div></div>\n'
                            '                <div style={{width:"180px",textAlign:"center"}}><div style={{borderTop:"1px solid #374151",paddingTop:"3px",fontSize:"10px"}}>Signature Site Incharge</div></div>\n'
                            '              </div>\n'
                            '            </div>}\n'
                        )
                        lines.insert(k+1, overlay_jsx)
                        changes += 1
                        print("FIX 1: Print overlay added inside VIEW return at L" + str(k+2))
                    break
            break

# ── FIX 2: openEdit — make async and await attendance pre-load ────────
if dr != -1:
    for j in range(dr, min(dr+200, len(lines))):
        l = lines[j]
        if "const openEdit" in l and "=>" in l and "rpt" in l:
            if "async" not in l:
                lines[j] = lines[j].replace("const openEdit = rpt =>", "const openEdit = async (rpt) =>")
                lines[j] = lines[j].replace("const openEdit = (rpt) =>", "const openEdit = async (rpt) =>")
                print("FIX 2a: openEdit async at L" + str(j+1))
                changes += 1
            # Find setMode("form") in openEdit body
            for k in range(j, min(j+15, len(lines))):
                if 'setMode("form")' in lines[k]:
                    ctx = "".join(lines[max(0,k-3):k])
                    if "await loadAttendance" not in ctx:
                        preload = '      const _preAtt = await loadAttendance(rpt&&rpt.id?rpt.id:""); if(_preAtt&&_preAtt.length) attRowsRef.current=_preAtt;\n'
                        lines.insert(k, preload)
                        changes += 1
                        print("FIX 2b: await pre-load at L" + str(k+1))
                    break
            break

# WRITE
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","attRowsRef","printData"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL: " + str(failed))
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("Saved OK. Lines: " + str(len(lines)))

print("TOTAL CHANGES: " + str(changes))
print("\nRUN: set CI=false && npm run build")
input("\nPress Enter...")
