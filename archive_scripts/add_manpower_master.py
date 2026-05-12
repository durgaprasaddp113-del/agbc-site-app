import shutil, re
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

content = "".join(lines)
changes = 0

# ══════════════════════════════════════════════════════════════════════
# BLOCK 1: Find useManpowerMaster hook boundaries
# ══════════════════════════════════════════════════════════════════════
hook_start = -1
hook_end   = -1
for i, l in enumerate(lines):
    if "function useManpowerMaster()" in l:
        hook_start = i
    if hook_start != -1 and hook_end == -1:
        if "return {" in l and i > hook_start + 5:
            # find closing }; of hook
            for j in range(i, min(i+10, len(lines))):
                stripped = lines[j].strip()
                if stripped == "};" or stripped == "}" :
                    hook_end = j
                    break
print(f"Hook: L{hook_start+1} → L{hook_end+1}")

# ══════════════════════════════════════════════════════════════════════
# BLOCK 2: Find ManpowerMaster component boundaries (brace counting)
# ══════════════════════════════════════════════════════════════════════
comp_start = -1
comp_end   = -1
for i, l in enumerate(lines):
    if "const ManpowerMaster = ({" in l:
        comp_start = i
        break

if comp_start != -1:
    depth = 0
    for i in range(comp_start, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        if depth <= 0 and i > comp_start + 5:
            comp_end = i
            break
print(f"Component: L{comp_start+1} → L{comp_end+1}")

# ══════════════════════════════════════════════════════════════════════
# BLOCK 3: NEW useManpowerMaster hook code
# ══════════════════════════════════════════════════════════════════════
NEW_HOOK = r"""function useManpowerMaster() {
  const [masters, setMasters] = useState([]);
  const [loading, setLoading] = useState(true);
  const loadData = useCallback(async () => {
    const { data, error } = await supabase.from("manpower_master").select("*").order("created_at", { ascending: true });
    if (error) { console.error("ManpowerMaster:", error.message); setLoading(false); return; }
    if (data) setMasters(data.map(m => ({
      id: m.id, subId: m.subcontractor_id || "",
      empId: m.employee_id || "", name: m.name || "",
      designation: m.designation || "", defaultTeamNo: m.default_team_no || "",
      status: m.status || "Active", dateJoined: m.date_joined || "",
      dateLeft: m.date_left || "", remarks: m.remarks || "",
    })));
    setLoading(false);
  }, []);
  useEffect(() => { loadData(); }, [loadData]);

  const addMaster = async (f) => {
    const { error } = await supabase.from("manpower_master").insert([{
      subcontractor_id: f.subId || null, employee_id: f.empId || "",
      name: f.name || "", designation: f.designation || "",
      default_team_no: f.defaultTeamNo || "", status: f.status || "Active",
      date_joined: f.dateJoined || null, date_left: f.dateLeft || null, remarks: f.remarks || "",
    }]);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };

  const updateMaster = async (id, f) => {
    const { error } = await supabase.from("manpower_master").update({
      subcontractor_id: f.subId || null, employee_id: f.empId || "",
      name: f.name || "", designation: f.designation || "",
      default_team_no: f.defaultTeamNo || "", status: f.status || "Active",
      date_joined: f.dateJoined || null, date_left: f.dateLeft || null, remarks: f.remarks || "",
    }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };

  const removeMaster = async (id) => {
    const { error } = await supabase.from("manpower_master").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };

  const toggleMpStatus = async (id, cur) => {
    const { error } = await supabase.from("manpower_master")
      .update({ status: cur === "Active" ? "Inactive" : "Active" }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };

  const loadAttendance = async (dprId) => {
    if (!dprId) return [];
    const { data, error } = await supabase.from("dpr_attendance").select("*").eq("dpr_id", dprId).order("created_at");
    if (error) return [];
    return (data || []).map(a => ({
      id: a.id, dprId: a.dpr_id, subId: a.subcontractor_id || "",
      mpId: a.manpower_id || "", am: String(a.am_count || 0),
      pm: String(a.pm_count || 0), ot: String(a.ot_hours || 0),
      description: a.description_of_work || "", teamNo: a.team_no || "", remarks: a.daily_remarks || "",
    }));
  };

  const saveAttendance = async (dprId, rows) => {
    if (!dprId) return { ok: false, error: "No DPR ID" };
    await supabase.from("dpr_attendance").delete().eq("dpr_id", dprId);
    const valid = rows.filter(r => r.mpId);
    if (!valid.length) return { ok: true };
    const { error } = await supabase.from("dpr_attendance").insert(valid.map(r => ({
      dpr_id: dprId, subcontractor_id: r.subId || null, manpower_id: r.mpId || null,
      am_count: parseInt(r.am) || 0, pm_count: parseInt(r.pm) || 0,
      ot_hours: parseFloat(r.ot) || 0, description_of_work: r.description || "",
      team_no: r.teamNo || "", daily_remarks: r.remarks || "",
    })));
    if (error) return { ok: false, error: error.message };
    return { ok: true };
  };

  return { masters, loading, addMaster, updateMaster, removeMaster, toggleMpStatus, loadAttendance, saveAttendance };
}
"""

# ══════════════════════════════════════════════════════════════════════
# BLOCK 4: NEW ManpowerMaster component code
# ══════════════════════════════════════════════════════════════════════
NEW_COMP = r"""const EMPTY_MP_FORM = () => ({ subId:"", empId:"", name:"", designation:"", defaultTeamNo:"", status:"Active", dateJoined:"", dateLeft:"", remarks:"" });
const MP_TRADES = ["Foreman","Carpenter","Mason","Plumber","Electrician","Steel Fixer","Bar Bender","Shuttering Carpenter","Scaffolder","Helper","Driver","Equipment Operator","Painter","Welder","Tiler","Waterproofing Applicator","Other"];

const ManpowerMaster = ({ subcontractors = [], projects = [], showToast }) => {
  const { masters, loading, addMaster, updateMaster, removeMaster, toggleMpStatus } = useManpowerMaster();
  const [mode,      setMode]      = useState("list");
  const [sel,       setSel]       = useState(null);
  const [saving,    setSaving]    = useState(false);
  const [search,    setSearch]    = useState("");
  const [fSub,      setFSub]      = useState("All");
  const [fStatus,   setFStatus]   = useState("Active");
  const [confirmId, setConfirmId] = useState(null);
  const [form,      setForm]      = useState(EMPTY_MP_FORM());
  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));

  const filtered = masters.filter(m => {
    if (fSub !== "All" && m.subId !== fSub) return false;
    if (fStatus !== "All" && m.status !== fStatus) return false;
    if (search) { const q = search.toLowerCase(); if (!`${m.empId} ${m.name} ${m.designation}`.toLowerCase().includes(q)) return false; }
    return true;
  });

  const openCreate = () => { setForm({ ...EMPTY_MP_FORM(), subId: fSub !== "All" ? fSub : "" }); setSel(null); setMode("form"); };
  const openEdit   = m  => { setSel(m); setForm({ subId:m.subId, empId:m.empId, name:m.name, designation:m.designation, defaultTeamNo:m.defaultTeamNo, status:m.status, dateJoined:m.dateJoined, dateLeft:m.dateLeft, remarks:m.remarks }); setMode("form"); };

  const handleSave = async () => {
    if (!form.subId) { showToast("Select a subcontractor","error"); return; }
    if (!form.empId.trim()) { showToast("Employee ID required","error"); return; }
    if (!form.name.trim())  { showToast("Employee name required","error"); return; }
    setSaving(true);
    const res = sel ? await updateMaster(sel.id, form) : await addMaster(form);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Save failed","error"); return; }
    showToast(sel ? "Employee updated!" : "Employee added!"); setMode("list"); setSel(null);
  };

  const handleDelete = async (id) => {
    const res = await removeMaster(id);
    if (!res.ok) { showToast(res.error,"error"); return; }
    showToast("Employee deleted!"); setConfirmId(null);
  };

  const subName = id => (subcontractors.find(s => s.id === id) || {}).name || "—";
  const totFor  = st => masters.filter(m => (fSub === "All" || m.subId === fSub) && m.status === st).length;
  const totAll  = masters.filter(m => fSub === "All" || m.subId === fSub).length;

  if (mode === "form") return (
    <div className="p-4 max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-5">
        <button onClick={() => { setMode("list"); setSel(null); }} className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors text-lg">&#8592;</button>
        <div><h2 className="text-lg font-bold text-slate-800">{sel ? "Edit Employee" : "Add Employee"}</h2><p className="text-xs text-slate-400">Manpower Master Record</p></div>
      </div>
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <Lbl t="Subcontractor / Company" req/>
            <Sel value={form.subId} onChange={set("subId")}>
              <option value="">Select Subcontractor...</option>
              {subcontractors.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </Sel>
          </div>
          <div><Lbl t="Employee ID / Labour Card No" req/><Inp value={form.empId} onChange={set("empId")} placeholder="e.g. LC-001"/></div>
          <div><Lbl t="Employee Name" req/><Inp value={form.name} onChange={set("name")} placeholder="Full name"/></div>
          <div>
            <Lbl t="Designation / Trade"/>
            <Sel value={form.designation} onChange={set("designation")}>
              <option value="">Select Trade...</option>
              {MP_TRADES.map(d => <option key={d}>{d}</option>)}
            </Sel>
          </div>
          <div><Lbl t="Default Team No"/><Inp value={form.defaultTeamNo} onChange={set("defaultTeamNo")} placeholder="e.g. T-1"/></div>
          <div>
            <Lbl t="Status"/>
            <Sel value={form.status} onChange={set("status")}>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
            </Sel>
          </div>
          <div><Lbl t="Date Joined"/><Inp type="date" value={form.dateJoined} onChange={set("dateJoined")}/></div>
          <div><Lbl t="Date Left (if resigned)"/><Inp type="date" value={form.dateLeft} onChange={set("dateLeft")}/></div>
          <div className="sm:col-span-2"><Lbl t="Remarks"/><Txta value={form.remarks} onChange={set("remarks")} placeholder="Any notes about this employee..." rows={2}/></div>
        </div>
        <div className="flex gap-2 pt-1">
          <Btn onClick={handleSave} saving={saving} label={sel ? "Update Employee" : "Save Employee"}/>
          <button onClick={() => { setMode("list"); setSel(null); }} className="px-4 py-2 rounded-lg border border-slate-200 text-slate-600 text-sm hover:bg-slate-50 transition-colors">Cancel</button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-4">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-5">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Manpower Master</h2>
          <p className="text-xs text-slate-400 mt-0.5">Reusable employee database per subcontractor — auto-fills DPR attendance</p>
        </div>
        <button onClick={openCreate} className="flex items-center gap-1.5 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-xl text-sm font-semibold shadow-sm transition-colors whitespace-nowrap">
          + Add Employee
        </button>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-5">
        {[{l:"Total",v:totAll,c:"bg-blue-50 text-blue-700 border-blue-200"},{l:"Active",v:totFor("Active"),c:"bg-green-50 text-green-700 border-green-200"},{l:"Inactive",v:totFor("Inactive"),c:"bg-red-50 text-red-700 border-red-200"}].map(x=>(
          <div key={x.l} className={`rounded-xl border p-3 text-center ${x.c}`}>
            <div className="text-2xl font-black">{x.v}</div>
            <div className="text-xs font-semibold mt-0.5">{x.l}</div>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        <Sel value={fSub} onChange={e=>setFSub(e.target.value)} className="w-auto">
          <option value="All">All Companies</option>
          {subcontractors.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
        </Sel>
        <Sel value={fStatus} onChange={e=>setFStatus(e.target.value)} className="w-auto">
          <option value="All">All Status</option>
          <option value="Active">Active Only</option>
          <option value="Inactive">Inactive Only</option>
        </Sel>
        <SearchBar value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search name, ID, trade..."/>
      </div>

      {loading ? <Spinner/> : filtered.length === 0 ? <EmptyState msg="No manpower records found" onCreate={openCreate}/> : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto shadow-sm">
          <table className="w-full text-sm min-w-[800px]">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>{["S.No","Emp ID","Name","Designation","Team","Company","Status","Date Joined","Actions"].map(h=>(
                <th key={h} className="text-left px-3 py-3 text-xs font-bold text-slate-500 uppercase tracking-wide whitespace-nowrap">{h}</th>
              ))}</tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((m,idx)=>(
                <tr key={m.id} className={`hover:bg-slate-50 transition-colors ${m.status==="Inactive"?"opacity-50":""}`}>
                  <td className="px-3 py-2.5 text-slate-400 text-xs">{idx+1}</td>
                  <td className="px-3 py-2.5 font-mono text-xs text-blue-700 font-semibold">{m.empId||"—"}</td>
                  <td className="px-3 py-2.5 font-semibold text-slate-800">{m.name}</td>
                  <td className="px-3 py-2.5 text-slate-500 text-xs">{m.designation||"—"}</td>
                  <td className="px-3 py-2.5 text-slate-500 text-xs">{m.defaultTeamNo||"—"}</td>
                  <td className="px-3 py-2.5 text-xs text-slate-500 max-w-[130px] truncate">{subName(m.subId)}</td>
                  <td className="px-3 py-2.5">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${m.status==="Active"?"bg-green-50 text-green-700 border-green-200":"bg-red-50 text-red-700 border-red-200"}`}>{m.status}</span>
                  </td>
                  <td className="px-3 py-2.5 text-xs text-slate-400">{m.dateJoined||"—"}</td>
                  <td className="px-3 py-2.5">
                    <div className="flex items-center gap-1 flex-wrap">
                      <button onClick={()=>openEdit(m)} className="px-2 py-1 text-xs rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition-colors">Edit</button>
                      <button onClick={()=>toggleMpStatus(m.id,m.status)} className={`px-2 py-1 text-xs rounded-md font-medium transition-colors ${m.status==="Active"?"bg-amber-50 hover:bg-amber-100 text-amber-700":"bg-green-50 hover:bg-green-100 text-green-700"}`}>
                        {m.status==="Active"?"Deactivate":"Activate"}
                      </button>
                      <button onClick={()=>setConfirmId(m.id)} className="px-2 py-1 text-xs rounded-md bg-red-50 hover:bg-red-100 text-red-600 font-medium transition-colors">Del</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {confirmId && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-red-600 text-lg font-bold">!</span>
            </div>
            <h3 className="font-bold text-slate-800 text-center mb-1">Delete Employee?</h3>
            <p className="text-sm text-slate-500 text-center mb-5">This permanently removes the employee from master. Cannot be undone.</p>
            <div className="flex gap-2">
              <button onClick={()=>handleDelete(confirmId)} className="flex-1 py-2.5 bg-red-500 hover:bg-red-600 text-white rounded-xl text-sm font-semibold transition-colors">Delete</button>
              <button onClick={()=>setConfirmId(null)} className="flex-1 py-2.5 border border-slate-200 text-slate-700 rounded-xl text-sm hover:bg-slate-50 transition-colors">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
"""

# ══════════════════════════════════════════════════════════════════════
# BLOCK 5: DPR Attendance Panel (new component to inject above DailyReports)
# ══════════════════════════════════════════════════════════════════════
DPR_ATT_PANEL = r"""
// ── DPR Attendance Panel ─────────────────────────────────────────────
const EMPTY_ATT_ROW = (mp) => ({
  rowId: Date.now() + Math.random(),
  mpId: mp ? mp.id : "", subId: mp ? mp.subId : "",
  empId: mp ? mp.empId : "", name: mp ? mp.name : "",
  designation: mp ? mp.designation : "", teamNo: mp ? mp.defaultTeamNo : "",
  am: "0", pm: "0", ot: "0", description: "", remarks: "",
});

const DprAttendancePanel = ({ dprId, subcontractors = [], masters = [], loadAttendance, saveAttendance, showToast }) => {
  const [rows, setRows]       = useState([]);
  const [subId, setSubId]     = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving]   = useState(false);
  const [loaded, setLoaded]   = useState(false);

  useEffect(() => {
    if (dprId) {
      setLoading(true);
      loadAttendance(dprId).then(att => {
        if (att.length) { setRows(att); setLoaded(true); }
        setLoading(false);
      });
    }
  }, [dprId, loadAttendance]);

  const activeForSub = subId ? masters.filter(m => m.subId === subId && m.status === "Active") : [];

  const loadFromMaster = () => {
    if (!subId) { showToast("Select a subcontractor first","error"); return; }
    if (!activeForSub.length) { showToast("No active employees for this subcontractor","error"); return; }
    const existing = rows.filter(r => r.subId !== subId);
    const newRows  = activeForSub.map(mp => EMPTY_ATT_ROW(mp));
    setRows([...existing, ...newRows]);
    setLoaded(true);
    showToast(`Loaded ${newRows.length} employees from master`);
  };

  const setCell = (rowId, key, val) => setRows(p => p.map(r => r.rowId === rowId || r.id === rowId ? { ...r, [key]: val } : r));
  const delRow  = (rowId) => setRows(p => p.filter(r => r.rowId !== rowId && r.id !== rowId));
  const addManual = () => setRows(p => [...p, EMPTY_ATT_ROW(null)]);

  const handleSave = async () => {
    if (!dprId) { showToast("Save the DPR first, then save attendance","error"); return; }
    setSaving(true);
    const res = await saveAttendance(dprId, rows);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Save failed","error"); return; }
    showToast("Attendance saved!");
  };

  const subName = id => (subcontractors.find(s => s.id === id) || {}).name || "";
  const grouped = rows.reduce((acc, r) => { const k = r.subId||"unknown"; if (!acc[k]) acc[k]=[]; acc[k].push(r); return acc; }, {});
  const totalAM = rows.reduce((s,r) => s + (parseInt(r.am)||0), 0);
  const totalPM = rows.reduce((s,r) => s + (parseInt(r.pm)||0), 0);

  return (
    <div className="mt-4 border border-blue-200 rounded-xl overflow-hidden">
      <div className="bg-blue-600 px-4 py-2.5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-white font-bold text-sm">Detailed Attendance (from Master)</span>
          {rows.length > 0 && (
            <span className="bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full">{rows.length} employees</span>
          )}
        </div>
        <div className="flex items-center gap-2 text-xs text-blue-200">
          <span>AM: {totalAM}</span>
          <span>PM: {totalPM}</span>
        </div>
      </div>

      <div className="bg-blue-50 p-3 flex flex-wrap gap-2 items-end border-b border-blue-200">
        <div className="flex-1 min-w-[180px]">
          <label className="block text-xs font-semibold text-blue-700 mb-1">Load Subcontractor from Master</label>
          <Sel value={subId} onChange={e=>setSubId(e.target.value)} className="w-full">
            <option value="">Select Subcontractor...</option>
            {subcontractors.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
          </Sel>
        </div>
        <button onClick={loadFromMaster} className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition-colors whitespace-nowrap">
          &#8635; Load from Master
        </button>
        <button onClick={addManual} className="px-3 py-2 bg-white hover:bg-blue-50 text-blue-700 border border-blue-300 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap">
          + Add Row
        </button>
        {rows.length > 0 && dprId && (
          <button onClick={handleSave} disabled={saving} className="px-3 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-xs font-semibold transition-colors whitespace-nowrap">
            {saving ? "Saving..." : "Save Attendance"}
          </button>
        )}
      </div>

      {loading ? <div className="p-4 text-center text-sm text-slate-400">Loading attendance...</div> :
       rows.length === 0 ? (
        <div className="p-6 text-center">
          <p className="text-sm text-slate-400">No attendance records yet.</p>
          <p className="text-xs text-slate-300 mt-1">Select a subcontractor above and click "Load from Master"</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          {Object.entries(grouped).map(([gSubId, gRows]) => (
            <div key={gSubId}>
              {gSubId !== "unknown" && (
                <div className="bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-600 border-b border-slate-200">
                  {subName(gSubId)} — {gRows.filter(r=>parseInt(r.am)>0||parseInt(r.pm)>0).length}/{gRows.length} present
                </div>
              )}
              <table className="w-full text-xs min-w-[900px]">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    {["S.No","Emp ID","Name","Designation","A.M","P.M","O.T Hrs","Description of Work","Team No","Remarks",""].map(h=>(
                      <th key={h} className="text-left px-2 py-2 font-bold text-slate-500 uppercase tracking-wide whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {gRows.map((r, idx) => (
                    <tr key={r.rowId||r.id} className="hover:bg-slate-50">
                      <td className="px-2 py-1.5 text-slate-400 w-8">{idx+1}</td>
                      <td className="px-2 py-1.5 w-20">
                        {r.mpId ? <span className="font-mono text-blue-700 font-semibold">{r.empId||"—"}</span>
                          : <Inp value={r.empId} onChange={e=>setCell(r.rowId||r.id,"empId",e.target.value)} placeholder="ID"/>}
                      </td>
                      <td className="px-2 py-1.5 w-32">
                        {r.mpId ? <span className="font-semibold text-slate-800">{r.name}</span>
                          : <Inp value={r.name} onChange={e=>setCell(r.rowId||r.id,"name",e.target.value)} placeholder="Name"/>}
                      </td>
                      <td className="px-2 py-1.5 w-28">
                        {r.mpId ? <span className="text-slate-500">{r.designation||"—"}</span>
                          : <Inp value={r.designation} onChange={e=>setCell(r.rowId||r.id,"designation",e.target.value)} placeholder="Trade"/>}
                      </td>
                      <td className="px-2 py-1.5 w-16"><Inp type="number" min="0" value={r.am} onChange={e=>setCell(r.rowId||r.id,"am",e.target.value)} className="text-center font-bold text-green-700"/></td>
                      <td className="px-2 py-1.5 w-16"><Inp type="number" min="0" value={r.pm} onChange={e=>setCell(r.rowId||r.id,"pm",e.target.value)} className="text-center font-bold text-blue-700"/></td>
                      <td className="px-2 py-1.5 w-16"><Inp type="number" min="0" step="0.5" value={r.ot} onChange={e=>setCell(r.rowId||r.id,"ot",e.target.value)} className="text-center text-amber-700"/></td>
                      <td className="px-2 py-1.5 min-w-[150px]"><Inp value={r.description} onChange={e=>setCell(r.rowId||r.id,"description",e.target.value)} placeholder="Formwork, Rebar, Concrete..."/></td>
                      <td className="px-2 py-1.5 w-20"><Inp value={r.teamNo} onChange={e=>setCell(r.rowId||r.id,"teamNo",e.target.value)} placeholder="T-1"/></td>
                      <td className="px-2 py-1.5 min-w-[120px]"><Inp value={r.remarks} onChange={e=>setCell(r.rowId||r.id,"remarks",e.target.value)} placeholder="Notes"/></td>
                      <td className="px-2 py-1.5 w-8"><button onClick={()=>delRow(r.rowId||r.id)} className="text-red-400 hover:text-red-600 text-base transition-colors">&#215;</button></td>
                    </tr>
                  ))}
                </tbody>
                <tfoot className="bg-blue-50 border-t-2 border-blue-200">
                  <tr>
                    <td colSpan={4} className="px-2 py-1.5 font-bold text-xs text-blue-700">SUBTOTAL</td>
                    <td className="px-2 py-1.5 font-black text-green-700">{gRows.reduce((s,r)=>s+(parseInt(r.am)||0),0)}</td>
                    <td className="px-2 py-1.5 font-black text-blue-700">{gRows.reduce((s,r)=>s+(parseInt(r.pm)||0),0)}</td>
                    <td className="px-2 py-1.5 font-black text-amber-700">{gRows.reduce((s,r)=>s+(parseFloat(r.ot)||0),0).toFixed(1)}</td>
                    <td colSpan={4}></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          ))}
          {!dprId && <div className="p-2 text-center text-xs text-amber-600 bg-amber-50 border-t border-amber-100">Save the DPR first to persist attendance records</div>}
        </div>
      )}
    </div>
  );
};
// ── End DprAttendancePanel ────────────────────────────────────────────
"""

# ══════════════════════════════════════════════════════════════════════
# APPLY CHANGES
# ══════════════════════════════════════════════════════════════════════
new_lines = list(lines)

# Change 1: Replace useManpowerMaster hook lines
if hook_start != -1 and hook_end != -1:
    hook_replacement = NEW_HOOK.split('\n')
    new_lines[hook_start:hook_end+1] = [l + '\n' for l in hook_replacement]
    changes += 1
    print("CHANGE 1: useManpowerMaster hook replaced")
else:
    print("WARN 1: useManpowerMaster hook not found")

# Rebuild content for next search (line numbers shifted)
content2 = "".join(new_lines)
lines2 = content2.splitlines(keepends=True)

# Change 2: Replace ManpowerMaster component
comp_start2 = -1
comp_end2   = -1
for i, l in enumerate(lines2):
    if "const ManpowerMaster = ({" in l:
        comp_start2 = i
        break

if comp_start2 != -1:
    depth = 0
    for i in range(comp_start2, len(lines2)):
        depth += lines2[i].count("{") - lines2[i].count("}")
        if depth <= 0 and i > comp_start2 + 5:
            comp_end2 = i
            break
    print(f"CHANGE 2: ManpowerMaster L{comp_start2+1}→L{comp_end2+1}")
    comp_replacement = NEW_COMP.split('\n')
    lines2[comp_start2:comp_end2+1] = [l + '\n' for l in comp_replacement]
    changes += 1
else:
    print("WARN 2: ManpowerMaster component not found")

content3 = "".join(lines2)
lines3 = content3.splitlines(keepends=True)

# Change 3: Insert DprAttendancePanel before DailyReports component
dr_start = -1
for i, l in enumerate(lines3):
    if "const DailyReports = ({" in l:
        dr_start = i
        break

if dr_start != -1:
    panel_lines = [l + '\n' for l in DPR_ATT_PANEL.split('\n')]
    lines3 = lines3[:dr_start] + panel_lines + lines3[dr_start:]
    changes += 1
    print(f"CHANGE 3: DprAttendancePanel inserted before DailyReports at L{dr_start+1}")
else:
    print("WARN 3: DailyReports component not found")

content4 = "".join(lines3)
lines4 = content4.splitlines(keepends=True)

# Change 4: In DailyReports, add useManpowerMaster + mpAttendance state after existing state setup
dr_start2 = -1
for i, l in enumerate(lines4):
    if "const DailyReports = ({" in l:
        dr_start2 = i
        break

if dr_start2 != -1:
    # Find where saving/confirmId state is declared (end of state setup)
    insert_after = -1
    for j in range(dr_start2, min(dr_start2+30, len(lines4))):
        if "const [saving," in lines4[j] or "const [confirmId," in lines4[j]:
            insert_after = j
    if insert_after != -1:
        att_state = [
            "  const { masters: mpMasters, loadAttendance, saveAttendance } = useManpowerMaster();\n",
            "  const [mpAttDprId, setMpAttDprId] = useState(null);\n",
        ]
        lines4 = lines4[:insert_after+1] + att_state + lines4[insert_after+1:]
        changes += 1
        print(f"CHANGE 4: Attendance state added to DailyReports at L{insert_after+2}")
    else:
        print("WARN 4: Could not find state insertion point in DailyReports")
else:
    print("WARN 4: DailyReports not found for state injection")

content5 = "".join(lines4)
lines5 = content5.splitlines(keepends=True)

# Change 5: After DPR is saved (onAdd returns ok), set mpAttDprId
dr_start3 = -1
for i, l in enumerate(lines5):
    if "const DailyReports = ({" in l:
        dr_start3 = i
        break

if dr_start3 != -1:
    # Find handleSave in DailyReports
    hs_line = -1
    for j in range(dr_start3, min(dr_start3+200, len(lines5))):
        if "showToast(sel?" in lines5[j] and "DPR" in lines5[j]:
            hs_line = j
            break
        if "showToast(" in lines5[j] and "created" in lines5[j].lower():
            hs_line = j
            break
    if hs_line != -1:
        # Insert setMpAttDprId before the showToast line
        lines5 = lines5[:hs_line] + ["        if (res.id || res.dprId) setMpAttDprId(res.id || res.dprId);\n"] + lines5[hs_line:]
        changes += 1
        print(f"CHANGE 5: setMpAttDprId inserted after DPR save at L{hs_line+1}")
    else:
        print("WARN 5: handleSave success line not found in DailyReports")

content6 = "".join(lines5)
lines6 = content6.splitlines(keepends=True)

# Change 6: openEdit in DailyReports — set mpAttDprId when editing
dr_start4 = -1
for i, l in enumerate(lines6):
    if "const DailyReports = ({" in l:
        dr_start4 = i
        break

if dr_start4 != -1:
    for j in range(dr_start4, min(dr_start4+200, len(lines6))):
        if "openEdit" in lines6[j] and "=>" in lines6[j] and "setSel(" in lines6[j]:
            # Add setMpAttDprId(rpt.id) call
            old_line = lines6[j]
            new_line = old_line.rstrip('\n') + '; setMpAttDprId(rpt ? rpt.id : null);\n' if 'setMpAttDprId' not in old_line else old_line
            if new_line != old_line:
                lines6[j] = new_line
                changes += 1
                print(f"CHANGE 6: setMpAttDprId added to openEdit at L{j+1}")
            break

content7 = "".join(lines6)
lines7 = content7.splitlines(keepends=True)

# Change 7: Add DprAttendancePanel in DPR manpower section
# Find {/* MANPOWER section */} and add panel after the closing </div>}
dr_start5 = -1
for i, l in enumerate(lines7):
    if "const DailyReports = ({" in l:
        dr_start5 = i
        break

manpower_section_end = -1
if dr_start5 != -1:
    # Find the manpower section in the form render
    in_mp = False
    mp_div_depth = 0
    for j in range(dr_start5, min(dr_start5+600, len(lines7))):
        l = lines7[j]
        if "{/* MANPOWER section */}" in l or 'activeSection==="manpower"' in l:
            in_mp = True
        if in_mp:
            mp_div_depth += l.count("{") - l.count("}")
            if mp_div_depth <= 0 and j > dr_start5 + 50:
                manpower_section_end = j
                break

if manpower_section_end != -1:
    att_panel_usage = [
        "      {/* DETAILED ATTENDANCE PANEL - Manpower Master Integration */}\n",
        "      {activeSection===\"manpower\"&&<DprAttendancePanel\n",
        "        dprId={mpAttDprId||(sel?sel.id:null)}\n",
        "        subcontractors={subcontractors}\n",
        "        masters={mpMasters}\n",
        "        loadAttendance={loadAttendance}\n",
        "        saveAttendance={saveAttendance}\n",
        "        showToast={showToast}\n",
        "      />}\n",
    ]
    lines7 = lines7[:manpower_section_end+1] + att_panel_usage + lines7[manpower_section_end+1:]
    changes += 1
    print(f"CHANGE 7: DprAttendancePanel added after manpower section at L{manpower_section_end+2}")
else:
    print("WARN 7: Manpower section end not found in DailyReports")

# Change 8: Pass subcontractors to DailyReports in App()
content8 = "".join(lines7)
# Find DailyReports case and add subcontractors prop if not present
for old, new in [
    ('return <DailyReports', 'return <DailyReports subcontractors={subs}'),
]:
    if old in content8 and new not in content8:
        content8 = content8.replace(old, new, 1)
        changes += 1
        print("CHANGE 8: subcontractors prop added to DailyReports case in App()")

# ══════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════
with open(APP, "w", encoding="utf-8") as f:
    f.write(content8)

print()
print("=" * 60)
print("TOTAL CHANGES:", changes)
print("Backup:", bk)
print()
print("NEXT:")
print("  1. Run SQL schema in Supabase (schema_manpower.sql)")
print("  2. set CI=false && npm run build")
print("  3. npx vercel --prod --force")
print("  4. git add src/App.js && git commit -m 'feat: Manpower Master + DPR Attendance' && git push")
print("=" * 60)
input("Press Enter...")
