import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

changes = 0

# ══════════════════════════════════════════════════════════════════════
# FIX 1: saveAttendance — save ALL rows (not just mpId rows)
#         Also save emp_name, designation, employee_id for manual rows
# ══════════════════════════════════════════════════════════════════════
OLD_SAVE = """    const saveAttendance = async (dprId, rows) => {
      if (!dprId) return { ok: false, error: "No DPR ID" };
      await supabase.from("dpr_attendance").delete().eq("dpr_id", dprId);
      const valid = rows.filter(r => r.mpId);
      if (!valid.length) return { ok: true };
      const { error } = await supabase.from("dpr_attendance").insert(valid.map(r => ({
        dpr_id: dprId, subcontractor_id: r.subId || null, manpower_id: r.mpId || null,
        am_count: r.am==="P"?1:0, pm_count: r.pm==="P"?1:0,
        ot_hours: parseFloat(r.ot) || 0, description_of_work: r.description || "",
        team_no: r.teamNo || "", daily_remarks: r.remarks || "",
      })));
      if (error) return { ok: false, error: error.message };
      return { ok: true };
    };"""

NEW_SAVE = """    const saveAttendance = async (dprId, rows) => {
      if (!dprId) return { ok: false, error: "No DPR ID" };
      await supabase.from("dpr_attendance").delete().eq("dpr_id", dprId);
      const valid = rows.filter(r => r.name && r.name.trim());
      if (!valid.length) return { ok: true };
      const { error } = await supabase.from("dpr_attendance").insert(valid.map(r => ({
        dpr_id: dprId, subcontractor_id: r.subId || null, manpower_id: r.mpId || null,
        employee_id: r.empId || "", emp_name: r.name || "", designation: r.designation || "",
        am_count: r.am==="P"?1:0, pm_count: r.pm==="P"?1:0,
        ot_hours: parseFloat(r.ot) || 0, description_of_work: r.description || "",
        team_no: r.teamNo || "", daily_remarks: r.remarks || "",
      })));
      if (error) return { ok: false, error: error.message };
      return { ok: true };
    };"""

if OLD_SAVE in content:
    content = content.replace(OLD_SAVE, NEW_SAVE)
    changes += 1
    print("FIX 1: saveAttendance now saves ALL rows + emp_name/designation")
else:
    print("WARN 1: saveAttendance pattern not found")

# ══════════════════════════════════════════════════════════════════════
# FIX 2: loadAttendance — also return emp_name, designation, employee_id
# ══════════════════════════════════════════════════════════════════════
OLD_LOAD = """      return (data || []).map(a => ({
        id: a.id, dprId: a.dpr_id, subId: a.subcontractor_id || "",
        mpId: a.manpower_id || "", am: a.am_count===1?"P":"A",
        pm: a.pm_count===1?"P":"A", ot: String(a.ot_hours || 0),
        description: a.description_of_work || "", teamNo: a.team_no || "", remarks: a.daily_remarks || "",
      }));"""

NEW_LOAD = """      return (data || []).map(a => ({
        id: a.id, dprId: a.dpr_id, subId: a.subcontractor_id || "",
        mpId: a.manpower_id || "", empId: a.employee_id || "",
        name: a.emp_name || "", designation: a.designation || "",
        am: a.am_count===1?"P":"A", pm: a.pm_count===1?"P":"A",
        ot: String(a.ot_hours || 0), description: a.description_of_work || "",
        teamNo: a.team_no || "", remarks: a.daily_remarks || "",
      }));"""

if OLD_LOAD in content:
    content = content.replace(OLD_LOAD, NEW_LOAD)
    changes += 1
    print("FIX 2: loadAttendance now returns empId/name/designation")
else:
    print("WARN 2: loadAttendance pattern not found")

# ══════════════════════════════════════════════════════════════════════
# FIX 3: Add Team column to DprAttendancePanel + auto-fill description
# Replace headers and row cells
# ══════════════════════════════════════════════════════════════════════
OLD_HEADS = '        {["S.No","ID No","Name","Designation","A.M","P.M","O.T","Description of Work",""].map(h=>('
NEW_HEADS = '        {["S.No","ID No","Name","Designation","Team","A.M","P.M","O.T","Description of Work",""].map(h=>('

if OLD_HEADS in content:
    content = content.replace(OLD_HEADS, NEW_HEADS)
    changes += 1
    print("FIX 3a: Team column added to headers")
else:
    print("WARN 3a: headers not found")

# Add Team cell before A.M cell in the row
OLD_AM_CELL = """                    <td className="px-2 py-2 w-12 text-center">
                      <PABtn val={r.am||"P"} onClick={()=>toggle(rid,"am")}/>
                    </td>"""

NEW_TEAM_AM_CELL = """                    <td className="px-2 py-2 w-20">
                      <Inp value={r.teamNo||""} onChange={e=>{
                        const t=e.target.value;
                        setCell(rid,"teamNo",t);
                      }} onBlur={e=>{
                        const t=e.target.value.trim();
                        if(!t) return;
                        // Auto-fill description for same team
                        setRows(prev=>{
                          const teamDesc = prev.find(x=>(x.rowId!==rid&&x.id!==rid)&&x.teamNo===t&&x.description)?
                            prev.find(x=>(x.rowId!==rid&&x.id!==rid)&&x.teamNo===t&&x.description).description : null;
                          if(!teamDesc) return prev;
                          return prev.map(x=>x.teamNo===t&&!(x.description)?{...x,description:teamDesc}:x);
                        });
                      }} placeholder="T-1" className="w-16 text-center font-semibold text-purple-700"/>
                    </td>
                    <td className="px-2 py-2 w-12 text-center">
                      <PABtn val={r.am||"P"} onClick={()=>toggle(rid,"am")}/>
                    </td>"""

if OLD_AM_CELL in content:
    content = content.replace(OLD_AM_CELL, NEW_TEAM_AM_CELL)
    changes += 1
    print("FIX 3b: Team cell added with auto-fill description logic")
else:
    print("WARN 3b: AM cell pattern not found")

# Also update description cell to trigger team auto-fill on change
OLD_DESC = """                    <td className="px-2 py-2 min-w-[160px]">
                      <Inp value={r.description||""} onChange={e=>setCell(rid,"description",e.target.value)}
                        placeholder="Formwork, rebar, concrete pour..."/>
                    </td>"""

NEW_DESC = """                    <td className="px-2 py-2 min-w-[160px]">
                      <Inp value={r.description||""} onChange={e=>{
                        const v=e.target.value;
                        setCell(rid,"description",v);
                        // Auto-fill all same-team rows
                        if(r.teamNo&&r.teamNo.trim()){
                          setRows(prev=>prev.map(x=>(x.rowId!==rid&&x.id!==rid)&&x.teamNo===r.teamNo?{...x,description:v}:x));
                        }
                      }} placeholder="Formwork, rebar, concrete pour..."/>
                    </td>"""

if OLD_DESC in content:
    content = content.replace(OLD_DESC, NEW_DESC)
    changes += 1
    print("FIX 3c: Description auto-fills same-team rows on change")
else:
    print("WARN 3c: Description cell pattern not found")

# ══════════════════════════════════════════════════════════════════════
# FIX 4: Add Attendance section to DPR View mode
# Insert after the existing sections list (after the .filter().map() block)
# ══════════════════════════════════════════════════════════════════════
OLD_VIEW_END = """            {sel.issues&&<div className="bg-red-50 border border-red-200 rounded-xl p-4"><div className="text-xs font-bold text-red-600 uppercase mb-1">Issues / Delays</div><p className="text-sm text-slate-700">{sel.issues}</p></div>}
            {sel.remarks&&<div className="bg-slate-50 border border-slate-200 rounded-xl p-4"><div className="text-xs font-bold text-slate-500 uppercase mb-1">Remarks</div><p className="text-sm text-slate-700">{sel.remarks}</p></div>}"""

NEW_VIEW_END = """            {/* ── Attendance Register in View ── */}
            <DprAttendanceViewPanel dprId={sel.id} loadAttendance={loadAttendance} subcontractors={subcontractors}/>
            {sel.issues&&<div className="bg-red-50 border border-red-200 rounded-xl p-4"><div className="text-xs font-bold text-red-600 uppercase mb-1">Issues / Delays</div><p className="text-sm text-slate-700">{sel.issues}</p></div>}
            {sel.remarks&&<div className="bg-slate-50 border border-slate-200 rounded-xl p-4"><div className="text-xs font-bold text-slate-500 uppercase mb-1">Remarks</div><p className="text-sm text-slate-700">{sel.remarks}</p></div>}"""

if OLD_VIEW_END in content:
    content = content.replace(OLD_VIEW_END, NEW_VIEW_END)
    changes += 1
    print("FIX 4: Attendance panel added to View mode")
else:
    print("WARN 4: View mode end pattern not found")

# ══════════════════════════════════════════════════════════════════════
# FIX 5: Insert DprAttendanceViewPanel component before DprAttendancePanel
# ══════════════════════════════════════════════════════════════════════
VIEW_PANEL_CODE = """// ── DPR Attendance View Panel (read-only) ────────────────────────────
const DprAttendanceViewPanel = ({ dprId, loadAttendance, subcontractors = [] }) => {
  const [rows, setRows]   = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!dprId) { setLoading(false); return; }
    loadAttendance(dprId).then(att => { setRows(att||[]); setLoading(false); });
  }, [dprId, loadAttendance]);

  if (loading) return <div className="p-4 text-center text-sm text-slate-400">Loading attendance...</div>;
  if (!rows.length) return null;

  const subName = id => (subcontractors.find(s=>s.id===id)||{}).name||"";
  const presentAM = rows.filter(r=>r.am==="P").length;
  const presentPM = rows.filter(r=>r.pm==="P").length;

  // Group by team
  const teams = [...new Set(rows.map(r=>r.teamNo||"").filter(Boolean))];

  return (
    <div className="bg-white rounded-xl border-2 border-slate-200 overflow-hidden shadow-sm">
      <div className="bg-slate-800 px-4 py-2.5 flex items-center justify-between">
        <span className="text-white font-bold text-sm">Daily Attendance Register</span>
        <div className="flex gap-4 text-xs">
          <span className="text-green-300 font-bold">AM Present: {presentAM}</span>
          <span className="text-blue-300 font-bold">PM Present: {presentPM}</span>
          <span className="text-red-300 font-bold">Absent: {rows.filter(r=>r.am==="A"&&r.pm==="A").length}</span>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs min-w-[700px]">
          <thead>
            <tr className="bg-slate-700 text-white">
              {["S.No","ID No","Name","Designation","Team","A.M","P.M","O.T","Description of Work"].map(h=>(
                <th key={h} className="px-2 py-2.5 text-left font-bold uppercase tracking-wide whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r,idx)=>{
              const absent = r.am==="A"&&r.pm==="A";
              return (
                <tr key={r.id||idx} className={`border-b border-slate-100 ${absent?"bg-red-50":idx%2===0?"bg-white":"bg-slate-50/50"}`}>
                  <td className="px-2 py-2 text-slate-400 font-mono text-center">{idx+1}</td>
                  <td className="px-2 py-2 font-mono font-bold text-blue-700">{r.empId||"—"}</td>
                  <td className="px-2 py-2 font-semibold text-slate-800 whitespace-nowrap">{r.name||"—"}</td>
                  <td className="px-2 py-2 text-slate-500">{r.designation||"—"}</td>
                  <td className="px-2 py-2 font-semibold text-purple-700">{r.teamNo||"—"}</td>
                  <td className="px-2 py-2 text-center">
                    <span className={`inline-block w-7 h-7 rounded-lg font-black text-sm flex items-center justify-center border-2 ${r.am==="P"?"bg-green-100 text-green-700 border-green-400":"bg-red-100 text-red-700 border-red-400"}`}>{r.am}</span>
                  </td>
                  <td className="px-2 py-2 text-center">
                    <span className={`inline-block w-7 h-7 rounded-lg font-black text-sm flex items-center justify-center border-2 ${r.pm==="P"?"bg-green-100 text-green-700 border-green-400":"bg-red-100 text-red-700 border-red-400"}`}>{r.pm}</span>
                  </td>
                  <td className="px-2 py-2 text-center text-amber-700 font-semibold">{r.ot&&r.ot!=="0"?r.ot:"—"}</td>
                  <td className="px-2 py-2 text-slate-600 max-w-[200px] truncate">{r.description||"—"}</td>
                </tr>
              );
            })}
          </tbody>
          <tfoot>
            <tr className="bg-slate-700 text-white">
              <td colSpan={5} className="px-3 py-2 font-bold text-xs">TOTAL PRESENT</td>
              <td className="px-2 py-2 text-center font-black text-green-300">{presentAM}</td>
              <td className="px-2 py-2 text-center font-black text-blue-300">{presentPM}</td>
              <td colSpan={2} className="px-3 py-2 text-xs text-slate-300">
                Total: {rows.length} workers | Absent: {rows.filter(r=>r.am==="A"&&r.pm==="A").length}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
      {teams.length > 0 && (
        <div className="bg-slate-50 border-t border-slate-200 px-4 py-3">
          <div className="text-xs font-bold text-slate-500 uppercase mb-2">Team Summary</div>
          <div className="flex flex-wrap gap-2">
            {teams.map(t=>{
              const tRows = rows.filter(r=>r.teamNo===t);
              const tDesc = tRows.find(r=>r.description)?.description||"";
              return (
                <div key={t} className="bg-white border border-purple-200 rounded-lg px-3 py-2 min-w-[100px]">
                  <div className="text-xs font-bold text-purple-700">{t}</div>
                  <div className="text-lg font-black text-slate-800">{tRows.filter(r=>r.am==="P"||r.pm==="P").length}<span className="text-xs font-normal text-slate-400">/{tRows.length}</span></div>
                  {tDesc&&<div className="text-xs text-slate-400 truncate max-w-[120px]" title={tDesc}>{tDesc}</div>}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
// ── End DprAttendanceViewPanel ────────────────────────────────────────

"""

INSERT_BEFORE = 'const DprAttendancePanel = ('
if INSERT_BEFORE in content:
    content = content.replace(INSERT_BEFORE, VIEW_PANEL_CODE + INSERT_BEFORE, 1)
    changes += 1
    print("FIX 5: DprAttendanceViewPanel component inserted")
else:
    print("WARN 5: DprAttendancePanel not found for insertion")

# ══════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════
with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

print()
print("="*60)
print("TOTAL FIXES:", changes)
print()
print("ALSO RUN THIS SQL IN SUPABASE:")
print("  ALTER TABLE dpr_attendance ADD COLUMN IF NOT EXISTS employee_id text DEFAULT '';")
print("  ALTER TABLE dpr_attendance ADD COLUMN IF NOT EXISTS emp_name text DEFAULT '';")
print("  ALTER TABLE dpr_attendance ADD COLUMN IF NOT EXISTS designation text DEFAULT '';")
print()
print("THEN RUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js')
print('  git commit -m "Fix: DPR attendance view + Team column + save all rows"')
print('  git push')
print("="*60)
input("Press Enter...")
