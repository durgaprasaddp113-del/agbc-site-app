import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# ── Find insertion point: just before function useNOCs ───────────────
insert_before = "function useNOCs()"
idx = content.find(insert_before)
if idx == -1:
    print("ERROR: insertion point not found")
    input(); exit()

# ── New code to insert ───────────────────────────────────────────────
NEW_CODE = '''
// ── useManpowerMaster Hook ──────────────────────────────────────────
function useManpowerMaster() {
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

  const toggleStatus = async (id, cur) => {
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
      id: a.id, subId: a.subcontractor_id || "",
      mpId: a.manpower_id || "", empId: a.employee_id || "",
      name: a.emp_name || "", designation: a.designation || "",
      am: a.am_count === 1 ? "P" : "A", pm: a.pm_count === 1 ? "P" : "A",
      ot: String(a.ot_hours || 0), description: a.description_of_work || "",
      teamNo: a.team_no || "", remarks: a.daily_remarks || "",
    }));
  };

  const saveAttendance = async (dprId, rows) => {
    if (!dprId) return { ok: false, error: "No DPR ID" };
    await supabase.from("dpr_attendance").delete().eq("dpr_id", dprId);
    const valid = rows.filter(r => r.name && r.name.trim());
    if (!valid.length) return { ok: true };
    const { error } = await supabase.from("dpr_attendance").insert(valid.map(r => ({
      dpr_id: dprId, subcontractor_id: r.subId || null, manpower_id: r.mpId || null,
      employee_id: r.empId || "", emp_name: r.name || "", designation: r.designation || "",
      am_count: r.am === "P" ? 1 : 0, pm_count: r.pm === "P" ? 1 : 0,
      ot_hours: parseFloat(r.ot) || 0, description_of_work: r.description || "",
      team_no: r.teamNo || "", daily_remarks: r.remarks || "",
    })));
    if (error) return { ok: false, error: error.message };
    const presentCount = valid.filter(r => r.am === "P" || r.pm === "P").length;
    await supabase.from("daily_reports").update({ manpower_total: presentCount }).eq("id", dprId);
    return { ok: true };
  };

  return { masters, loading, addMaster, updateMaster, removeMaster, toggleStatus, loadAttendance, saveAttendance };
}

// ── ManpowerMaster Component ─────────────────────────────────────────
const MP_TRADES = ["Foreman","Carpenter","Mason","Plumber","Electrician","Steel Fixer","Bar Bender","Scaffolder","Helper","Driver","Equipment Operator","Painter","Welder","Tiler","Other"];
const EMPTY_MP = () => ({ subId:"", empId:"", name:"", designation:"", defaultTeamNo:"", status:"Active", dateJoined:"", dateLeft:"", remarks:"" });

const ManpowerMaster = ({ subcontractors = [], showToast }) => {
  const { masters, loading, addMaster, updateMaster, removeMaster, toggleStatus } = useManpowerMaster();
  const [mode, setMode] = useState("list");
  const [sel, setSel] = useState(null);
  const [form, setForm] = useState(EMPTY_MP());
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState("");
  const [fSub, setFSub] = useState("All");
  const [fStatus, setFStatus] = useState("Active");
  const [confirmId, setConfirmId] = useState(null);
  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));

  const filtered = masters.filter(m => {
    if (fSub !== "All" && m.subId !== fSub) return false;
    if (fStatus !== "All" && m.status !== fStatus) return false;
    if (search && !`${m.empId} ${m.name} ${m.designation}`.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const openCreate = () => { setForm(EMPTY_MP()); setSel(null); setMode("form"); };
  const openEdit = m => { setSel(m); setForm({ subId:m.subId, empId:m.empId, name:m.name, designation:m.designation, defaultTeamNo:m.defaultTeamNo, status:m.status, dateJoined:m.dateJoined, dateLeft:m.dateLeft, remarks:m.remarks }); setMode("form"); };

  const handleSave = async () => {
    if (!form.subId) { showToast("Select a subcontractor","error"); return; }
    if (!form.empId.trim()) { showToast("Employee ID required","error"); return; }
    if (!form.name.trim()) { showToast("Name required","error"); return; }
    setSaving(true);
    const res = sel ? await updateMaster(sel.id, form) : await addMaster(form);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Save failed","error"); return; }
    showToast(sel ? "Updated!" : "Employee added!"); setMode("list"); setSel(null);
  };

  const subName = id => (subcontractors.find(s => s.id === id) || {}).name || "—";

  if (mode === "form") return (
    <div className="p-4 max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-5">
        <button onClick={() => { setMode("list"); setSel(null); }} className="p-2 hover:bg-slate-100 rounded-lg text-slate-500">&#8592;</button>
        <h2 className="text-lg font-bold text-slate-800">{sel ? "Edit Employee" : "Add Employee"}</h2>
      </div>
      <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <Lbl t="Subcontractor" req/>
            <Sel value={form.subId} onChange={set("subId")}>
              <option value="">Select...</option>
              {subcontractors.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </Sel>
          </div>
          <div><Lbl t="Employee ID / Labour Card" req/><Inp value={form.empId} onChange={set("empId")} placeholder="LC-001"/></div>
          <div><Lbl t="Name" req/><Inp value={form.name} onChange={set("name")} placeholder="Full name"/></div>
          <div><Lbl t="Designation / Trade"/><Sel value={form.designation} onChange={set("designation")}><option value="">Select...</option>{MP_TRADES.map(d=><option key={d}>{d}</option>)}</Sel></div>
          <div><Lbl t="Default Team No"/><Inp value={form.defaultTeamNo} onChange={set("defaultTeamNo")} placeholder="T-1"/></div>
          <div><Lbl t="Status"/><Sel value={form.status} onChange={set("status")}><option value="Active">Active</option><option value="Inactive">Inactive</option></Sel></div>
          <div><Lbl t="Date Joined"/><Inp type="date" value={form.dateJoined} onChange={set("dateJoined")}/></div>
          <div className="sm:col-span-2"><Lbl t="Remarks"/><Txta value={form.remarks} onChange={set("remarks")} rows={2}/></div>
        </div>
        <div className="flex gap-2">
          <Btn onClick={handleSave} saving={saving} label={sel ? "Update" : "Save"}/>
          <button onClick={() => { setMode("list"); setSel(null); }} className="px-4 py-2 rounded-lg border border-slate-200 text-slate-600 text-sm">Cancel</button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-4">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Manpower Master</h2>
          <p className="text-xs text-slate-400 mt-0.5">Employee database — auto-fills DPR attendance</p>
        </div>
        <button onClick={openCreate} className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-xl text-sm font-semibold">+ Add Employee</button>
      </div>
      <div className="flex flex-wrap gap-2 mb-4">
        <Sel value={fSub} onChange={e=>setFSub(e.target.value)} className="w-auto">
          <option value="All">All Companies</option>
          {subcontractors.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
        </Sel>
        <Sel value={fStatus} onChange={e=>setFStatus(e.target.value)} className="w-auto">
          <option value="All">All</option>
          <option value="Active">Active</option>
          <option value="Inactive">Inactive</option>
        </Sel>
        <SearchBar value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search..."/>
      </div>
      {loading ? <Spinner/> : filtered.length === 0 ? <EmptyState msg="No employees found" onCreate={openCreate}/> : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto shadow-sm">
          <table className="w-full text-sm min-w-[700px]">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>{["S.No","Emp ID","Name","Designation","Team","Company","Status","Actions"].map(h=>(
                <th key={h} className="text-left px-3 py-3 text-xs font-bold text-slate-500 uppercase">{h}</th>
              ))}</tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((m,idx)=>(
                <tr key={m.id} className={`hover:bg-slate-50 ${m.status==="Inactive"?"opacity-50":""}`}>
                  <td className="px-3 py-2 text-slate-400 text-xs">{idx+1}</td>
                  <td className="px-3 py-2 font-mono text-xs text-blue-700 font-semibold">{m.empId||"—"}</td>
                  <td className="px-3 py-2 font-semibold text-slate-800">{m.name}</td>
                  <td className="px-3 py-2 text-slate-500 text-xs">{m.designation||"—"}</td>
                  <td className="px-3 py-2 text-slate-500 text-xs">{m.defaultTeamNo||"—"}</td>
                  <td className="px-3 py-2 text-xs text-slate-500 max-w-[120px] truncate">{subName(m.subId)}</td>
                  <td className="px-3 py-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${m.status==="Active"?"bg-green-100 text-green-700":"bg-red-100 text-red-700"}`}>{m.status}</span>
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex gap-1">
                      <button onClick={()=>openEdit(m)} className="px-2 py-1 text-xs rounded bg-slate-100 hover:bg-slate-200 text-slate-700">Edit</button>
                      <button onClick={()=>toggleStatus(m.id,m.status)} className={`px-2 py-1 text-xs rounded font-medium ${m.status==="Active"?"bg-amber-50 text-amber-700":"bg-green-50 text-green-700"}`}>{m.status==="Active"?"Deactivate":"Activate"}</button>
                      <button onClick={()=>setConfirmId(m.id)} className="px-2 py-1 text-xs rounded bg-red-50 text-red-600">Del</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {confirmId&&<ConfirmDialog message="Delete this employee permanently?" onConfirm={async()=>{await removeMaster(confirmId);showToast("Deleted");setConfirmId(null);}} onCancel={()=>setConfirmId(null)}/>}
    </div>
  );
};

// ── DPR Attendance Panel ─────────────────────────────────────────────
const DprAttendancePanel = ({ dprId, subcontractors=[], masters=[], loadAttendance, saveAttendance, showToast, allReports=[] }) => {
  const [rows, setRows] = useState([]);
  const [subId, setSubId] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!dprId) return;
    setLoading(true);
    loadAttendance(dprId).then(att => { if (att.length) setRows(att); setLoading(false); });
  }, [dprId]);

  const toggle = (id, field) => setRows(p => p.map(r => (r.id===id||r.rowId===id) ? {...r, [field]: r[field]==="P"?"A":"P"} : r));
  const setCell = (id, k, v) => setRows(p => p.map(r => (r.id===id||r.rowId===id) ? {...r, [k]: v} : r));
  const delRow = id => setRows(p => p.filter(r => r.id!==id && r.rowId!==id));
  const addRow = () => setRows(p => [...p, { rowId:Date.now(), mpId:"", subId:"", empId:"", name:"", designation:"", am:"P", pm:"P", ot:"", description:"", teamNo:"", remarks:"" }]);

  const loadFromMaster = () => {
    if (!subId) { showToast("Select a subcontractor","error"); return; }
    const active = masters.filter(m => m.subId===subId && m.status==="Active");
    if (!active.length) { showToast("No active employees. Add employees in Manpower Master first.","error"); return; }
    const existIds = new Set(rows.map(r=>r.mpId).filter(Boolean));
    const newRows = active.filter(m=>!existIds.has(m.id)).map(m=>({ rowId:Date.now()+Math.random(), mpId:m.id, subId:m.subId, empId:m.empId, name:m.name, designation:m.designation, teamNo:m.defaultTeamNo||"", am:"P", pm:"P", ot:"", description:"", remarks:"" }));
    if (!newRows.length) { showToast("All employees already loaded","error"); return; }
    setRows(p=>[...p,...newRows]);
    showToast(newRows.length+" employees loaded");
  };

  const copyLastDpr = async () => {
    const prev = (allReports||[]).filter(r=>r.id!==dprId).sort((a,b)=>new Date(b.date)-new Date(a.date))[0];
    if (!prev) { showToast("No previous DPR found","error"); return; }
    setLoading(true);
    const att = await loadAttendance(prev.id);
    setLoading(false);
    if (!att.length) { showToast("Previous DPR has no attendance","error"); return; }
    setRows(att.map(a=>({rowId:Date.now()+Math.random(), mpId:a.mpId||"", subId:a.subId||"", empId:a.empId||"", name:a.name||"", designation:a.designation||"", teamNo:a.teamNo||"", am:"P", pm:"P", ot:"", description:"", remarks:""})));
    showToast(att.length+" employees copied from last DPR");
  };

  const handleSave = async () => {
    if (!dprId) { showToast("Save the DPR first","error"); return; }
    setSaving(true);
    const res = await saveAttendance(dprId, rows);
    setSaving(false);
    if (!res.ok) { showToast(res.error||"Save failed","error"); return; }
    showToast("Attendance saved!");
  };

  const presentAM = rows.filter(r=>r.am==="P").length;
  const presentPM = rows.filter(r=>r.pm==="P").length;
  const subName = id => (subcontractors.find(s=>s.id===id)||{}).name||"";

  const PABtn = ({val, onClick}) => (
    <button onClick={onClick} className={`w-8 h-8 rounded-lg font-black text-sm border-2 transition-all ${val==="P"?"bg-green-100 text-green-700 border-green-400":"bg-red-100 text-red-700 border-red-400"}`}>{val}</button>
  );

  return (
    <div className="mt-3 border-2 border-slate-200 rounded-xl overflow-hidden">
      <div className="bg-slate-800 px-4 py-2 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-white font-bold text-sm">Daily Attendance Register</span>
          <span className="bg-amber-500 text-white text-xs px-2 py-0.5 rounded-full">{rows.length} workers</span>
        </div>
        <div className="flex gap-3 text-xs">
          <span className="text-green-300 font-bold">AM: {presentAM}</span>
          <span className="text-blue-300 font-bold">PM: {presentPM}</span>
          <span className="text-red-300 font-bold">Absent: {rows.filter(r=>r.am==="A"&&r.pm==="A").length}</span>
        </div>
      </div>
      <div className="bg-slate-50 px-3 py-2 flex flex-wrap gap-2 items-end border-b border-slate-200">
        <div className="flex-1 min-w-[160px]">
          <label className="block text-xs font-semibold text-slate-600 mb-1">Load from Manpower Master</label>
          <Sel value={subId} onChange={e=>setSubId(e.target.value)} className="w-full text-xs">
            <option value="">Select Subcontractor...</option>
            {subcontractors.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
          </Sel>
        </div>
        <button onClick={loadFromMaster} className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold">&#8635; Load Employees</button>
        <button onClick={copyLastDpr} disabled={loading} className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-semibold">Copy Last DPR</button>
        <button onClick={addRow} className="px-3 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg text-xs font-semibold">+ Add Row</button>
        {rows.length>0&&<button onClick={handleSave} disabled={saving} className="px-3 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-xs font-semibold">{saving?"Saving...":"Save Attendance"}</button>}
      </div>
      {loading?<div className="p-4 text-center text-sm text-slate-400">Loading...</div>:rows.length===0?(
        <div className="p-6 text-center"><p className="text-sm text-slate-400">No attendance yet. Load from Master or add rows manually.</p></div>
      ):(
        <div className="overflow-x-auto">
          <table className="w-full text-xs min-w-[750px]">
            <thead><tr className="bg-slate-700 text-white">{["S.No","ID No","Name","Designation","Team","A.M","P.M","O.T","Description of Work",""].map(h=>(<th key={h} className="px-2 py-2 text-left font-bold uppercase">{h}</th>))}</tr></thead>
            <tbody>
              {rows.map((r,idx)=>{
                const rid = r.rowId||r.id;
                return (
                  <tr key={rid} className={`border-b border-slate-100 ${r.am==="A"&&r.pm==="A"?"bg-red-50":"hover:bg-amber-50/30"}`}>
                    <td className="px-2 py-1.5 text-slate-400 text-center">{idx+1}</td>
                    <td className="px-2 py-1.5">{r.mpId?<span className="font-mono font-bold text-blue-700">{r.empId||"—"}</span>:<Inp value={r.empId} onChange={e=>setCell(rid,"empId",e.target.value)} placeholder="ID" className="w-14"/>}</td>
                    <td className="px-2 py-1.5">{r.mpId?<span className="font-semibold text-slate-800">{r.name}</span>:<Inp value={r.name} onChange={e=>setCell(rid,"name",e.target.value)} placeholder="Name"/>}</td>
                    <td className="px-2 py-1.5">{r.mpId?<span className="text-slate-500">{r.designation||"—"}</span>:<Inp value={r.designation} onChange={e=>setCell(rid,"designation",e.target.value)} placeholder="Trade"/>}</td>
                    <td className="px-2 py-1.5"><Inp value={r.teamNo||""} onChange={e=>setCell(rid,"teamNo",e.target.value)} placeholder="T-1" className="w-14 text-center font-semibold text-purple-700"/></td>
                    <td className="px-2 py-1.5 text-center"><PABtn val={r.am||"P"} onClick={()=>toggle(rid,"am")}/></td>
                    <td className="px-2 py-1.5 text-center"><PABtn val={r.pm||"P"} onClick={()=>toggle(rid,"pm")}/></td>
                    <td className="px-2 py-1.5"><Inp value={r.ot||""} onChange={e=>setCell(rid,"ot",e.target.value)} placeholder="0" className="w-12 text-center text-amber-700"/></td>
                    <td className="px-2 py-1.5"><Inp value={r.description||""} onChange={e=>setCell(rid,"description",e.target.value)} placeholder="Description..."/></td>
                    <td className="px-2 py-1.5 text-center"><button onClick={()=>delRow(rid)} className="w-6 h-6 rounded-full bg-red-100 hover:bg-red-200 text-red-600 font-bold text-xs">&#215;</button></td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot><tr className="bg-slate-700 text-white">
              <td colSpan={5} className="px-3 py-1.5 font-bold text-xs">TOTAL PRESENT</td>
              <td className="px-2 py-1.5 text-center font-black text-green-300">{presentAM}</td>
              <td className="px-2 py-1.5 text-center font-black text-blue-300">{presentPM}</td>
              <td colSpan={3} className="px-3 py-1.5 text-xs text-slate-300">OT: {rows.reduce((s,r)=>s+(parseFloat(r.ot)||0),0).toFixed(1)} hrs</td>
            </tr></tfoot>
          </table>
          {!dprId&&<div className="p-2 text-center text-xs text-amber-600 bg-amber-50">Save the DPR first, then Save Attendance</div>}
        </div>
      )}
    </div>
  );
};
// ── End DPR Attendance Panel ─────────────────────────────────────────

'''

content = content[:idx] + NEW_CODE + content[idx:]
changes += 1
print("STEP 1: Hook + ManpowerMaster + DprAttendancePanel inserted")

# ── Add ManpowerMaster to App() ──────────────────────────────────────
# Find useNOCs in App() and add useManpowerMaster
app_marker = 'const { nocs, loading: nocLoad, add: addNoc, update: updNoc, remove: delNoc } = useNOCs();'
if app_marker in content:
    content = content.replace(
        app_marker,
        app_marker + '\n  const { masters: mpMasters, loadAttendance, saveAttendance } = useManpowerMaster();'
    )
    changes += 1
    print("STEP 2: useManpowerMaster added to App()")

# ── Add manpower-master case to renderPage ───────────────────────────
case_marker = 'case "manpower-master":'
if case_marker not in content:
    noc_case = 'case "noc":'
    noc_idx = content.rfind(noc_case)
    if noc_idx != -1:
        # Find end of noc case
        end_noc = content.find('\n', content.find(';', noc_idx)) + 1
        content = content[:end_noc] + '        case "manpower-master": return <ManpowerMaster subcontractors={subs} showToast={showToast}/>;\n' + content[end_noc:]
        changes += 1
        print("STEP 3: manpower-master case added to renderPage")

# ── Add Manpower Master to sidebar ───────────────────────────────────
sidebar_marker = '"manpower-master"'
if sidebar_marker not in content:
    # Find NOC in sidebar
    noc_sidebar = '"noc"'
    # Find the sidebar nav items array
    for old_nav, new_nav in [
        ('{ id: "noc"', '{ id: "manpower-master", label: "Manpower Master", icon: "users" },\n          { id: "noc"'),
        ('{ id:"noc"', '{ id:"manpower-master", label:"Manpower Master", icon:"users" },\n          { id:"noc"'),
    ]:
        if old_nav in content:
            content = content.replace(old_nav, new_nav, 1)
            changes += 1
            print("STEP 4: Manpower Master added to sidebar")
            break

# ── Add DprAttendancePanel to DailyReports manpower section ─────────
# Find the manpower section in DailyReports form
mp_section = '{activeSection==="manpower"&&<div'
if mp_section in content and 'DprAttendancePanel' not in content:
    content = content.replace(
        mp_section,
        '{activeSection==="manpower"&&<DprAttendancePanel dprId={sel?sel.id:null} subcontractors={subcontractors||[]} masters={mpMasters||[]} loadAttendance={loadAttendance} saveAttendance={saveAttendance} showToast={showToast} allReports={reports}/> }{activeSection==="manpower"&&<div'
    )
    changes += 1
    print("STEP 5: DprAttendancePanel added to DPR manpower section")

# ── Pass subcontractors to DailyReports ─────────────────────────────
dr_case = 'case "reports":'
if dr_case in content:
    # Find the DailyReports component usage
    dr_usage = content[content.rfind(dr_case):]
    if 'subcontractors={subs}' not in dr_usage[:200]:
        content = content[:content.rfind(dr_case)] + content[content.rfind(dr_case):].replace(
            'return <DailyReports',
            'return <DailyReports subcontractors={subs}',
            1
        )
        changes += 1
        print("STEP 6: subcontractors passed to DailyReports")

# ── Pass mpMasters and loadAttendance to DailyReports ────────────────
if 'mpMasters={mpMasters}' not in content:
    content = content.replace(
        'return <DailyReports subcontractors={subs}',
        'return <DailyReports subcontractors={subs} mpMasters={mpMasters} loadAttendance={loadAttendance} saveAttendance={saveAttendance}'
    )
    changes += 1
    print("STEP 7: mpMasters/loadAttendance passed to DailyReports")

# ── Accept new props in DailyReports ────────────────────────────────
dr_comp = 'const DailyReports = ({ projects, reports, loading, onAdd, onUpdate, onDelete, showToast, navFilter = {} })'
if dr_comp in content:
    content = content.replace(
        dr_comp,
        'const DailyReports = ({ projects, reports, loading, onAdd, onUpdate, onDelete, showToast, navFilter = {}, subcontractors = [], mpMasters = [], loadAttendance, saveAttendance })'
    )
    changes += 1
    print("STEP 8: DailyReports accepts new props")

# WRITE
with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print("\nSaved OK")
print("TOTAL CHANGES:", changes)
print("\nRUN:")
print("  set CI=false && npm run build")
print("  git add src/App.js")
print("  git commit -m 'feat: Manpower Master + DPR Attendance'")
print("  git push")
input("\nPress Enter...")
