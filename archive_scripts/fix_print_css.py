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

# ── APPROACH: Replace iframe print with CSS print overlay ────────────
# 1. Add printData state to DailyReports
# 2. handlePrintDPR sets printData instead of writing to iframe
# 3. Render a hidden print div in DailyReports return
# 4. CSS @media print shows only that div

# STEP A: Add printData state after mpAttDprId state
mpatt = find("const [mpAttDprId, setMpAttDprId] = useState(null);")
if mpatt != -1 and "printData" not in lines[mpatt+1]:
    lines.insert(mpatt+1, "  const [printData, setPrintData] = useState(null);\n")
    changes += 1
    print(f"STEP A: printData state added at L{mpatt+2}")

# STEP B: Replace handlePrintDPR to use setPrintData instead of iframe
hp = find("handlePrintDPR = async")
if hp != -1:
    # Find the end of this function
    depth = 0
    func_end = -1
    for j in range(hp, min(hp+120, len(lines))):
        depth += lines[j].count('{') - lines[j].count('}')
        if depth <= 0 and j > hp:
            func_end = j
            break
    if func_end != -1:
        print(f"STEP B: handlePrintDPR L{hp+1} to L{func_end+1} - replacing...")
        # Build new function lines
        new_fn = [
            "      const handlePrintDPR = async (rpt) => {\n",
            "        const proj = projects.find(p => p.id === rpt.pid);\n",
            "        const att = await loadAttendance(rpt.id);\n",
            "        setPrintData({ rpt, proj, att });\n",
            "        setTimeout(() => window.print(), 300);\n",
            "      };\n",
        ]
        lines[hp:func_end+1] = new_fn
        changes += 1
        print(f"STEP B: handlePrintDPR simplified - now uses setPrintData")

# STEP C: Add print CSS to the page and print div before closing return
# Find the closing </div> of DailyReports return
dr = find("const DailyReports = ({")
# Find the last return in DailyReports - look for the list return
list_return = -1
if dr != -1:
    for j in range(dr+400, min(dr+2000, len(lines))):
        if "return (" in lines[j] and j > dr+400:
            list_return = j
            break

# Insert print overlay and CSS just before the final return of DailyReports list view
if list_return != -1 and "DprPrintOverlay" not in "".join(lines[list_return:list_return+5]):
    print_overlay = [
        "      {/* CSS Print Overlay */}\n",
        "      <style dangerouslySetInnerHTML={{__html:`\n",
        "        @media print {\n",
        "          body > * { display: none !important; }\n",
        "          #dpr-print-overlay { display: block !important; }\n",
        "        }\n",
        "        #dpr-print-overlay { display: none; }\n",
        "        @page { size: A4 landscape; margin: 12mm; }\n",
        "      `}}/>\n",
        "      {printData && (\n",
        "        <div id=\"dpr-print-overlay\" style={{fontFamily:'Arial,sans-serif',fontSize:'12px',color:'#1e293b',padding:'16px'}}>\n",
        "          <div style={{textAlign:'center',borderBottom:'3px double #1e293b',paddingBottom:'8px',marginBottom:'10px'}}>\n",
        "            <div style={{fontSize:'16px',fontWeight:'900'}}>AL GHAITH BUILDING CONSTRUCTION LLC</div>\n",
        "            <div style={{fontSize:'12px',fontWeight:'700',color:'#d97706'}}>SITE DAILY REPORT</div>\n",
        "          </div>\n",
        "          <table style={{width:'100%',borderCollapse:'collapse',marginBottom:'10px',border:'1px solid #e2e8f0'}}><tbody>\n",
        "            <tr style={{background:'#f8fafc'}}>\n",
        "              <td style={{padding:'4px 8px'}}><b>Site No:</b> {printData.proj?.number||'--'}</td>\n",
        "              <td style={{padding:'4px 8px'}}><b>Project:</b> {printData.proj?.name||'--'}</td>\n",
        "              <td style={{padding:'4px 8px'}}><b>Date:</b> {printData.rpt.date||'--'}</td>\n",
        "              <td style={{padding:'4px 8px'}}><b>Report No:</b> {printData.rpt.reportNum||'--'}</td>\n",
        "            </tr><tr>\n",
        "              <td style={{padding:'4px 8px'}}><b>Prepared By:</b> {printData.rpt.preparedBy||'--'}</td>\n",
        "              <td style={{padding:'4px 8px'}}><b>Weather:</b> {printData.rpt.weather||'--'} {printData.rpt.temp?printData.rpt.temp+'C':''}</td>\n",
        "              <td style={{padding:'4px 8px'}}><b>Work Hours:</b> {printData.rpt.workHours||'8'}h</td>\n",
        "              <td style={{padding:'4px 8px'}}><b>Status:</b> {printData.rpt.status||'--'}</td>\n",
        "            </tr>\n",
        "          </tbody></table>\n",
        "          {printData.att.length>0&&(\n",
        "            <div style={{marginBottom:'12px'}}>\n",
        "              <div style={{background:'#1e293b',color:'white',padding:'5px 10px',fontWeight:'700',fontSize:'11px'}}>\n",
        "                MANPOWER ATTENDANCE | Total: {printData.att.length} | AM Present: {printData.att.filter(r=>r.am==='P').length} | PM Present: {printData.att.filter(r=>r.pm==='P').length}\n",
        "              </div>\n",
        "              <table style={{width:'100%',borderCollapse:'collapse',fontSize:'10px'}}><thead>\n",
        "                <tr style={{background:'#f1f5f9'}}>{['S.No','ID No','Name','Designation','Team','A.M','P.M','O.T','Description of Work'].map(h=>(<th key={h} style={{padding:'4px 6px',textAlign:'left',fontWeight:'700',color:'#475569',borderBottom:'2px solid #e2e8f0'}}>{h}</th>))}</tr>\n",
        "              </thead><tbody>\n",
        "                {printData.att.map((r,i)=>(\n",
        "                  <tr key={i} style={{borderBottom:'1px solid #e2e8f0',background:r.am==='A'&&r.pm==='A'?'#fff5f5':''}}>\n",
        "                    <td style={{padding:'3px 6px',textAlign:'center',color:'#94a3b8'}}>{i+1}</td>\n",
        "                    <td style={{padding:'3px 6px',fontWeight:'700',color:'#1d4ed8'}}>{r.empId||'--'}</td>\n",
        "                    <td style={{padding:'3px 6px',fontWeight:'600'}}>{r.name||'--'}</td>\n",
        "                    <td style={{padding:'3px 6px',color:'#64748b'}}>{r.designation||'--'}</td>\n",
        "                    <td style={{padding:'3px 6px',textAlign:'center',color:'#7c3aed',fontWeight:'700'}}>{r.teamNo||'--'}</td>\n",
        "                    <td style={{padding:'3px 6px',textAlign:'center',fontWeight:'900',color:r.am==='P'?'#15803d':'#b91c1c'}}>{r.am}</td>\n",
        "                    <td style={{padding:'3px 6px',textAlign:'center',fontWeight:'900',color:r.pm==='P'?'#15803d':'#b91c1c'}}>{r.pm}</td>\n",
        "                    <td style={{padding:'3px 6px',textAlign:'center',color:'#d97706'}}>{r.ot&&r.ot!=='0'?r.ot:'--'}</td>\n",
        "                    <td style={{padding:'3px 6px',color:'#475569'}}>{r.description||'--'}</td>\n",
        "                  </tr>\n",
        "                ))}\n",
        "              </tbody><tfoot><tr style={{background:'#1e293b',color:'white'}}>\n",
        "                <td colSpan={5} style={{padding:'4px 8px',fontWeight:'700',fontSize:'10px'}}>TOTAL PRESENT</td>\n",
        "                <td style={{padding:'4px 6px',fontWeight:'900',color:'#86efac',textAlign:'center'}}>{printData.att.filter(r=>r.am==='P').length}</td>\n",
        "                <td style={{padding:'4px 6px',fontWeight:'900',color:'#93c5fd',textAlign:'center'}}>{printData.att.filter(r=>r.pm==='P').length}</td>\n",
        "                <td colSpan={2} style={{padding:'4px 8px',color:'#cbd5e1',fontSize:'10px'}}>Absent: {printData.att.filter(r=>r.am==='A'&&r.pm==='A').length}</td>\n",
        "              </tr></tfoot></table>\n",
        "            </div>\n",
        "          )}\n",
        "          <div style={{marginTop:'30px',display:'flex',justifyContent:'space-between',borderTop:'1px solid #e2e8f0',paddingTop:'12px'}}>\n",
        "            <div style={{width:'180px',textAlign:'center'}}><div style={{borderTop:'1px solid #374151',paddingTop:'3px',fontSize:'10px'}}>Signature Site Engineer</div></div>\n",
        "            <div style={{width:'180px',textAlign:'center'}}><div style={{borderTop:'1px solid #374151',paddingTop:'3px',fontSize:'10px'}}>Signature Site Incharge</div></div>\n",
        "          </div>\n",
        "        </div>\n",
        "      )}\n",
    ]
    for k, ln in enumerate(print_overlay):
        lines.insert(list_return + k, ln)
    changes += 1
    print(f"STEP C: Print overlay JSX added at L{list_return+1}")

# SAFETY CHECK
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","printData","setPrintData"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL:", failed)
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print(f"\nSaved OK. Lines: {len(lines)}")

print(f"TOTAL CHANGES: {changes}")
print("\nRUN: set CI=false && npm run build")
input("\nPress Enter...")
