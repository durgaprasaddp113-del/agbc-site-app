// ============================================================
// MANPOWER MASTER — Hook + Component
// Insert into App.js BEFORE the DailyReports component
// ============================================================

// ── useManpowerMaster Hook ────────────────────────────────────────────────────
function useManpowerMaster() {
  const [masters, setMasters] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const { data } = await supabase
      .from("manpower_master")
      .select("*")
      .order("employee_name");
    if (data) setMasters(data.map(m => ({
      id:          m.id,
      subId:       m.subcontractor_id  || "",
      pid:         m.project_id        || "",
      empId:       m.employee_id       || "",
      name:        m.employee_name     || "",
      designation: m.designation       || "",
      trade:       m.trade             || "",
      teamNo:      m.default_team_no   || "",
      status:      m.status            || "Active",
      dateJoined:  m.date_joined       || "",
      dateLeft:    m.date_left         || "",
      remarks:     m.remarks           || "",
    })));
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const addMaster = async (f) => {
    const { error } = await supabase.from("manpower_master").insert([{
      subcontractor_id: f.subId  || null,
      project_id:       f.pid    || null,
      employee_id:      f.empId,
      employee_name:    f.name,
      designation:      f.designation,
      trade:            f.trade,
      default_team_no:  f.teamNo,
      status:           f.status || "Active",
      date_joined:      f.dateJoined || null,
      date_left:        f.dateLeft   || null,
      remarks:          f.remarks,
    }]);
    if (error) return { ok: false, error: error.message };
    await load(); return { ok: true };
  };

  const updateMaster = async (id, f) => {
    const { error } = await supabase.from("manpower_master").update({
      subcontractor_id: f.subId  || null,
      project_id:       f.pid    || null,
      employee_id:      f.empId,
      employee_name:    f.name,
      designation:      f.designation,
      trade:            f.trade,
      default_team_no:  f.teamNo,
      status:           f.status || "Active",
      date_joined:      f.dateJoined || null,
      date_left:        f.dateLeft   || null,
      remarks:          f.remarks,
      updated_at:       new Date().toISOString(),
    }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await load(); return { ok: true };
  };

  const removeMaster = async (id) => {
    const { error } = await supabase.from("manpower_master").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await load(); return { ok: true };
  };

  const getActiveBySubcontractor = (subId) =>
    masters.filter(m => m.subId === subId && m.status === "Active");

  return { masters, loading, addMaster, updateMaster, removeMaster, getActiveBySubcontractor, reload: load };
}

// ── ManpowerMaster Component ──────────────────────────────────────────────────
const ManpowerMaster = ({ subcontractors, projects, showToast }) => {
  const { masters, loading, addMaster, updateMaster, removeMaster } = useManpowerMaster();
  const [mode,      setMode]      = useState("list");
  const [sel,       setSel]       = useState(null);
  const [saving,    setSaving]    = useState(false);
  const [search,    setSearch]    = useState("");
  const [fSub,      setFSub]      = useState("All");
  const [fStatus,   setFStatus]   = useState("Active");
  const [confirmId, setConfirmId] = useState(null);
  const [form,      setForm]      = useState(EMPTY_MP_FORM());

  function EMPTY_MP_FORM() {
    return { subId:"", pid:"", empId:"", name:"", designation:"", trade:"",
             teamNo:"", status:"Active", dateJoined:"", dateLeft:"", remarks:"" };
  }

  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));

  const filtered = masters.filter(m => {
    if (fSub    !== "All" && m.subId  !== fSub)    return false;
    if (fStatus !== "All" && m.status !== fStatus)  return false;
    if (search  && !`${m.empId} ${m.name} ${m.designation} ${m.trade}`
        .toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const goList = () => { setMode("list"); setSel(null); setForm(EMPTY_MP_FORM()); };

  const handleSave = async () => {
    if (!form.name.trim()) { showToast("Employee name required", "error"); return; }
    if (!form.subId)       { showToast("Select subcontractor", "error"); return; }
    setSaving(true);
    const res = sel ? await updateMaster(sel.id, form) : await addMaster(form);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Failed", "error"); return; }
    showToast(sel ? "Employee updated!" : "Employee added to master!"); goList();
  };

  const handleDelete = async (id) => {
    const res = await removeMaster(id);
    if (!res.ok) { showToast(res.error, "error"); return; }
    showToast("Deleted!"); setConfirmId(null);
  };

  const TRADES = ["Mason","Carpenter","Steel Fixer","Plasterer","Painter","Tiler",
    "Electrician","Plumber","AC Technician","Helper","Supervisor","Foreman",
    "Safety Officer","Surveyor","Driver","Cleaner","Other"];
  const STATUS_OPTS = ["Active","Inactive","On Leave","Resigned"];

  // ── Form ───────────────────────────────────────────────────────────────────
  if (mode === "form") return (
    <div className="p-6 max-w-2xl">
      <BackBtn onClick={goList}/>
      <h2 className="text-xl font-bold text-slate-800 mb-4">
        {sel ? "Edit Employee" : "Add Employee to Master"}
      </h2>
      <FormCard>
        <Grid2>
          <div>
            <Lbl t="Subcontractor" req/>
            <Sel value={form.subId} onChange={set("subId")}>
              <option value="">Select subcontractor...</option>
              {subcontractors.map(s => <option key={s.id} value={s.id}>{s.companyName}</option>)}
            </Sel>
          </div>
          <div>
            <Lbl t="Project"/>
            <Sel value={form.pid} onChange={set("pid")}>
              <option value="">All Projects</option>
              {projects.map(p => <option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}
            </Sel>
          </div>
          <div><Lbl t="Employee ID / Labour Card No"/><Inp value={form.empId} onChange={set("empId")} placeholder="LC-001"/></div>
          <div><Lbl t="Employee Name" req/><Inp value={form.name} onChange={set("name")} placeholder="Full name"/></div>
          <div>
            <Lbl t="Designation / Trade"/>
            <Sel value={form.trade} onChange={e => { set("trade")(e); set("designation")(e); }}>
              <option value="">Select trade...</option>
              {TRADES.map(t => <option key={t}>{t}</option>)}
            </Sel>
          </div>
          <div><Lbl t="Custom Designation"/><Inp value={form.designation} onChange={set("designation")} placeholder="e.g. Senior Mason"/></div>
          <div><Lbl t="Default Team No"/><Inp value={form.teamNo} onChange={set("teamNo")} placeholder="T-01"/></div>
          <div>
            <Lbl t="Status"/>
            <Sel value={form.status} onChange={set("status")}>
              {STATUS_OPTS.map(s => <option key={s}>{s}</option>)}
            </Sel>
          </div>
          <div><Lbl t="Date Joined"/><Inp type="date" value={form.dateJoined} onChange={set("dateJoined")}/></div>
          <div><Lbl t="Date Left (if resigned)"/><Inp type="date" value={form.dateLeft} onChange={set("dateLeft")}/></div>
        </Grid2>
        <div><Lbl t="Remarks"/><Txta value={form.remarks} onChange={set("remarks")} rows={2}/></div>
        <div className="flex gap-3 pt-2">
          <Btn saving={saving} onClick={handleSave} label={sel ? "Update" : "Add Employee"}/>
          <Btn onClick={goList} label="Cancel" color="slate"/>
        </div>
      </FormCard>
    </div>
  );

  // ── List ───────────────────────────────────────────────────────────────────
  const activeCount   = masters.filter(m => m.status === "Active").length;
  const inactiveCount = masters.filter(m => m.status !== "Active").length;

  return (
    <div className="p-6">
      {confirmId && <ConfirmDialog
        message="Permanently delete this employee from master?"
        onConfirm={() => handleDelete(confirmId)}
        onCancel={() => setConfirmId(null)}/>}

      {/* KPI */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        {[
          { l:"Total Employees", v: masters.length,     c:"bg-blue-500"  },
          { l:"Active",          v: activeCount,         c:"bg-green-500" },
          { l:"Inactive",        v: inactiveCount,       c:"bg-slate-500" },
          { l:"Subcontractors",  v: [...new Set(masters.map(m=>m.subId))].filter(Boolean).length, c:"bg-amber-500" },
        ].map(k => (
          <div key={k.l} className={`${k.c} rounded-xl p-3 text-white`}>
            <div className="text-2xl font-bold">{k.v}</div>
            <div className="text-xs opacity-80 mt-0.5">{k.l}</div>
          </div>
        ))}
      </div>

      {/* Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
        <div className="flex flex-wrap gap-2">
          <SearchBar value={search} onChange={e=>setSearch(e.target.value)} placeholder="ID, name, trade..."/>
          <Sel value={fSub} onChange={e=>setFSub(e.target.value)} className="w-auto">
            <option value="All">All Subcontractors</option>
            {subcontractors.map(s=><option key={s.id} value={s.id}>{s.companyName}</option>)}
          </Sel>
          <Sel value={fStatus} onChange={e=>setFStatus(e.target.value)} className="w-auto">
            <option value="All">All Status</option>
            {STATUS_OPTS.map(s=><option key={s}>{s}</option>)}
          </Sel>
        </div>
        <AddBtn onClick={()=>{setForm(EMPTY_MP_FORM());setSel(null);setMode("form");}} label="Add Employee"/>
      </div>

      {loading ? <Spinner/> : filtered.length === 0 ? (
        <EmptyState msg="No employees found" onCreate={()=>{setForm(EMPTY_MP_FORM());setSel(null);setMode("form");}}/>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto shadow-sm">
          <table className="w-full text-sm min-w-[900px]">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>{["S.No","Emp ID","Name","Trade / Designation","Subcontractor","Team","Joined","Status","Actions"].map(h=>(
                <th key={h} className="text-left px-3 py-3 text-xs font-bold text-slate-500 uppercase whitespace-nowrap">{h}</th>
              ))}</tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((m, idx) => {
                const sub  = subcontractors.find(s => s.id === m.subId);
                const sBadge = m.status === "Active"
                  ? "bg-green-100 text-green-700 border-green-200"
                  : m.status === "On Leave"
                    ? "bg-amber-100 text-amber-700 border-amber-200"
                    : "bg-slate-100 text-slate-600 border-slate-200";
                return (
                  <tr key={m.id} className={`hover:bg-slate-50 ${m.status !== "Active" ? "opacity-60" : ""}`}>
                    <td className="px-3 py-2.5 text-xs text-slate-400">{idx+1}</td>
                    <td className="px-3 py-2.5 font-mono text-xs text-slate-700">{m.empId||"—"}</td>
                    <td className="px-3 py-2.5 font-semibold text-slate-800">{m.name}</td>
                    <td className="px-3 py-2.5 text-xs text-slate-600">{m.designation||m.trade||"—"}</td>
                    <td className="px-3 py-2.5 text-xs text-slate-700">{sub?.companyName||"—"}</td>
                    <td className="px-3 py-2.5 text-xs text-center">{m.teamNo||"—"}</td>
                    <td className="px-3 py-2.5 text-xs text-slate-500 whitespace-nowrap">{m.dateJoined ? fmtDate(m.dateJoined) : "—"}</td>
                    <td className="px-3 py-2.5">
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${sBadge}`}>{m.status}</span>
                    </td>
                    <td className="px-3 py-2.5">
                      <div className="flex gap-1">
                        <ActBtn onClick={()=>{setSel(m);setForm({...m});setMode("form");}} label="Edit" color="edit"/>
                        {m.status === "Active"
                          ? <ActBtn onClick={async()=>{await updateMaster(m.id,{...m,status:"Inactive"});showToast("Marked inactive");}} label="Deactivate" color="slate"/>
                          : <ActBtn onClick={async()=>{await updateMaster(m.id,{...m,status:"Active"});showToast("Reactivated!");}} label="Activate" color="edit"/>
                        }
                        <ActBtn onClick={()=>setConfirmId(m.id)} label="Del" color="del"/>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};


// ── DPR Manpower Section — Drop-in replacement for manpower rows in DPR form ──
// Use this inside your DPR form where subcontractor manpower is entered

const DPRManpowerSection = ({ subcontractorId, subcontractorName, dprId, reportDate, projectId, showToast }) => {
  const [rows,    setRows]    = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving,  setSaving]  = useState(false);
  const [saved,   setSaved]   = useState(false);

  const AM_OPTS = ["P","A","H"];
  const PM_OPTS = ["P","A","H"];

  // Load active manpower for this subcontractor
  useEffect(() => {
    if (!subcontractorId) { setRows([]); return; }
    const load = async () => {
      setLoading(true);

      // Check if attendance already saved for this DPR+subcontractor
      if (dprId) {
        const { data: existing } = await supabase
          .from("dpr_attendance")
          .select("*, manpower_master(*)")
          .eq("dpr_id", dprId)
          .eq("subcontractor_id", subcontractorId);

        if (existing && existing.length > 0) {
          setRows(existing.map(a => ({
            attId:       a.id,
            masterId:    a.manpower_master_id,
            empId:       a.manpower_master?.employee_id       || "",
            name:        a.manpower_master?.employee_name     || "",
            designation: a.manpower_master?.designation       || "",
            teamNo:      a.team_no || a.manpower_master?.default_team_no || "",
            am:          a.am_status    || "P",
            pm:          a.pm_status    || "P",
            ot:          a.ot_hours     || 0,
            work:        a.description_of_work || "",
            remarks:     a.daily_remarks || "",
            saved:       true,
          })));
          setSaved(true);
          setLoading(false);
          return;
        }
      }

      // Load fresh from master
      const { data: mpData } = await supabase
        .from("manpower_master")
        .select("*")
        .eq("subcontractor_id", subcontractorId)
        .eq("status", "Active")
        .order("employee_name");

      if (mpData) {
        setRows(mpData.map(m => ({
          attId:       null,
          masterId:    m.id,
          empId:       m.employee_id   || "",
          name:        m.employee_name || "",
          designation: m.designation   || m.trade || "",
          teamNo:      m.default_team_no || "",
          am:    "P",
          pm:    "P",
          ot:    0,
          work:  "",
          remarks: "",
          saved: false,
        })));
      }
      setLoading(false);
    };
    load();
  }, [subcontractorId, dprId]);

  const setRow = (idx, k, v) => setRows(p => p.map((r,i) => i===idx ? {...r,[k]:v} : r));

  const presentAM = rows.filter(r => r.am === "P").length;
  const presentPM = rows.filter(r => r.pm === "P").length;

  const handleSave = async () => {
    if (!dprId) { showToast("Save DPR first before saving attendance","error"); return; }
    setSaving(true);
    let errors = 0;
    for (const row of rows) {
      if (!row.masterId) continue;
      const payload = {
        dpr_id:              dprId,
        subcontractor_id:    subcontractorId,
        manpower_master_id:  row.masterId,
        project_id:          projectId || null,
        report_date:         reportDate || null,
        am_status:           row.am,
        pm_status:           row.pm,
        ot_hours:            Number(row.ot) || 0,
        description_of_work: row.work,
        team_no:             row.teamNo,
        daily_remarks:       row.remarks,
      };
      if (row.attId) {
        const { error } = await supabase.from("dpr_attendance").update(payload).eq("id", row.attId);
        if (error) errors++;
      } else {
        const { data, error } = await supabase.from("dpr_attendance").insert([payload]).select().single();
        if (error) errors++;
        else {
          setRows(p => p.map(r => r.masterId===row.masterId ? {...r, attId:data.id, saved:true} : r));
        }
      }
    }
    setSaving(false);
    if (errors > 0) showToast(`${errors} rows failed to save`, "error");
    else { showToast("✅ Attendance saved!"); setSaved(true); }
  };

  if (loading) return <div className="text-xs text-slate-400 py-4 text-center">Loading manpower...</div>;
  if (rows.length === 0) return (
    <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-800 text-center">
      No active employees in master for this subcontractor.
      <span className="block mt-1 font-semibold">Go to Manpower Master → Add employees first.</span>
    </div>
  );

  return (
    <div className="mt-3">
      {/* Summary bar */}
      <div className="flex flex-wrap gap-3 mb-2">
        <span className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full font-semibold border border-green-200">
          AM Present: {presentAM} / {rows.length}
        </span>
        <span className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-semibold border border-blue-200">
          PM Present: {presentPM} / {rows.length}
        </span>
        <span className="text-xs bg-amber-100 text-amber-700 px-3 py-1 rounded-full font-semibold border border-amber-200">
          Total: {rows.length} Workers
        </span>
        {saved && <span className="text-xs bg-slate-100 text-slate-500 px-3 py-1 rounded-full font-semibold border border-slate-200">✅ Saved</span>}
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-200">
        <table className="w-full text-xs min-w-[800px]">
          <thead className="bg-slate-700 text-white">
            <tr>{["S.No","Emp ID","Name","Designation","A.M","P.M","O.T Hrs","Description of Work","Team No","Remarks"].map(h => (
              <th key={h} className="px-2 py-2 text-left font-semibold whitespace-nowrap">{h}</th>
            ))}</tr>
          </thead>
          <tbody>
            {rows.map((r, idx) => (
              <tr key={idx} className={`border-t border-slate-100 ${idx%2===0?"bg-white":"bg-slate-50/50"}`}>
                <td className="px-2 py-1.5 text-slate-400 text-center">{idx+1}</td>
                <td className="px-2 py-1.5 font-mono text-slate-600">{r.empId||"—"}</td>
                <td className="px-2 py-1.5 font-semibold text-slate-800 whitespace-nowrap">{r.name}</td>
                <td className="px-2 py-1.5 text-slate-600">{r.designation||"—"}</td>
                <td className="px-1 py-1 w-16">
                  <select value={r.am} onChange={e=>setRow(idx,"am",e.target.value)}
                    className={`w-full text-xs px-1 py-1 rounded border font-bold text-center
                      ${r.am==="P"?"bg-green-100 text-green-700 border-green-300"
                        :r.am==="A"?"bg-red-100 text-red-700 border-red-300"
                        :"bg-amber-100 text-amber-700 border-amber-300"}`}>
                    {AM_OPTS.map(o=><option key={o}>{o}</option>)}
                  </select>
                </td>
                <td className="px-1 py-1 w-16">
                  <select value={r.pm} onChange={e=>setRow(idx,"pm",e.target.value)}
                    className={`w-full text-xs px-1 py-1 rounded border font-bold text-center
                      ${r.pm==="P"?"bg-green-100 text-green-700 border-green-300"
                        :r.pm==="A"?"bg-red-100 text-red-700 border-red-300"
                        :"bg-amber-100 text-amber-700 border-amber-300"}`}>
                    {PM_OPTS.map(o=><option key={o}>{o}</option>)}
                  </select>
                </td>
                <td className="px-1 py-1 w-14">
                  <input type="number" value={r.ot||""} min="0" max="12" step="0.5"
                    onChange={e=>setRow(idx,"ot",e.target.value)}
                    className="w-full text-xs px-1.5 py-1 rounded border border-slate-200 text-center focus:outline-none focus:ring-1 focus:ring-amber-400"/>
                </td>
                <td className="px-1 py-1 min-w-[140px]">
                  <input value={r.work||""} onChange={e=>setRow(idx,"work",e.target.value)}
                    placeholder="Work done..."
                    className="w-full text-xs px-1.5 py-1 rounded border border-slate-200 focus:outline-none focus:ring-1 focus:ring-amber-400"/>
                </td>
                <td className="px-1 py-1 w-16">
                  <input value={r.teamNo||""} onChange={e=>setRow(idx,"teamNo",e.target.value)}
                    placeholder="T-01"
                    className="w-full text-xs px-1.5 py-1 rounded border border-slate-200 text-center focus:outline-none focus:ring-1 focus:ring-amber-400"/>
                </td>
                <td className="px-1 py-1 min-w-[100px]">
                  <input value={r.remarks||""} onChange={e=>setRow(idx,"remarks",e.target.value)}
                    placeholder="Notes..."
                    className="w-full text-xs px-1.5 py-1 rounded border border-slate-200 focus:outline-none focus:ring-1 focus:ring-amber-400"/>
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-slate-50 border-t-2 border-slate-300">
            <tr>
              <td colSpan={4} className="px-3 py-2 text-xs font-bold text-slate-700">
                TOTAL — {subcontractorName}
              </td>
              <td className="px-2 py-2 text-center">
                <span className="text-xs font-bold text-green-700 bg-green-100 px-2 py-0.5 rounded-full">{presentAM}P</span>
              </td>
              <td className="px-2 py-2 text-center">
                <span className="text-xs font-bold text-blue-700 bg-blue-100 px-2 py-0.5 rounded-full">{presentPM}P</span>
              </td>
              <td className="px-2 py-2 text-center text-xs font-bold text-amber-700">
                {rows.reduce((s,r)=>s+(Number(r.ot)||0),0)}h
              </td>
              <td colSpan={3}/>
            </tr>
          </tfoot>
        </table>
      </div>

      <div className="flex justify-end mt-3">
        <button onClick={handleSave} disabled={saving}
          className="text-sm bg-green-600 hover:bg-green-700 text-white font-semibold px-4 py-2 rounded-lg disabled:opacity-50 flex items-center gap-2">
          {saving ? "Saving..." : "💾 Save Attendance"}
        </button>
      </div>
    </div>
  );
};
