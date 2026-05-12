import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

def find_line(t):
    for i,l in enumerate(content.split('\n')):
        if t in l: return i
    return -1

changes = 0

# ── STEP 1: Add showPrint state after printData state ────────────────
old_state = '  const [printData, setPrintData] = useState(null);'
new_state = ('  const [printData, setPrintData] = useState(null);\n'
             '  const [showPrint, setShowPrint] = useState(null);')
if old_state in content and 'showPrint' not in content:
    content = content.replace(old_state, new_state, 1)
    changes += 1
    print("STEP 1: showPrint state added")

# ── STEP 2: Replace handlePrintDPR with simple async version ─────────
old_fn_marker = 'const handlePrintDPR = async (rpt) => {'
if old_fn_marker in content:
    # Find start and end of function
    start = content.find('      ' + old_fn_marker)
    if start == -1:
        start = content.find('        ' + old_fn_marker)
    if start != -1:
        # Find closing }; by counting braces
        depth = 0
        end = start
        for i, ch in enumerate(content[start:]):
            if ch == '{': depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = start + i + 1
                    # Skip optional semicolon
                    if end < len(content) and content[end] == ';':
                        end += 1
                    break

        new_fn = """      const handlePrintDPR = async (rpt) => {
        showToast('Loading report...');
        const proj = projects.find(p => p.id === rpt.pid);
        const att = await loadAttendance(rpt.id);
        setShowPrint({ rpt, proj, att });
      };"""

        content = content[:start] + new_fn + content[end:]
        changes += 1
        print("STEP 2: handlePrintDPR simplified")

# ── STEP 3: Add print overlay component before closing of DailyReports
# Find the list return statement - insert overlay before it
# The overlay uses @media print CSS to show only itself when printing

OVERLAY = """
      {/* ── Print Overlay ── */}
      {showPrint&&(
        <div style={{position:'fixed',top:0,left:0,right:0,bottom:0,zIndex:9999,background:'white',overflowY:'auto',padding:'24px'}} id="print-area">
          <style dangerouslySetInnerHTML={{__html:'@media print{body>*{display:none}#print-area{display:block!important;position:static!important}}'}}/>
          <div style={{maxWidth:'1100px',margin:'0 auto'}}>
            <div style={{textAlign:'center',borderBottom:'3px double #1e293b',paddingBottom:'8px',marginBottom:'12px'}}>
              <div style={{fontSize:'18px',fontWeight:'900'}}>AL GHAITH BUILDING CONSTRUCTION (LLC)</div>
              <div style={{fontSize:'13px',fontWeight:'700',color:'#d97706'}}>SITE DAILY REPORT</div>
            </div>
            <table style={{width:'100%',borderCollapse:'collapse',marginBottom:'12px',fontSize:'12px'}}>
              <tbody>
                <tr style={{background:'#f8fafc'}}>
                  <td style={{padding:'5px 8px',border:'1px solid #e2e8f0'}}><b>Site No:</b> {showPrint.proj?.number||'--'}</td>
                  <td style={{padding:'5px 8px',border:'1px solid #e2e8f0'}}><b>Project:</b> {showPrint.proj?.name||'--'}</td>
                  <td style={{padding:'5px 8px',border:'1px solid #e2e8f0'}}><b>Date:</b> {showPrint.rpt.date||'--'}</td>
                  <td style={{padding:'5px 8px',border:'1px solid #e2e8f0'}}><b>Report No:</b> {showPrint.rpt.reportNum||'--'}</td>
                </tr>
                <tr>
                  <td style={{padding:'5px 8px',border:'1px solid #e2e8f0'}}><b>Prepared By:</b> {showPrint.rpt.preparedBy||'--'}</td>
                  <td style={{padding:'5px 8px',border:'1px solid #e2e8f0'}}><b>Weather:</b> {showPrint.rpt.weather||'--'} {showPrint.rpt.temp?showPrint.rpt.temp+'°C':''}</td>
                  <td style={{padding:'5px 8px',border:'1px solid #e2e8f0'}}><b>Work Hours:</b> {showPrint.rpt.workHours||'8'}h</td>
                  <td style={{padding:'5px 8px',border:'1px solid #e2e8f0'}}><b>Status:</b> {showPrint.rpt.status||'--'}</td>
                </tr>
              </tbody>
            </table>
            <div style={{fontWeight:'700',fontSize:'12px',background:'#1e293b',color:'white',padding:'6px 10px',marginBottom:'0'}}>
              MANPOWER ATTENDANCE &nbsp;|&nbsp; Total: {showPrint.att.length} &nbsp;|&nbsp; AM Present: {showPrint.att.filter(r=>r.am==='P').length} &nbsp;|&nbsp; PM Present: {showPrint.att.filter(r=>r.pm==='P').length}
            </div>
            <table style={{width:'100%',borderCollapse:'collapse',fontSize:'11px',marginBottom:'12px'}}>
              <thead>
                <tr style={{background:'#f1f5f9'}}>{['S.No','ID No','Name','Designation','Team','A.M','P.M','O.T','Description of Work'].map(h=><th key={h} style={{padding:'4px 6px',textAlign:'left',fontWeight:'700',color:'#475569',border:'1px solid #e2e8f0'}}>{h}</th>)}</tr>
              </thead>
              <tbody>
                {showPrint.att.map((r,i)=>(
                  <tr key={i} style={{background:i%2===0?'white':'#f8fafc'}}>
                    <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',textAlign:'center'}}>{i+1}</td>
                    <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',fontWeight:'700',color:'#1d4ed8'}}>{r.empId||'--'}</td>
                    <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',fontWeight:'600'}}>{r.name||'--'}</td>
                    <td style={{padding:'3px 6px',border:'1px solid #e2e8f0'}}>{r.designation||'--'}</td>
                    <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',textAlign:'center',fontWeight:'700',color:'#7c3aed'}}>{r.teamNo||'--'}</td>
                    <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',textAlign:'center',fontWeight:'900',color:r.am==='P'?'#15803d':'#b91c1c'}}>{r.am}</td>
                    <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',textAlign:'center',fontWeight:'900',color:r.pm==='P'?'#15803d':'#b91c1c'}}>{r.pm}</td>
                    <td style={{padding:'3px 6px',border:'1px solid #e2e8f0',textAlign:'center'}}>{r.ot&&r.ot!=='0'?r.ot:'--'}</td>
                    <td style={{padding:'3px 6px',border:'1px solid #e2e8f0'}}>{r.description||'--'}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr style={{background:'#1e293b',color:'white'}}>
                  <td colSpan={5} style={{padding:'4px 8px',fontWeight:'700'}}>TOTAL PRESENT</td>
                  <td style={{padding:'4px 6px',textAlign:'center',fontWeight:'900',color:'#86efac'}}>{showPrint.att.filter(r=>r.am==='P').length}</td>
                  <td style={{padding:'4px 6px',textAlign:'center',fontWeight:'900',color:'#93c5fd'}}>{showPrint.att.filter(r=>r.pm==='P').length}</td>
                  <td colSpan={2} style={{padding:'4px 8px',fontSize:'11px',color:'#cbd5e1'}}>Absent: {showPrint.att.filter(r=>r.am==='A'&&r.pm==='A').length}</td>
                </tr>
              </tfoot>
            </table>
            <div style={{marginTop:'32px',display:'flex',justifyContent:'space-between',borderTop:'1px solid #e2e8f0',paddingTop:'12px'}}>
              <div style={{width:'200px',textAlign:'center'}}><div style={{borderTop:'1px solid #374151',marginTop:'28px',paddingTop:'4px',fontSize:'11px'}}>Signature Site Engineer</div></div>
              <div style={{width:'200px',textAlign:'center'}}><div style={{borderTop:'1px solid #374151',marginTop:'28px',paddingTop:'4px',fontSize:'11px'}}>Signature Site Incharge</div></div>
            </div>
            <div style={{textAlign:'center',marginTop:'16px',display:'flex',gap:'8px',justifyContent:'center'}} className="noprint">
              <button onClick={()=>window.print()} style={{padding:'10px 28px',background:'#1e293b',color:'white',border:'none',borderRadius:'6px',fontSize:'14px',fontWeight:'700',cursor:'pointer'}}>Print / Save PDF</button>
              <button onClick={()=>setShowPrint(null)} style={{padding:'10px 20px',background:'#e2e8f0',color:'#374151',border:'none',borderRadius:'6px',fontSize:'14px',cursor:'pointer'}}>Close</button>
            </div>
          </div>
        </div>
      )}
"""

# Find the list return in DailyReports - insert overlay before it
# Look for the filtered.map table render
marker = '      const filtered = reports.filter'
if marker in content:
    idx = content.find(marker)
    content = content[:idx] + OVERLAY + '\n' + content[idx:]
    changes += 1
    print("STEP 3: Print overlay added")

# ── STEP 4: Update button label ───────────────────────────────────────
for old,new in [
    ('Export / Print','Export / Print'),
    ('Export Excel','Export / Print'),
    ('Print DPR','Export / Print'),
]:
    if 'handlePrintDPR(sel)' in content:
        # Just ensure button exists - label already good
        break

# Write
with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

checks = ["const DailyReports","showPrint","setShowPrint","handlePrintDPR","DprAttendancePanel"]
failed = [c for c in checks if c not in content]
if failed:
    print("SAFETY FAIL:"+str(failed))
    shutil.copy2(bk,APP)
else:
    print("Saved OK")

print("CHANGES:"+str(changes))
print("RUN: set CI=false && npm run build")
print("     git add src/App.js && git commit -m 'fix: print overlay' && git push")
input("Press Enter...")
