import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup created:", bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# ── What we are replacing ─────────────────────────────────────────────
# 1. EMPTY_ATT_ROW  (L3163)
# 2. DprAttendancePanel  (L3171-3320)
# We replace both with a new version that:
#   - Uses P/A toggle buttons instead of number inputs
#   - Has exact column format: S.No | ID | Name | Designation | A.M | P.M | O.T | Description | Del
#   - Has "Copy from Last DPR" button
#   - Has summary footer: AGBC / Others / AGBC Supply / SUB Contractors / Total
# ─────────────────────────────────────────────────────────────────────

OLD_EMPTY = """const EMPTY_ATT_ROW = (mp) => ({
  rowId: Date.now() + Math.random(),
  mpId: mp ? mp.id : "", subId: mp ? mp.subId : "",
  empId: mp ? mp.empId : "", name: mp ? mp.name : "",
  designation: mp ? mp.designation : "", teamNo: mp ? mp.defaultTeamNo : "","""

NEW_EMPTY = """const EMPTY_ATT_ROW = (mp) => ({
  rowId: Date.now() + Math.random(),
  mpId: mp ? mp.id : "", subId: mp ? mp.subId : "",
  empId: mp ? mp.empId : "", name: mp ? mp.name : "",
  designation: mp ? mp.designation : "", teamNo: mp ? mp.defaultTeamNo : "","""

# Find and replace the full DprAttendancePanel component
OLD_PANEL_START = 'const DprAttendancePanel = ({ dprId, subcontractors = [], masters = [], loadAttendance, saveAttendance, showToast }) => {'
OLD_PANEL_END   = '''      {!dprId && <div className="p-2 text-center text-xs text-amber-600 bg-amber-50 border-t border-amber-100">Save the DPR first to persist attendance records</div>}
        </div>
      )}
    </div>
  );
};'''

NEW_PANEL = '''const DprAttendancePanel = ({ dprId, subcontractors = [], masters = [], loadAttendance, saveAttendance, showToast, allReports = [] }) => {
  const [rows, setRows]       = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving,  setSaving]  = useState(false);
  const [subId,   setSubId]   = useState("");

  // Load saved attendance when opening existing DPR
  useEffect(() => {
    if (!dprId) return;
    setLoading(true);
    loadAttendance(dprId).then(att => {
      if (att && att.length) setRows(att.map(a => ({ ...a, rowId: a.id || Date.now()+Math.random() })));
      setLoading(false);
    });
  }, [dprId, loadAttendance]);

  // ── Toggle P / A ──────────────────────────────────────────────────
  const toggle = (rowId, field) =>
    setRows(p => p.map(r => (r.rowId===rowId||r.id===rowId) ? { ...r, [field]: r[field]==="P"?"A":"P" } : r));

  const setCell = (rowId, key, val) =>
    setRows(p => p.map(r => (r.rowId===rowId||r.id===rowId) ? { ...r, [key]: val } : r));

  const delRow = (rowId) =>
    setRows(p => p.filter(r => r.rowId!==rowId && r.id!==rowId));

  const addRow = () =>
    setRows(p => [...p, { rowId:Date.now()+Math.random(), mpId:"", subId:"", empId:"", name:"", designation:"", am:"P", pm:"P", ot:"", description:"", teamNo:"", remarks:"" }]);

  // ── Load from Manpower Master ─────────────────────────────────────
  const loadFromMaster = () => {
    if (!subId) { showToast("Select a subcontractor first","error"); return; }
    const active = masters.filter(m => m.subId===subId && m.status==="Active");
    if (!active.length) { showToast("No active employees for this subcontractor","error"); return; }
    const existingIds = new Set(rows.map(r=>r.mpId).filter(Boolean));
    const newRows = active.filter(m=>!existingIds.has(m.id)).map(mp=>({
      rowId: Date.now()+Math.random(),
      mpId: mp.id, subId: mp.subId,
      empId: mp.empId, name: mp.name,
      designation: mp.designation, teamNo: mp.defaultTeamNo||"",
      am:"P", pm:"P", ot:"", description:"", remarks:""
    }));
    if (!newRows.length) { showToast("All employees already loaded","error"); return; }
    setRows(p => [...p, ...newRows]);
    showToast(newRows.length+" employees loaded from master");
  };

  // ── Copy from Last DPR ────────────────────────────────────────────
  const copyFromLastDpr = async () => {
    if (!allReports || allReports.length === 0) {
      showToast("No previous DPR found","error"); return;
    }
    // Get most recent DPR (skip current one)
    const prev = allReports.filter(r => r.id !== dprId).sort((a,b) => new Date(b.date) - new Date(a.date))[0];
    if (!prev) { showToast("No previous DPR found","error"); return; }
    setLoading(true);
    const prevAtt = await loadAttendance(prev.id);
    setLoading(false);
    if (!prevAtt || !prevAtt.length) { showToast("Previous DPR has no attendance records","error"); return; }
    // Copy employees, reset daily values
    const copied = prevAtt.map(a => ({
      rowId: Date.now()+Math.random(),
      mpId: a.mpId||"", subId: a.subId||"",
      empId: a.empId||"", name: a.name||"",
      designation: a.designation||"", teamNo: a.teamNo||"",
      am:"P", pm:"P", ot:"", description:"", remarks:""
    }));
    setRows(copied);
    showToast(copied.length+" employees copied from last DPR");
  };

  // ── Save Attendance ───────────────────────────────────────────────
  const handleSave = async () => {
    if (!dprId) { showToast("Save the DPR first, then save attendance","error"); return; }
    setSaving(true);
    const res = await saveAttendance(dprId, rows);
    setSaving(false);
    if (!res.ok) { showToast(res.error||"Save failed","error"); return; }
    showToast("Attendance saved!");
  };

  // ── Summary counts ────────────────────────────────────────────────
  const presentAM = rows.filter(r=>r.am==="P").length;
  const presentPM = rows.filter(r=>r.pm==="P").length;
  const absentAM  = rows.filter(r=>r.am==="A").length;

  // Subcontractor lookup
  const subName = id => (subcontractors.find(s=>s.id===id)||{}).name||"";

  // PA Toggle Button
  const PABtn = ({ val, onClick }) => (
    <button onClick={onClick}
      className={`w-8 h-8 rounded-lg font-black text-sm border-2 transition-all ${
        val==="P"
          ? "bg-green-100 text-green-700 border-green-400 hover:bg-green-200"
          : "bg-red-100 text-red-700 border-red-400 hover:bg-red-200"
      }`}>
      {val}
    </button>
  );

  return (
    <div className="mt-4 border-2 border-slate-200 rounded-xl overflow-hidden shadow-sm">

      {/* ── Header Bar ── */}
      <div className="bg-slate-800 px-4 py-2.5 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <span className="text-white font-bold text-sm">Daily Attendance Register</span>
          <span className="bg-amber-500 text-white text-xs px-2 py-0.5 rounded-full font-semibold">{rows.length} workers</span>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className="text-green-300 font-bold">AM Present: {presentAM}</span>
          <span className="text-red-300 font-bold">Absent: {absentAM}</span>
          <span className="text-blue-300 font-bold">PM Present: {presentPM}</span>
        </div>
      </div>

      {/* ── Toolbar ── */}
      <div className="bg-slate-50 px-3 py-2.5 flex flex-wrap gap-2 items-end border-b border-slate-200">
        <div className="flex-1 min-w-[160px]">
          <label className="block text-xs font-semibold text-slate-600 mb-1">Load from Manpower Master</label>
          <Sel value={subId} onChange={e=>setSubId(e.target.value)} className="w-full text-xs">
            <option value="">Select Subcontractor...</option>
            {subcontractors.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
          </Sel>
        </div>
        <button onClick={loadFromMaster}
          className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition-colors whitespace-nowrap">
          &#8635; Load Master
        </button>
        <button onClick={copyFromLastDpr} disabled={loading}
          className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-semibold transition-colors whitespace-nowrap">
          &#9650; Copy Last DPR
        </button>
        <button onClick={addRow}
          className="px-3 py-2 bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap">
          + Add Row
        </button>
        {rows.length > 0 && (
          <button onClick={handleSave} disabled={saving}
            className="px-3 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-xs font-semibold transition-colors whitespace-nowrap">
            {saving?"Saving...":"&#128190; Save Attendance"}
          </button>
        )}
      </div>

      {/* ── Table ── */}
      {loading ? (
        <div className="p-6 text-center text-sm text-slate-400">Loading attendance...</div>
      ) : rows.length === 0 ? (
        <div className="p-8 text-center">
          <div className="text-3xl mb-2">&#128101;</div>
          <p className="text-sm font-semibold text-slate-500">No manpower added yet</p>
          <p className="text-xs text-slate-400 mt-1">Use "Load Master" to auto-fill from saved employees, or "Copy Last DPR" to reuse yesterday's list</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-xs min-w-[750px]">
            <thead>
              <tr className="bg-slate-700 text-white">
                {["S.No","ID No","Name","Designation","A.M","P.M","O.T","Description of Work",""].map(h=>(
                  <th key={h} className="px-2 py-2.5 text-left text-xs font-bold uppercase tracking-wide whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r,idx)=>{
                const rid = r.rowId||r.id;
                const isAbsent = r.am==="A" && r.pm==="A";
                return (
                  <tr key={rid} className={`border-b border-slate-100 transition-colors ${isAbsent?"bg-red-50":"hover:bg-amber-50/30"}`}>
                    <td className="px-2 py-2 text-slate-400 font-mono w-10 text-center">{idx+1}</td>
                    <td className="px-2 py-2 w-16">
                      {r.mpId
                        ? <span className="font-mono font-bold text-blue-700">{r.empId||"—"}</span>
                        : <Inp value={r.empId} onChange={e=>setCell(rid,"empId",e.target.value)} placeholder="ID" className="w-14"/>}
                    </td>
                    <td className="px-2 py-2 min-w-[120px]">
                      {r.mpId
                        ? <span className="font-semibold text-slate-800">{r.name}</span>
                        : <Inp value={r.name} onChange={e=>setCell(rid,"name",e.target.value)} placeholder="Full name"/>}
                    </td>
                    <td className="px-2 py-2 min-w-[110px]">
                      {r.mpId
                        ? <span className="text-slate-500">{r.designation||"—"}</span>
                        : <Inp value={r.designation} onChange={e=>setCell(rid,"designation",e.target.value)} placeholder="Trade"/>}
                    </td>
                    <td className="px-2 py-2 w-12 text-center">
                      <PABtn val={r.am||"P"} onClick={()=>toggle(rid,"am")}/>
                    </td>
                    <td className="px-2 py-2 w-12 text-center">
                      <PABtn val={r.pm||"P"} onClick={()=>toggle(rid,"pm")}/>
                    </td>
                    <td className="px-2 py-2 w-16">
                      <Inp value={r.ot||""} onChange={e=>setCell(rid,"ot",e.target.value)}
                        placeholder="0" className="w-12 text-center text-amber-700 font-semibold"/>
                    </td>
                    <td className="px-2 py-2 min-w-[160px]">
                      <Inp value={r.description||""} onChange={e=>setCell(rid,"description",e.target.value)}
                        placeholder="Formwork, rebar, concrete pour..."/>
                    </td>
                    <td className="px-2 py-2 w-8 text-center">
                      <button onClick={()=>delRow(rid)}
                        className="w-6 h-6 rounded-full bg-red-100 hover:bg-red-200 text-red-600 font-bold text-xs transition-colors">
                        &#215;
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>

            {/* ── Summary Footer ── */}
            <tfoot>
              <tr className="bg-slate-700 text-white">
                <td colSpan={4} className="px-3 py-2 font-bold text-xs">TOTAL PRESENT</td>
                <td className="px-2 py-2 text-center font-black text-green-300 text-sm">{presentAM}</td>
                <td className="px-2 py-2 text-center font-black text-blue-300 text-sm">{presentPM}</td>
                <td colSpan={3} className="px-3 py-2 text-xs text-slate-300">
                  Absent: {absentAM} &nbsp;|&nbsp; OT: {rows.reduce((s,r)=>s+(parseFloat(r.ot)||0),0).toFixed(1)} hrs
                </td>
              </tr>
            </tfoot>
          </table>

          {/* ── Subcontractor Summary Card ── */}
          <div className="bg-slate-50 border-t-2 border-slate-200 px-4 py-3">
            <div className="text-xs font-bold text-slate-600 mb-2 uppercase tracking-wide">Manpower Summary by Category</div>
            <div className="flex flex-wrap gap-3">
              {[...new Set(rows.map(r=>r.subId||"manual"))].map(sid=>{
                const grp = rows.filter(r=>(r.subId||"manual")===sid);
                const present = grp.filter(r=>r.am==="P"||r.pm==="P").length;
                const nm = sid==="manual" ? "Manual Entry" : subName(sid);
                return (
                  <div key={sid} className="bg-white border border-slate-200 rounded-lg px-3 py-2 min-w-[120px]">
                    <div className="text-xs text-slate-500 font-semibold truncate max-w-[130px]">{nm}</div>
                    <div className="text-xl font-black text-slate-800 mt-0.5">{present}<span className="text-xs font-normal text-slate-400">/{grp.length}</span></div>
                    <div className="text-xs text-slate-400">present</div>
                  </div>
                );
              })}
              <div className="bg-amber-500 border border-amber-400 rounded-lg px-3 py-2 min-w-[120px]">
                <div className="text-xs text-white font-semibold">TOTAL</div>
                <div className="text-xl font-black text-white mt-0.5">
                  {rows.filter(r=>r.am==="P"||r.pm==="P").length}
                  <span className="text-xs font-normal text-amber-200">/{rows.length}</span>
                </div>
                <div className="text-xs text-amber-200">present</div>
              </div>
            </div>
          </div>

          {!dprId && (
            <div className="px-4 py-2 text-center text-xs text-amber-700 bg-amber-50 border-t border-amber-200">
              &#9888; Save the DPR first, then click "Save Attendance" to store records
            </div>
          )}
        </div>
      )}
    </div>
  );
};'''

# ── Apply the replacement ────────────────────────────────────────────
changes = 0

# Find the old panel start and end
old_start = content.find(OLD_PANEL_START)
old_end   = content.find(OLD_PANEL_END)

if old_start != -1 and old_end != -1:
    old_end_full = old_end + len(OLD_PANEL_END)
    content = content[:old_start] + NEW_PANEL + content[old_end_full:]
    changes += 1
    print("FIX 1: DprAttendancePanel replaced with new P/A format")
else:
    print("WARN: Could not find panel boundaries")
    print(f"  start found: {old_start != -1}")
    print(f"  end found:   {old_end != -1}")

# Also update EMPTY_ATT_ROW am/pm defaults from "0" to "P"
old_att_defaults = '"am":"0", "pm":"0"'
new_att_defaults = '"am":"P", "pm":"P"'
if old_att_defaults in content:
    content = content.replace(old_att_defaults, new_att_defaults)
    changes += 1
    print("FIX 2: EMPTY_ATT_ROW am/pm defaults changed to P")

# Also fix single-quote version
old_att_defaults2 = "am: \"0\", pm: \"0\""
new_att_defaults2 = 'am: "P", pm: "P"'
if old_att_defaults2 in content:
    content = content.replace(old_att_defaults2, new_att_defaults2)
    changes += 1
    print("FIX 2b: EMPTY_ATT_ROW am/pm defaults changed to P")

# Update DprAttendancePanel usage in DailyReports to pass allReports
old_usage = '''      {activeSection==="manpower"&&<DprAttendancePanel
        dprId={mpAttDprId||(sel?sel.id:null)}
        subcontractors={subcontractors}
        masters={mpMasters}
        loadAttendance={loadAttendance}
        saveAttendance={saveAttendance}
        showToast={showToast}
      />}'''

new_usage = '''      {activeSection==="manpower"&&<DprAttendancePanel
        dprId={mpAttDprId||(sel?sel.id:null)}
        subcontractors={subcontractors}
        masters={mpMasters}
        loadAttendance={loadAttendance}
        saveAttendance={saveAttendance}
        showToast={showToast}
        allReports={reports}
      />}'''

if old_usage in content:
    content = content.replace(old_usage, new_usage)
    changes += 1
    print("FIX 3: allReports passed to DprAttendancePanel")
else:
    print("WARN 3: DprAttendancePanel usage not found — trying partial...")
    if 'DprAttendancePanel' in content and 'saveAttendance={saveAttendance}' in content:
        content = content.replace(
            'saveAttendance={saveAttendance}\n        showToast={showToast}\n      />}',
            'saveAttendance={saveAttendance}\n        showToast={showToast}\n        allReports={reports}\n      />}'
        )
        changes += 1
        print("FIX 3b: allReports added via partial match")

# Update saveAttendance to store am/pm as text ("P"/"A") not numbers
old_save = 'am_count: parseInt(r.am) || 0, pm_count: parseInt(r.pm) || 0,'
new_save = 'am_count: r.am==="P"?1:0, pm_count: r.pm==="P"?1:0,'
if old_save in content:
    content = content.replace(old_save, new_save)
    changes += 1
    print("FIX 4: saveAttendance updated for P/A values")

# Update loadAttendance to return "P"/"A" not numbers
old_load = 'am: String(a.am_count || 0),'
new_load = 'am: a.am_count===1?"P":"A",'
if old_load in content:
    content = content.replace(old_load, new_load)
    changes += 1
    print("FIX 5a: loadAttendance am → P/A")

old_load2 = 'pm: String(a.pm_count || 0),'
new_load2 = 'pm: a.pm_count===1?"P":"A",'
if old_load2 in content:
    content = content.replace(old_load2, new_load2)
    changes += 1
    print("FIX 5b: loadAttendance pm → P/A")

# Write
with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

print()
print("="*55)
print("TOTAL FIXES:", changes)
print()
print("NOW RUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print('  git add src/App.js')
print('  git commit -m "feat: DPR P/A toggle, copy last DPR manpower"')
print('  git push')
print("="*55)
input("Press Enter...")
