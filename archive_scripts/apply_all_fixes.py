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

# ══ FIX 1: Manpower count in list ════════════════════════════════════
# Find setLoading(false) inside useDailyReports loadData
udr = find("function useDailyReports()")
loading_line = -1
if udr != -1:
    for j in range(udr, min(udr+80,len(lines))):
        if "setLoading(false);" in lines[j] and j > udr+5:
            loading_line = j
            break

if loading_line != -1 and "cntMap" not in "".join(lines[udr:loading_line]):
    att_merge = [
        "        try { const {data:aC}=await supabase.from('dpr_attendance').select('dpr_id,am_count,pm_count');\n",
        "          if(aC&&aC.length){const m={};aC.forEach(a=>{if(!m[a.dpr_id])m[a.dpr_id]=0;if(a.am_count===1||a.pm_count===1)m[a.dpr_id]++;});\n",
        "          setReports(p=>p.map(r=>({...r,manpowerTotal:m[r.id]||r.manpowerTotal}))); } } catch(e){}\n",
    ]
    for k,ln in enumerate(att_merge):
        lines.insert(loading_line+k, ln)
    changes += 1
    print("FIX 1: Manpower count from attendance - inserted at L"+str(loading_line+1))
else:
    print("SKIP 1: Already applied or not found (loading_line="+str(loading_line)+")")

# ══ FIX 2: Print function ═════════════════════════════════════════════
# Find DailyReports component and add showPrint state + handlePrintDPR
dr = find("const DailyReports = ({")
if dr != -1:
    # Check if handlePrintDPR already exists
    has_print = any("handlePrintDPR" in l for l in lines[dr:dr+1500])
    has_showprint = any("showPrint" in l for l in lines[dr:dr+50])
    
    if not has_showprint:
        # Add showPrint state after first useState in DailyReports
        for j in range(dr, min(dr+20,len(lines))):
            if "useState" in lines[j] and "mode" in lines[j]:
                lines.insert(j+1, "  const [showPrint, setShowPrint] = useState(null);\n")
                changes += 1
                print("FIX 2a: showPrint state added at L"+str(j+2))
                break

    if not has_print:
        # Find the last handleXxx function before return
        # Insert handlePrintDPR before the return statement
        ret_line = -1
        depth = 0
        for j in range(dr, min(dr+2000,len(lines))):
            depth += lines[j].count('{') - lines[j].count('}')
            if depth==1 and lines[j].strip().startswith('return (') and j > dr+100:
                ret_line = j
                break
        
        if ret_line != -1:
            print_fn = [
                "\n",
                "  const handlePrintDPR = async (rpt) => {\n",
                "    showToast('Loading report...');\n",
                "    const proj = projects.find(p=>p.id===rpt.pid);\n",
                "    const att = await loadAttendance(rpt.id);\n",
                "    setShowPrint({rpt,proj,att});\n",
                "  };\n",
                "\n",
            ]
            for k,ln in enumerate(print_fn):
                lines.insert(ret_line+k, ln)
            changes += 1
            print("FIX 2b: handlePrintDPR added at L"+str(ret_line+1))

# ══ FIX 3: Add Print button to View mode ══════════════════════════════
# Find "Edit Report" button in view mode and add Print before it
if dr != -1:
    for j in range(dr, min(dr+2500,len(lines))):
        if '"Edit Report"' in lines[j] and 'openEdit(sel)' in lines[j]:
            if j > dr+200:  # make sure we're in view mode not elsewhere
                ctx = "".join(lines[max(0,j-100):j])
                if "mode===\"view\"" in ctx or "sel.reportNum" in ctx:
                    if not any("handlePrintDPR" in lines[k] for k in range(max(0,j-5),j+2)):
                        lines.insert(j, '              <button onClick={()=>handlePrintDPR(sel)} className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-xl text-sm font-semibold transition-colors">Export / Print</button>\n')
                        changes += 1
                        print("FIX 3: Print button added at L"+str(j+1))
                    break

# ══ FIX 4: Add print overlay to DailyReports return ══════════════════
# Find the list return (filtered.map) and insert overlay before it
marker = "const filtered = reports.filter"
if dr != -1:
    for j in range(dr, min(dr+500,len(lines))):
        if marker in lines[j]:
            # Check showPrint overlay not already there
            if not any("showPrint&&" in lines[k] for k in range(max(0,j-5),j+3)):
                overlay = (
                    "      {showPrint&&(\n"
                    "        <div style={{position:'fixed',top:0,left:0,right:0,bottom:0,zIndex:9999,background:'white',overflowY:'auto',padding:'20px'}}>\n"
                    "          <div style={{maxWidth:'1050px',margin:'0 auto'}}>\n"
                    "            <div style={{textAlign:'center',borderBottom:'3px double #1e293b',paddingBottom:'8px',marginBottom:'12px'}}>\n"
                    "              <div style={{fontSize:'17px',fontWeight:'900'}}>AL GHAITH BUILDING CONSTRUCTION (LLC)</div>\n"
                    "              <div style={{fontSize:'12px',fontWeight:'700',color:'#d97706'}}>SITE DAILY REPORT</div>\n"
                    "            </div>\n"
                    "            <table style={{width:'100%',borderCollapse:'collapse',marginBottom:'10px',fontSize:'12px'}}><tbody>\n"
                    "              <tr style={{background:'#f8fafc'}}>\n"
                    "                <td style={{padding:'4px 8px',border:'1px solid #e2e8f0'}}><b>Site No:</b> {showPrint.proj?.number||'--'}</td>\n"
                    "                <td style={{padding:'4px 8px',border:'1px solid #e2e8f0'}}><b>Project:</b> {showPrint.proj?.name||'--'}</td>\n"
                    "                <td style={{padding:'4px 8px',border:'1px solid #e2e8f0'}}><b>Date:</b> {showPrint.rpt.date||'--'}</td>\n"
                    "                <td style={{padding:'4px 8px',border:'1px solid #e2e8f0'}}><b>Report No:</b> {showPrint.rpt.reportNum||'--'}</td>\n"
                    "              </tr><tr>\n"
                    "                <td style={{padding:'4px 8px',border:'1px solid #e2e8f0'}}><b>Prepared By:</b> {showPrint.rpt.preparedBy||'--'}</td>\n"
                    "                <td style={{padding:'4px 8px',border:'1px solid #e2e8f0'}}><b>Weather:</b> {showPrint.rpt.weather||'--'} {showPrint.rpt.temp?showPrint.rpt.temp+'C':''}</td>\n"
                    "                <td style={{padding:'4px 8px',border:'1px solid #e2e8f0'}}><b>Work Hours:</b> {showPrint.rpt.workHours||'8'}h</td>\n"
                    "                <td style={{padding:'4px 8px',border:'1px solid #e2e8f0'}}><b>Status:</b> {showPrint.rpt.status||'--'}</td>\n"
                    "              </tr>\n"
                    "            </tbody></table>\n"
                    "            <div style={{background:'#1e293b',color:'white',padding:'5px 10px',fontWeight:'700',fontSize:'11px'}}>\n"
                    "              MANPOWER ATTENDANCE | Total: {showPrint.att.length} | AM Present: {showPrint.att.filter(r=>r.am==='P').length} | PM Present: {showPrint.att.filter(r=>r.pm==='P').length}\n"
                    "            </div>\n"
                    "            <table style={{width:'100%',borderCollapse:'collapse',fontSize:'11px',marginBottom:'12px'}}>\n"
                    "              <thead><tr style={{background:'#f1f5f9'}}>{['S.No','ID No','Name','Designation','Team','A.M','P.M','O.T','Description'].map(h=>(<th key={h} style={{padding:'4px 6px',textAlign:'left',fontWeight:'700',color:'#475569',border:'1px solid #e2e8f0'}}>{h}</th>))}</tr></thead>\n"
                    "              <tbody>{showPrint.att.map((r,i)=>(\n"
                    "                <tr key={i} style={{background:i%2===0?'white':'#f8fafc'}}>\n"
                    "                  <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',textAlign:'center'}}>{i+1}</td>\n"
                    "                  <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',fontWeight:'700',color:'#1d4ed8'}}>{r.empId||'--'}</td>\n"
                    "                  <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',fontWeight:'600'}}>{r.name||'--'}</td>\n"
                    "                  <td style={{padding:'3px 6px',border:'1px solid #e2e8f0'}}>{r.designation||'--'}</td>\n"
                    "                  <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',textAlign:'center',color:'#7c3aed',fontWeight:'700'}}>{r.teamNo||'--'}</td>\n"
                    "                  <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',textAlign:'center',fontWeight:'900',color:r.am==='P'?'#15803d':'#b91c1c'}}>{r.am}</td>\n"
                    "                  <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',textAlign:'center',fontWeight:'900',color:r.pm==='P'?'#15803d':'#b91c1c'}}>{r.pm}</td>\n"
                    "                  <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',textAlign:'center'}}>{r.ot&&r.ot!=='0'?r.ot:'--'}</td>\n"
                    "                  <td style={{padding:'3px 6px',border:'1px solid #e2e8f0'}}>{r.description||'--'}</td>\n"
                    "                </tr>\n"
                    "              ))}</tbody>\n"
                    "              <tfoot><tr style={{background:'#1e293b',color:'white'}}>\n"
                    "                <td colSpan={5} style={{padding:'4px 8px',fontWeight:'700'}}>TOTAL PRESENT</td>\n"
                    "                <td style={{padding:'4px 6px',textAlign:'center',fontWeight:'900',color:'#86efac'}}>{showPrint.att.filter(r=>r.am==='P').length}</td>\n"
                    "                <td style={{padding:'4px 6px',textAlign:'center',fontWeight:'900',color:'#93c5fd'}}>{showPrint.att.filter(r=>r.pm==='P').length}</td>\n"
                    "                <td colSpan={2} style={{padding:'4px 8px',color:'#cbd5e1',fontSize:'10px'}}>Absent: {showPrint.att.filter(r=>r.am==='A'&&r.pm==='A').length}</td>\n"
                    "              </tr></tfoot>\n"
                    "            </table>\n"
                    "            <div style={{marginTop:'30px',display:'flex',justifyContent:'space-between',borderTop:'1px solid #e2e8f0',paddingTop:'10px'}}>\n"
                    "              <div style={{width:'180px',textAlign:'center'}}><div style={{borderTop:'1px solid #374151',marginTop:'24px',paddingTop:'3px',fontSize:'10px'}}>Signature Site Engineer</div></div>\n"
                    "              <div style={{width:'180px',textAlign:'center'}}><div style={{borderTop:'1px solid #374151',marginTop:'24px',paddingTop:'3px',fontSize:'10px'}}>Signature Site Incharge</div></div>\n"
                    "            </div>\n"
                    "            <div style={{textAlign:'center',marginTop:'14px',display:'flex',gap:'8px',justifyContent:'center'}}>\n"
                    "              <button onClick={()=>window.print()} style={{padding:'9px 28px',background:'#1e293b',color:'white',border:'none',borderRadius:'6px',fontSize:'13px',fontWeight:'700',cursor:'pointer'}}>Print / Save as PDF</button>\n"
                    "              <button onClick={()=>setShowPrint(null)} style={{padding:'9px 18px',background:'#e2e8f0',color:'#374151',border:'none',borderRadius:'6px',fontSize:'13px',cursor:'pointer'}}>Close</button>\n"
                    "            </div>\n"
                    "          </div>\n"
                    "        </div>\n"
                    "      )}\n"
                )
                lines.insert(j, overlay)
                changes += 1
                print("FIX 4: Print overlay inserted at L"+str(j+1))
            break

# ══ WRITE ════════════════════════════════════════════════════════════
out = "".join(lines)
checks = ["const DailyReports","DprAttendancePanel","showPrint","handlePrintDPR"]
failed = [c for c in checks if c not in out]
if failed:
    print("SAFETY FAIL:"+str(failed))
    shutil.copy2(bk,APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("\nSaved OK. Lines:"+str(len(lines)))

print("TOTAL CHANGES:"+str(changes))
print("\nRUN:")
print("  set CI=false && npm run build")
print("  git add src/App.js")
print("  git commit -m 'feat: manpower count + print overlay'")
print("  git push")
input("\nPress Enter...")
