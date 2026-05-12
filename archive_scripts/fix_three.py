import shutil, re
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
dr = find("const DailyReports = ({")

# ── SHOW CURRENT STATE ────────────────────────────────────────────────
print("── SECTIONS array (tab badges) ──")
if dr != -1:
    for j in range(dr, min(dr+800,len(lines))):
        if "SECTIONS" in lines[j] and ("manpower" in lines[j].lower() or "Manpower" in lines[j]):
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:140])

print("\n── List row mp variable ──")
if dr != -1:
    for j in range(dr, min(dr+900,len(lines))):
        if "const mp" in lines[j] and j > dr+300:
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:120])

# ══════════════════════════════════════════════════════════════════════
# FIX 1: Manpower tab badge — change from form.manpower.length 
# to attRowsRef.current.length
# ══════════════════════════════════════════════════════════════════════
if dr != -1:
    for j in range(dr, min(dr+800,len(lines))):
        l = lines[j]
        # Find: {id:"manpower",label:`? Manpower (${...form.manpower...})`}
        if '"manpower"' in l and 'label:' in l and 'Manpower' in l:
            old = lines[j]
            # Replace the count part
            lines[j] = re.sub(
                r'\$\{[^}]*form\.manpower[^}]*\}',
                '${(attRowsRef.current||[]).length}',
                lines[j]
            )
            if lines[j] != old:
                changes += 1
                print("FIX 1: Manpower tab badge now uses attRowsRef at L"+str(j+1))
            else:
                print("WARN 1: Manpower tab badge pattern not matched at L"+str(j+1))
                print("  Content: "+s(old.rstrip())[:120])
            break

# ══════════════════════════════════════════════════════════════════════
# FIX 2: List row mp — already fixed? Check and fix if needed
# ══════════════════════════════════════════════════════════════════════
if dr != -1:
    for j in range(dr, min(dr+900,len(lines))):
        if "const mp=" in lines[j] and "reduce" in lines[j] and j > dr+300:
            lines[j] = re.sub(
                r'const mp=\(r\.manpower\|\|\[\]\)\.reduce\([^;]+\);',
                'const mp = r.manpowerTotal || 0;',
                lines[j]
            )
            changes += 1
            print("FIX 2: List row mp fixed at L"+str(j+1))
            break
        elif "const mp = r.manpowerTotal" in lines[j] and j > dr+300:
            print("SKIP 2: Already fixed at L"+str(j+1))
            break

# ══════════════════════════════════════════════════════════════════════
# FIX 3: Print — add CSS print approach as ALTERNATIVE to window.open
# Add a "Download/Print" button that uses window.print() with CSS overlay
# The window.open approach works but browser blocks it
# Fix: keep window.open but also show the content in a modal that can print
# ══════════════════════════════════════════════════════════════════════
# Change handlePrintDPR to show a modal instead of window.open
hp = find("const handlePrintDPR = (rpt) => {")
if hp != -1:
    # Find end of function
    depth=0; end=hp
    for j in range(hp, min(hp+60,len(lines))):
        depth += lines[j].count('{') - lines[j].count('}')
        if depth<=0 and j>hp: end=j; break
    
    new_fn = [
        "      const handlePrintDPR = (rpt) => {\n",
        "        const proj = projects.find(p => p.id === rpt.pid);\n",
        "        setPrintData({ rpt, proj, att: [] });\n",
        "        setPrintRptId(String(rpt.id || '') + '_' + Date.now());\n",
        "      };\n",
    ]
    lines[hp:end+1] = new_fn
    changes += 1
    print("FIX 3: handlePrintDPR uses printData/printRptId state")

# ══════════════════════════════════════════════════════════════════════
# FIX 4: Add proper print modal to view return
# Find the print overlay in view return and make it a visible modal
# with a proper print button
# ══════════════════════════════════════════════════════════════════════
# Check if printRptId useEffect exists and fix it
for i,l in enumerate(lines):
    if "useEffect" in l and "printRptId" in l:
        lines[i] = (
            "  useEffect(() => {\n"
            "    if (!printRptId || !printData) return;\n"
            "    loadAttendance(printData.rpt.id).then(att => {\n"
            "      setPrintData(p => p ? {...p, att: att||[]} : p);\n"
            "    });\n"
            "  }, [printRptId]);\n"
        )
        changes += 1
        print("FIX 4: printRptId useEffect now loads att without auto-print at L"+str(i+1))
        break

# ══════════════════════════════════════════════════════════════════════
# FIX 5: Find print overlay in view return and add visible modal with print btn
# Find the hidden print overlay and make it a modal dialog when printData is set
# ══════════════════════════════════════════════════════════════════════
# Find the print overlay div in view return
for i,l in enumerate(lines):
    if "dpr-print-overlay" in l and 'div id="dpr-print-overlay"' in l:
        # Find the enclosing conditional
        for k in range(i-2, max(0,i-5),-1):
            if "{printData&&" in lines[k]:
                # Replace with modal approach
                # Find the closing of this block
                depth=0; end_k=-1
                for m in range(k, min(k+100,len(lines))):
                    depth += lines[m].count('{') - lines[m].count('}')
                    if depth<=0 and m>k: end_k=m; break
                if end_k != -1:
                    modal_lines = [
                        "            {printData&&printData.att&&(\n",
                        "              <div style={{position:'fixed',top:0,left:0,right:0,bottom:0,background:'rgba(0,0,0,0.7)',zIndex:9999,display:'flex',alignItems:'flex-start',justifyContent:'center',overflowY:'auto',padding:'20px'}}>\n",
                        "                <div style={{background:'white',borderRadius:'8px',padding:'24px',maxWidth:'1100px',width:'100%',marginTop:'10px'}}>\n",
                        "                  <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'16px'}}>\n",
                        "                    <div style={{fontWeight:'900',fontSize:'16px'}}>AL GHAITH BUILDING CONSTRUCTION LLC — SITE DAILY REPORT</div>\n",
                        "                    <div style={{display:'flex',gap:'8px'}}>\n",
                        "                      <button onClick={()=>window.print()} style={{padding:'8px 20px',background:'#1e293b',color:'white',border:'none',borderRadius:'6px',fontWeight:'700',cursor:'pointer'}}>Print</button>\n",
                        "                      <button onClick={()=>setPrintData(null)} style={{padding:'8px 16px',background:'#e2e8f0',color:'#374151',border:'none',borderRadius:'6px',cursor:'pointer'}}>Close</button>\n",
                        "                    </div>\n",
                        "                  </div>\n",
                        "                  <div id='dpr-print-overlay' style={{fontFamily:'Arial,sans-serif',fontSize:'12px',color:'#1e293b'}}>\n",
                        "                    <table style={{width:'100%',borderCollapse:'collapse',marginBottom:'10px',border:'1px solid #e2e8f0'}}><tbody>\n",
                        "                      <tr style={{background:'#f8fafc'}}>\n",
                        "                        <td style={{padding:'4px 8px'}}><b>Site:</b> {printData.proj?.number||'--'}</td>\n",
                        "                        <td style={{padding:'4px 8px'}}><b>Project:</b> {printData.proj?.name||'--'}</td>\n",
                        "                        <td style={{padding:'4px 8px'}}><b>Date:</b> {printData.rpt.date||'--'}</td>\n",
                        "                        <td style={{padding:'4px 8px'}}><b>Report No:</b> {printData.rpt.reportNum||'--'}</td>\n",
                        "                      </tr><tr>\n",
                        "                        <td style={{padding:'4px 8px'}}><b>Prepared By:</b> {printData.rpt.preparedBy||'--'}</td>\n",
                        "                        <td style={{padding:'4px 8px'}}><b>Weather:</b> {printData.rpt.weather||'--'} {printData.rpt.temp?printData.rpt.temp+'C':''}</td>\n",
                        "                        <td style={{padding:'4px 8px'}}><b>Work Hours:</b> {printData.rpt.workHours||'8'}h</td>\n",
                        "                        <td style={{padding:'4px 8px'}}><b>Status:</b> {printData.rpt.status||'--'}</td>\n",
                        "                      </tr>\n",
                        "                    </tbody></table>\n",
                        "                    {printData.att.length>0&&(\n",
                        "                      <div style={{marginBottom:'12px'}}>\n",
                        "                        <div style={{background:'#1e293b',color:'white',padding:'5px 10px',fontWeight:'700',fontSize:'11px'}}>MANPOWER ATTENDANCE | Total: {printData.att.length} | AM Present: {printData.att.filter(r=>r.am==='P').length} | PM Present: {printData.att.filter(r=>r.pm==='P').length}</div>\n",
                        "                        <table style={{width:'100%',borderCollapse:'collapse',fontSize:'10px'}}>\n",
                        "                          <thead><tr style={{background:'#f1f5f9'}}>{['S.No','ID No','Name','Designation','Team','A.M','P.M','O.T','Description'].map(h=>(<th key={h} style={{padding:'4px 6px',textAlign:'left',fontWeight:'700',color:'#475569',borderBottom:'2px solid #e2e8f0'}}>{h}</th>))}</tr></thead>\n",
                        "                          <tbody>{printData.att.map((r,i)=>(\n",
                        "                            <tr key={i} style={{borderBottom:'1px solid #e2e8f0',background:r.am==='A'&&r.pm==='A'?'#fff5f5':''}}>\n",
                        "                              <td style={{padding:'3px 6px',textAlign:'center',color:'#94a3b8'}}>{i+1}</td>\n",
                        "                              <td style={{padding:'3px 6px',fontWeight:'700',color:'#1d4ed8'}}>{r.empId||'--'}</td>\n",
                        "                              <td style={{padding:'3px 6px',fontWeight:'600'}}>{r.name||'--'}</td>\n",
                        "                              <td style={{padding:'3px 6px',color:'#64748b'}}>{r.designation||'--'}</td>\n",
                        "                              <td style={{padding:'3px 6px',textAlign:'center',color:'#7c3aed',fontWeight:'700'}}>{r.teamNo||'--'}</td>\n",
                        "                              <td style={{padding:'3px 6px',textAlign:'center',fontWeight:'900',color:r.am==='P'?'#15803d':'#b91c1c'}}>{r.am}</td>\n",
                        "                              <td style={{padding:'3px 6px',textAlign:'center',fontWeight:'900',color:r.pm==='P'?'#15803d':'#b91c1c'}}>{r.pm}</td>\n",
                        "                              <td style={{padding:'3px 6px',textAlign:'center',color:'#d97706'}}>{r.ot&&r.ot!=='0'?r.ot:'--'}</td>\n",
                        "                              <td style={{padding:'3px 6px',color:'#475569'}}>{r.description||'--'}</td>\n",
                        "                            </tr>\n",
                        "                          ))}</tbody>\n",
                        "                          <tfoot><tr style={{background:'#1e293b',color:'white'}}>\n",
                        "                            <td colSpan={5} style={{padding:'4px 8px',fontWeight:'700',fontSize:'10px'}}>TOTAL PRESENT</td>\n",
                        "                            <td style={{padding:'4px 6px',fontWeight:'900',color:'#86efac',textAlign:'center'}}>{printData.att.filter(r=>r.am==='P').length}</td>\n",
                        "                            <td style={{padding:'4px 6px',fontWeight:'900',color:'#93c5fd',textAlign:'center'}}>{printData.att.filter(r=>r.pm==='P').length}</td>\n",
                        "                            <td colSpan={2} style={{padding:'4px 8px',color:'#cbd5e1',fontSize:'10px'}}>Absent: {printData.att.filter(r=>r.am==='A'&&r.pm==='A').length}</td>\n",
                        "                          </tr></tfoot>\n",
                        "                        </table>\n",
                        "                      </div>\n",
                        "                    )}\n",
                        "                    <div style={{marginTop:'28px',display:'flex',justifyContent:'space-between',borderTop:'1px solid #e2e8f0',paddingTop:'10px'}}>\n",
                        "                      <div style={{width:'180px',textAlign:'center'}}><div style={{borderTop:'1px solid #374151',paddingTop:'3px',fontSize:'10px'}}>Signature Site Engineer</div></div>\n",
                        "                      <div style={{width:'180px',textAlign:'center'}}><div style={{borderTop:'1px solid #374151',paddingTop:'3px',fontSize:'10px'}}>Signature Site Incharge</div></div>\n",
                        "                    </div>\n",
                        "                  </div>\n",
                        "                </div>\n",
                        "              </div>\n",
                        "            )}\n",
                    ]
                    lines[k:end_k+1] = modal_lines
                    changes += 1
                    print("FIX 5: Print modal added (no popup needed) at L"+str(k+1))
                break
        break

# ══════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","setPrintData"]
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
