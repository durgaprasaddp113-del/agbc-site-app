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

# ════════════════════════════════════════════════════════════════════
# BUG 1 ROOT CAUSE: DprAttendancePanel unmounts/remounts when user
# switches tabs because of: {activeSection==="manpower"&&<DprAttendance...>}
# Each remount triggers useEffect([dprId]) → reloads OLD data from DB
# → overwrites user's changes (deletions)
#
# FIX: Always render the panel but show/hide with CSS display property
# ════════════════════════════════════════════════════════════════════
print("── Fixing panel conditional render ──")
if dr != -1:
    for j in range(dr, min(dr+900, len(lines))):
        l = lines[j]
        if '{activeSection==="manpower"&&<DprAttendancePanel' in l:
            # Replace conditional render with always-rendered but hidden
            lines[j] = lines[j].replace(
                '{activeSection==="manpower"&&<DprAttendancePanel',
                '<div style={{display:activeSection==="manpower"?"block":"none"}}><DprAttendancePanel'
            )
            # Find the closing />} and replace with /></div>
            for k in range(j, min(j+15, len(lines))):
                if '/>}' in lines[k]:
                    lines[k] = lines[k].replace('/>}', '/></div>')
                    changes += 1
                    print("FIX 1: Panel always rendered (CSS show/hide) at L"+str(j+1)+"-"+str(k+1))
                    break
                elif lines[k].strip() == '/>}':
                    lines[k] = lines[k].replace('/>}', '/></div>')
                    changes += 1
                    print("FIX 1: Panel always rendered at L"+str(j+1)+"-"+str(k+1))
                    break
            break

# ════════════════════════════════════════════════════════════════════
# BUG 2: Print - replace with in-page modal (no popup needed)
# Find handlePrintDPR and replace with state setter only
# Then add modal to view return that uses window.print() on click
# ════════════════════════════════════════════════════════════════════
print("\n── Fixing print ──")
hp = find("const handlePrintDPR =")
if hp != -1:
    depth=0; end=hp
    for j in range(hp, min(hp+60,len(lines))):
        depth += lines[j].count('{') - lines[j].count('}')
        if depth<=0 and j>hp: end=j; break

    new_fn = [
        "      const handlePrintDPR = (rpt) => {\n",
        "        const proj = projects.find(p => p.id === rpt.pid);\n",
        "        setPrintData({ rpt, proj, att: [] });\n",
        "        setPrintRptId(String(rpt.id||'')+'_'+Date.now());\n",
        "      };\n",
    ]
    lines[hp:end+1] = new_fn
    changes += 1
    print("FIX 2a: handlePrintDPR simplified at L"+str(hp+1))

# Fix useEffect to load attendance when printRptId changes
for i,l in enumerate(lines):
    if "useEffect" in l and "printRptId" in l:
        lines[i] = (
            "  useEffect(() => {\n"
            "    if (!printRptId||!printData) return;\n"
            "    loadAttendance(printData.rpt.id).then(att=>{\n"
            "      setPrintData(p=>p?{...p,att:att||[]}:p);\n"
            "    });\n"
            "  }, [printRptId]);\n"
        )
        changes += 1
        print("FIX 2b: printRptId useEffect fixed at L"+str(i+1))
        break

# Remove old printData&&printData.att modal blocks (may be duplicated/broken)
# Find and clean any existing print modal
i = 0
removed = 0
new_lines = []
skip_until = -1
for i, l in enumerate(lines):
    if skip_until > 0 and i <= skip_until:
        continue
    if "printData&&printData.att&&" in l or "{printData&&printData.att&&" in l:
        # Find the end of this block
        depth=0; end_i=i
        for j in range(i, min(i+100,len(lines))):
            depth += lines[j].count('{') - lines[j].count('}')
            if depth<=0 and j>i: end_i=j; break
        skip_until = end_i
        removed += 1
        print("FIX 2c: Removed old print modal block at L"+str(i+1)+"-"+str(end_i+1))
        continue
    new_lines.append(l)

if removed > 0:
    lines = new_lines
    changes += removed

# Add clean print modal to view return
# Find the view return block - look for the div.flex.flex-wrap.gap-3 with Print DPR button
# and add the modal BEFORE the closing </div> of view return
view_buttons = -1
for j in range(0, len(lines)):
    if "handlePrintDPR(sel)" in lines[j] and "button" in lines[j]:
        view_buttons = j
        break

if view_buttons != -1:
    # Find the closing of the view return
    # Look for the </div> that closes the view return (after buttons)
    for j in range(view_buttons, min(view_buttons+20, len(lines))):
        if lines[j].strip() in ["</div>", "    </div>", "      </div>"] and j > view_buttons+2:
            # Insert print modal before this closing
            modal = (
                "            {printData&&(\n"
                "              <div style={{position:'fixed',top:0,left:0,right:0,bottom:0,background:'rgba(0,0,0,0.75)',zIndex:9999,overflowY:'auto',padding:'16px'}}>\n"
                "                <div style={{background:'white',borderRadius:'8px',maxWidth:'1100px',margin:'0 auto',padding:'20px'}}>\n"
                "                  <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'12px'}}>\n"
                "                    <b style={{fontSize:'15px'}}>AL GHAITH BUILDING CONSTRUCTION LLC — SITE DAILY REPORT</b>\n"
                "                    <div style={{display:'flex',gap:'8px'}}>\n"
                "                      <button onClick={()=>window.print()} style={{padding:'7px 18px',background:'#1e293b',color:'white',border:'none',borderRadius:'6px',fontWeight:'700',cursor:'pointer',fontSize:'13px'}}>Print</button>\n"
                "                      <button onClick={()=>{setPrintData(null);setPrintRptId(null);}} style={{padding:'7px 14px',background:'#e2e8f0',color:'#374151',border:'none',borderRadius:'6px',cursor:'pointer',fontSize:'13px'}}>Close</button>\n"
                "                    </div>\n"
                "                  </div>\n"
                "                  <table style={{width:'100%',borderCollapse:'collapse',marginBottom:'10px',border:'1px solid #e2e8f0'}}><tbody>\n"
                "                    <tr style={{background:'#f8fafc'}}>\n"
                "                      <td style={{padding:'4px 8px'}}><b>Site No:</b> {printData.proj?.number||'--'}</td>\n"
                "                      <td style={{padding:'4px 8px'}}><b>Project:</b> {printData.proj?.name||'--'}</td>\n"
                "                      <td style={{padding:'4px 8px'}}><b>Date:</b> {printData.rpt.date||'--'}</td>\n"
                "                      <td style={{padding:'4px 8px'}}><b>Report No:</b> {printData.rpt.reportNum||'--'}</td>\n"
                "                    </tr><tr>\n"
                "                      <td style={{padding:'4px 8px'}}><b>Prepared By:</b> {printData.rpt.preparedBy||'--'}</td>\n"
                "                      <td style={{padding:'4px 8px'}}><b>Weather:</b> {printData.rpt.weather||'--'} {printData.rpt.temp?printData.rpt.temp+'°C':''}</td>\n"
                "                      <td style={{padding:'4px 8px'}}><b>Work Hours:</b> {printData.rpt.workHours||'8'}h</td>\n"
                "                      <td style={{padding:'4px 8px'}}><b>Status:</b> {printData.rpt.status||'--'}</td>\n"
                "                    </tr>\n"
                "                  </tbody></table>\n"
                "                  {(printData.att||[]).length>0&&(\n"
                "                    <div>\n"
                "                      <div style={{background:'#1e293b',color:'white',padding:'5px 10px',fontWeight:'700',fontSize:'11px',marginBottom:'0'}}>\n"
                "                        MANPOWER ATTENDANCE | Total: {printData.att.length} | AM Present: {printData.att.filter(r=>r.am==='P').length} | PM Present: {printData.att.filter(r=>r.pm==='P').length}\n"
                "                      </div>\n"
                "                      <table style={{width:'100%',borderCollapse:'collapse',fontSize:'11px'}}>\n"
                "                        <thead><tr style={{background:'#f1f5f9'}}>{['S.No','ID No','Name','Designation','Team','A.M','P.M','O.T','Description of Work'].map(h=>(<th key={h} style={{padding:'4px 6px',textAlign:'left',fontWeight:'700',color:'#475569',borderBottom:'2px solid #e2e8f0',whiteSpace:'nowrap'}}>{h}</th>))}</tr></thead>\n"
                "                        <tbody>{printData.att.map((r,i)=>(\n"
                "                          <tr key={i} style={{borderBottom:'1px solid #e2e8f0',background:r.am==='A'&&r.pm==='A'?'#fff5f5':''}}>\n"
                "                            <td style={{padding:'3px 6px',textAlign:'center',color:'#94a3b8'}}>{i+1}</td>\n"
                "                            <td style={{padding:'3px 6px',fontWeight:'700',color:'#1d4ed8'}}>{r.empId||'--'}</td>\n"
                "                            <td style={{padding:'3px 6px',fontWeight:'600',whiteSpace:'nowrap'}}>{r.name||'--'}</td>\n"
                "                            <td style={{padding:'3px 6px',color:'#64748b'}}>{r.designation||'--'}</td>\n"
                "                            <td style={{padding:'3px 6px',textAlign:'center',color:'#7c3aed',fontWeight:'700'}}>{r.teamNo||'--'}</td>\n"
                "                            <td style={{padding:'3px 6px',textAlign:'center',fontWeight:'900',color:r.am==='P'?'#15803d':'#b91c1c'}}>{r.am}</td>\n"
                "                            <td style={{padding:'3px 6px',textAlign:'center',fontWeight:'900',color:r.pm==='P'?'#15803d':'#b91c1c'}}>{r.pm}</td>\n"
                "                            <td style={{padding:'3px 6px',textAlign:'center',color:'#d97706'}}>{r.ot&&r.ot!=='0'?r.ot:'--'}</td>\n"
                "                            <td style={{padding:'3px 6px',color:'#475569'}}>{r.description||'--'}</td>\n"
                "                          </tr>\n"
                "                        ))}</tbody>\n"
                "                        <tfoot><tr style={{background:'#1e293b',color:'white'}}>\n"
                "                          <td colSpan={5} style={{padding:'4px 8px',fontWeight:'700',fontSize:'10px'}}>TOTAL PRESENT</td>\n"
                "                          <td style={{padding:'4px 6px',fontWeight:'900',color:'#86efac',textAlign:'center'}}>{printData.att.filter(r=>r.am==='P').length}</td>\n"
                "                          <td style={{padding:'4px 6px',fontWeight:'900',color:'#93c5fd',textAlign:'center'}}>{printData.att.filter(r=>r.pm==='P').length}</td>\n"
                "                          <td colSpan={2} style={{padding:'4px 8px',color:'#cbd5e1',fontSize:'10px'}}>Absent: {printData.att.filter(r=>r.am==='A'&&r.pm==='A').length}</td>\n"
                "                        </tr></tfoot>\n"
                "                      </table>\n"
                "                    </div>\n"
                "                  )}\n"
                "                  <div style={{marginTop:'24px',display:'flex',justifyContent:'space-between',borderTop:'1px solid #e2e8f0',paddingTop:'10px'}}>\n"
                "                    <div style={{width:'180px',textAlign:'center'}}><div style={{borderTop:'1px solid #374151',paddingTop:'3px',fontSize:'10px'}}>Signature Site Engineer</div></div>\n"
                "                    <div style={{width:'180px',textAlign:'center'}}><div style={{borderTop:'1px solid #374151',paddingTop:'3px',fontSize:'10px'}}>Signature Site Incharge</div></div>\n"
                "                  </div>\n"
                "                </div>\n"
                "              </div>\n"
                "            )}\n"
            )
            for k, ml in enumerate(modal.split('\n')):
                if ml: lines.insert(j+k, ml+'\n')
            changes += 1
            print("FIX 2d: Print modal inserted at L"+str(j+1))
            break

# ════════════════════════════════════════════════════════════════════
# BUG 3: Tab badge shows (0) — fix Manpower tab count
# ════════════════════════════════════════════════════════════════════
print("\n── Fixing tab badge ──")
if dr != -1:
    for j in range(dr, min(dr+900, len(lines))):
        l = lines[j]
        if '"manpower"' in l and 'label:' in l and 'Manpower' in l:
            old = lines[j]
            lines[j] = re.sub(
                r'\$\{[^`}]*form\.manpower[^`}]*\}',
                '${(attRowsRef.current||[]).length}',
                lines[j]
            )
            if lines[j] != old:
                changes += 1
                print("FIX 3: Manpower tab badge at L"+str(j+1))
            else:
                # Try different pattern
                lines[j] = re.sub(
                    r'Manpower \(\$\{[^}]+\}\)',
                    'Manpower (${(attRowsRef.current||[]).length})',
                    lines[j]
                )
                if lines[j] != old:
                    changes += 1
                    print("FIX 3b: Manpower tab badge (alt) at L"+str(j+1))
            break

# ════════════════════════════════════════════════════════════════════
# WRITE
# ════════════════════════════════════════════════════════════════════
out = "".join(lines)
checks = ["const DailyReports","handlePrintDPR","DprAttendancePanel","setPrintData","attRowsRef"]
failed = [c for c in checks if c not in out]
if failed:
    print("\nSAFETY FAIL: "+str(failed))
    shutil.copy2(bk, APP)
    print("Restored backup")
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(out)
    print("\nSaved OK. Lines: "+str(len(lines)))

print("TOTAL CHANGES: "+str(changes))
print("\nRUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
input("\nPress Enter...")
