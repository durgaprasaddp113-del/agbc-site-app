import { useState, useEffect, useCallback } from "react";
import { supabase } from "./supabase";
import Login from "./Login";

// ─────────────────────────────────────────────────────────────────────────────
// TOAST
// ─────────────────────────────────────────────────────────────────────────────
const Toast = ({ message, type, onClose }) => {
  useEffect(() => { const t = setTimeout(onClose, 3500); return () => clearTimeout(t); }, [onClose]);
  const bg = { success: "bg-green-600", error: "bg-red-600", info: "bg-blue-600" };
  return (
    <div className={`fixed top-5 right-5 z-[999] ${bg[type] || "bg-slate-800"} text-white px-5 py-3.5 rounded-xl shadow-2xl flex items-center gap-3 text-sm font-semibold max-w-sm`}>
      <span className="flex-1">{message}</span>
      <button onClick={onClose} className="text-white/70 hover:text-white text-xl leading-none ml-2">×</button>
    </div>
  );
};
function useToast() {
  const [toast, setToast] = useState(null);
  const showToast = useCallback((message, type = "success") => setToast({ message, type }), []);
  const hideToast = useCallback(() => setToast(null), []);
  return { toast, showToast, hideToast };
}

// ─────────────────────────────────────────────────────────────────────────────
// CONFIRM DIALOG
// ─────────────────────────────────────────────────────────────────────────────
const ConfirmDialog = ({ message, onConfirm, onCancel }) => (
  <div className="fixed inset-0 bg-black/50 z-[998] flex items-center justify-center p-4">
    <div className="bg-white rounded-2xl shadow-2xl p-6 max-w-sm w-full">
      <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
      </div>
      <p className="text-slate-700 text-sm text-center mb-6">{message}</p>
      <div className="flex gap-3">
        <button onClick={onConfirm} className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold text-sm py-2.5 rounded-lg transition-colors">Yes, Delete</button>
        <button onClick={onCancel} className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm py-2.5 rounded-lg transition-colors">Cancel</button>
      </div>
    </div>
  </div>
);

// ─────────────────────────────────────────────────────────────────────────────
// AUTH HOOK
// ─────────────────────────────────────────────────────────────────────────────
function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => { setUser(session?.user ?? null); setLoading(false); });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_, session) => setUser(session?.user ?? null));
    return () => subscription.unsubscribe();
  }, []);
  return { user, loading };
}

// ─────────────────────────────────────────────────────────────────────────────
// PROJECTS HOOK
// ─────────────────────────────────────────────────────────────────────────────
function useProjects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const loadData = useCallback(async () => {
    const { data, error } = await supabase.from("projects").select("*").order("project_number");
    if (error) { console.error("Projects:", error.message); }
    if (data) setProjects(data.map(p => ({
      id: p.id, number: p.project_number || "", name: p.project_name || "",
      plot: p.plot_number || "", location: p.location || "",
      plotArea: p.plot_area_sqft || "", bua: p.bua_sqft || "",
      duration: p.duration_months || "", consultant: p.consultant_name || "",
      consultantContact: p.consultant_contact || "",
      status: p.status || "Active", mapUrl: p.map_url || "",
    })));
    setLoading(false);
  }, []);
  useEffect(() => { loadData(); }, [loadData]);

  const add = async (f) => {
    const { error } = await supabase.from("projects").insert([{
      project_number: f.number, project_name: f.name, plot_number: f.plot,
      location: f.location, plot_area_sqft: parseFloat(f.plotArea) || null,
      bua_sqft: parseFloat(f.bua) || null, duration_months: parseInt(f.duration) || null,
      consultant_name: f.consultant, consultant_contact: f.consultantContact,
      status: f.status || "Active", map_url: f.mapUrl || null,
    }]);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const update = async (id, f) => {
    const { error } = await supabase.from("projects").update({
      project_number: f.number, project_name: f.name, plot_number: f.plot,
      location: f.location, plot_area_sqft: parseFloat(f.plotArea) || null,
      bua_sqft: parseFloat(f.bua) || null, duration_months: parseInt(f.duration) || null,
      consultant_name: f.consultant, consultant_contact: f.consultantContact,
      status: f.status, map_url: f.mapUrl || null,
    }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const remove = async (id) => {
    const { error } = await supabase.from("projects").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  return { projects, loading, add, update, remove, reload: loadData };
}

// ─────────────────────────────────────────────────────────────────────────────
// TASKS HOOK
// ─────────────────────────────────────────────────────────────────────────────
function useTasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const loadData = useCallback(async () => {
    const { data, error } = await supabase.from("tasks").select("*").order("created_at", { ascending: false });
    if (error) console.error("Tasks:", error.message);
    if (data) setTasks(data.map(t => ({
      id: t.id, pid: t.project_id, title: t.title || "", desc: t.description || "",
      location: t.location || "", trade: t.trade || "", assignee: t.assignee_name || "",
      priority: t.priority || "Medium", status: t.status || "Open", due: t.due_date || "",
    })));
    setLoading(false);
  }, []);
  useEffect(() => { loadData(); }, [loadData]);

  const add = async (f) => {
    const { error } = await supabase.from("tasks").insert([{
      project_id: f.pid, title: f.title, description: f.desc,
      location: f.location, trade: f.trade, assignee_name: f.assignee,
      priority: f.priority, status: "Open", due_date: f.due || null,
    }]);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const update = async (id, f) => {
    const { error } = await supabase.from("tasks").update({
      project_id: f.pid, title: f.title, description: f.desc,
      location: f.location, trade: f.trade, assignee_name: f.assignee,
      priority: f.priority, status: f.status, due_date: f.due || null,
    }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const remove = async (id) => {
    const { error } = await supabase.from("tasks").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  return { tasks, loading, add, update, remove };
}

// ─────────────────────────────────────────────────────────────────────────────
// SNAGS HOOK
// ─────────────────────────────────────────────────────────────────────────────
function useSnags() {
  const [snags, setSnags] = useState([]);
  const [loading, setLoading] = useState(true);
  const loadData = useCallback(async () => {
    const { data, error } = await supabase.from("snag_items").select("*").order("created_at", { ascending: false });
    if (error) console.error("Snags:", error.message);
    if (data) setSnags(data.map(s => ({
      id: s.id, pid: s.project_id, num: s.snag_number || "",
      title: s.title || "", desc: s.description || "",
      location: s.location || "", category: s.category || "",
      sub: s.responsible_sub_name || "", engineer: s.assigned_engineer_name || "",
      due: s.due_date || "", status: s.status || "Open",
      beforeUrl: s.before_photo_url || "", afterUrl: s.after_photo_url || "",
      consultant: s.consultant_comment || "", remarks: s.remarks || "",
    })));
    setLoading(false);
  }, []);
  useEffect(() => { loadData(); }, [loadData]);

  const uploadPhoto = async (file, folder) => {
    const ext = file.name.split(".").pop();
    const fileName = `${folder}/${Date.now()}_${Math.random().toString(36).slice(2)}.${ext}`;
    const { error } = await supabase.storage.from("site-photos").upload(fileName, file);
    if (error) { console.error("Photo upload:", error.message); return null; }
    const { data: { publicUrl } } = supabase.storage.from("site-photos").getPublicUrl(fileName);
    return publicUrl;
  };

  const getNextNum = async () => {
    const { data } = await supabase.from("snag_items").select("snag_number").order("created_at", { ascending: false }).limit(1);
    const last = data?.[0]?.snag_number || "SNF-000";
    const num = parseInt(last.replace("SNF-", "")) || 0;
    return `SNF-${String(num + 1).padStart(3, "0")}`;
  };

  const add = async (f) => {
    const num = await getNextNum();
    let beforeUrl = null, afterUrl = null;
    if (f.beforeFile) beforeUrl = await uploadPhoto(f.beforeFile, "before");
    if (f.afterFile) afterUrl = await uploadPhoto(f.afterFile, "after");
    const { error } = await supabase.from("snag_items").insert([{
      snag_number: num, project_id: f.pid, title: f.title,
      description: f.desc, location: f.location, category: f.category,
      responsible_sub_name: f.sub, assigned_engineer_name: f.engineer,
      due_date: f.due || null, status: "Open", remarks: f.remarks,
      consultant_comment: f.consultant,
      before_photo_url: beforeUrl, after_photo_url: afterUrl,
    }]);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };

  const update = async (id, f) => {
    let beforeUrl = f.beforeUrl, afterUrl = f.afterUrl;
    if (f.beforeFile) beforeUrl = await uploadPhoto(f.beforeFile, "before");
    if (f.afterFile) afterUrl = await uploadPhoto(f.afterFile, "after");
    const { error } = await supabase.from("snag_items").update({
      project_id: f.pid, title: f.title, description: f.desc,
      location: f.location, category: f.category,
      responsible_sub_name: f.sub, assigned_engineer_name: f.engineer,
      due_date: f.due || null, status: f.status, remarks: f.remarks,
      consultant_comment: f.consultant,
      before_photo_url: beforeUrl, after_photo_url: afterUrl,
    }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };

  const remove = async (id) => {
    const { error } = await supabase.from("snag_items").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  return { snags, loading, add, update, remove };
}

// ─────────────────────────────────────────────────────────────────────────────
// DAILY REPORTS HOOK
// ─────────────────────────────────────────────────────────────────────────────
function useDailyReports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const loadData = useCallback(async () => {
    const { data, error } = await supabase.from("daily_reports").select("*").order("report_date", { ascending: false });
    if (error) console.error("Reports:", error.message);
    if (data) setReports(data.map(r => ({
      id: r.id, pid: r.project_id, date: r.report_date || "",
      weather: r.weather || "", temp: r.temperature_high || "",
      manpower: r.manpower_total || 0, activities: r.work_activities || "",
      completed: r.work_completed || "", issues: r.issues_delays || "",
      safety: r.safety_observations || "", materials: r.materials_received || "",
      status: r.status || "Draft", preparedBy: r.prepared_by_name || "",
    })));
    setLoading(false);
  }, []);
  useEffect(() => { loadData(); }, [loadData]);

  const add = async (f) => {
    const { error } = await supabase.from("daily_reports").insert([{
      project_id: f.pid, report_date: f.date, weather: f.weather,
      temperature_high: parseInt(f.temp) || null, manpower_total: parseInt(f.manpower) || 0,
      work_activities: f.activities, work_completed: f.completed,
      issues_delays: f.issues, safety_observations: f.safety,
      materials_received: f.materials, status: "Draft", prepared_by_name: f.preparedBy,
    }]);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const update = async (id, f) => {
    const { error } = await supabase.from("daily_reports").update({
      project_id: f.pid, report_date: f.date, weather: f.weather,
      temperature_high: parseInt(f.temp) || null, manpower_total: parseInt(f.manpower) || 0,
      work_activities: f.activities, work_completed: f.completed,
      issues_delays: f.issues, safety_observations: f.safety,
      materials_received: f.materials, status: f.status, prepared_by_name: f.preparedBy,
    }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const remove = async (id) => {
    const { error } = await supabase.from("daily_reports").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  return { reports, loading, add, update, remove };
}

// ─────────────────────────────────────────────────────────────────────────────
// INSPECTIONS HOOK
// ─────────────────────────────────────────────────────────────────────────────
function useInspections() {
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const loadData = useCallback(async () => {
    const { data, error } = await supabase.from("inspections").select("*").order("created_at", { ascending: false });
    if (error) console.error("Inspections:", error.message);
    if (data) setInspections(data.map(i => ({
      id: i.id, pid: i.project_id, num: i.request_number || "",
      type: i.type || "WIR", desc: i.description || "",
      location: i.location || "", trade: i.trade || "",
      submitted: i.submitted_date || "", inspection: i.inspection_date || "",
      status: i.consultant_status || "Draft", remarks: i.remarks || "",
      submittedBy: i.submitted_by_name || "",
    })));
    setLoading(false);
  }, []);
  useEffect(() => { loadData(); }, [loadData]);

  const getNextNum = async (type) => {
    const { data } = await supabase.from("inspections").select("request_number").order("created_at", { ascending: false }).limit(1);
    const last = data?.[0]?.request_number || `${type}/AGBC/000/25`;
    const parts = last.split("/");
    const n = parseInt(parts[2] || "0") + 1;
    return `${type}/AGBC/${String(n).padStart(3, "0")}/25`;
  };

  const add = async (f) => {
    const num = await getNextNum(f.type);
    const { error } = await supabase.from("inspections").insert([{
      request_number: num, project_id: f.pid, type: f.type,
      description: f.desc, location: f.location, trade: f.trade,
      submitted_date: f.submitted || null, inspection_date: f.inspection || null,
      consultant_status: "Draft", remarks: f.remarks, submitted_by_name: f.submittedBy,
    }]);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const update = async (id, f) => {
    const { error } = await supabase.from("inspections").update({
      project_id: f.pid, type: f.type, description: f.desc,
      location: f.location, trade: f.trade,
      submitted_date: f.submitted || null, inspection_date: f.inspection || null,
      consultant_status: f.status, remarks: f.remarks, submitted_by_name: f.submittedBy,
    }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const remove = async (id) => {
    const { error } = await supabase.from("inspections").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  return { inspections, loading, add, update, remove };
}

// ─────────────────────────────────────────────────────────────────────────────
// DRAWINGS HOOK
// ─────────────────────────────────────────────────────────────────────────────
function useDrawings() {
  const [drawings, setDrawings] = useState([]);
  const [loading, setLoading] = useState(true);
  const loadData = useCallback(async () => {
    const { data, error } = await supabase.from("drawings").select("*").order("created_at", { ascending: false });
    if (error) console.error("Drawings:", error.message);
    if (data) setDrawings(data.map(d => ({
      id: d.id, pid: d.project_id, num: d.drawing_number || "",
      title: d.drawing_title || "", rev: d.revision || "A",
      discipline: d.discipline || "", received: d.date_received || "",
      latest: d.is_latest !== false, fileUrl: d.file_url || "", remarks: d.remarks || "",
    })));
    setLoading(false);
  }, []);
  useEffect(() => { loadData(); }, [loadData]);

  const uploadFile = async (file) => {
    const ext = file.name.split(".").pop();
    const name = `${Date.now()}_${Math.random().toString(36).slice(2)}.${ext}`;
    const { error } = await supabase.storage.from("drawings").upload(name, file);
    if (error) { console.error("File upload:", error.message); return null; }
    const { data: { publicUrl } } = supabase.storage.from("drawings").getPublicUrl(name);
    return publicUrl;
  };

  const add = async (f) => {
    let fileUrl = null;
    if (f.file) fileUrl = await uploadFile(f.file);
    const { error } = await supabase.from("drawings").insert([{
      project_id: f.pid, drawing_number: f.num, drawing_title: f.title,
      revision: f.rev, discipline: f.discipline, date_received: f.received || null,
      is_latest: true, remarks: f.remarks, file_url: fileUrl,
    }]);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const update = async (id, f) => {
    let fileUrl = f.fileUrl;
    if (f.file) fileUrl = await uploadFile(f.file);
    const { error } = await supabase.from("drawings").update({
      project_id: f.pid, drawing_number: f.num, drawing_title: f.title,
      revision: f.rev, discipline: f.discipline, date_received: f.received || null,
      remarks: f.remarks, file_url: fileUrl,
    }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const remove = async (id) => {
    const { error } = await supabase.from("drawings").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  return { drawings, loading, add, update, remove };
}

// ─────────────────────────────────────────────────────────────────────────────
// SUBCONTRACTORS HOOK
// ─────────────────────────────────────────────────────────────────────────────
function useSubcontractors() {
  const [subs, setSubs] = useState([]);
  const [loading, setLoading] = useState(true);
  const loadData = useCallback(async () => {
    const { data, error } = await supabase.from("subcontractors").select("*").order("company_name");
    if (error) console.error("Subs:", error.message);
    if (data) setSubs(data.map(s => ({
      id: s.id, name: s.company_name || "", contact: s.contact_person || "",
      phone: s.phone || "", email: s.email || "",
      trades: Array.isArray(s.trade) ? s.trade : (s.trade ? [s.trade] : []),
      active: s.is_active !== false, notes: s.performance_notes || "",
    })));
    setLoading(false);
  }, []);
  useEffect(() => { loadData(); }, [loadData]);

  const add = async (f) => {
    const { error } = await supabase.from("subcontractors").insert([{
      company_name: f.name, contact_person: f.contact, phone: f.phone,
      email: f.email, trade: f.trades, is_active: true, performance_notes: f.notes,
    }]);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const update = async (id, f) => {
    const { error } = await supabase.from("subcontractors").update({
      company_name: f.name, contact_person: f.contact, phone: f.phone,
      email: f.email, trade: f.trades, is_active: f.active, performance_notes: f.notes,
    }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const remove = async (id) => {
    const { error } = await supabase.from("subcontractors").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  return { subs, loading, add, update, remove };
}

// ─────────────────────────────────────────────────────────────────────────────
// PHOTOS HOOK
// ─────────────────────────────────────────────────────────────────────────────
function usePhotos() {
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const loadData = useCallback(async () => {
    const { data, error } = await supabase.from("project_photos").select("*").order("uploaded_at", { ascending: false });
    if (error) console.error("Photos:", error.message);
    if (data) setPhotos(data);
    setLoading(false);
  }, []);
  useEffect(() => { loadData(); }, [loadData]);

  const add = async (f) => {
    const ext = f.file.name.split(".").pop();
    const name = `${Date.now()}_${Math.random().toString(36).slice(2)}.${ext}`;
    const { error: upErr } = await supabase.storage.from("site-photos").upload(name, f.file);
    if (upErr) return { ok: false, error: upErr.message };
    const { data: { publicUrl } } = supabase.storage.from("site-photos").getPublicUrl(name);
    const { error } = await supabase.from("project_photos").insert([{
      project_id: f.pid, file_url: publicUrl, caption: f.caption, area: f.area,
    }]);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const update = async (id, f) => {
    const { error } = await supabase.from("project_photos").update({
      project_id: f.pid, caption: f.caption, area: f.area,
    }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  const remove = async (id) => {
    const { error } = await supabase.from("project_photos").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadData(); return { ok: true };
  };
  return { photos, loading, add, update, remove };
}

// ─────────────────────────────────────────────────────────────────────────────
// UTILITIES & SHARED COMPONENTS
// ─────────────────────────────────────────────────────────────────────────────
const fmtDate = (d) => { if (!d) return "—"; try { return new Date(d).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }); } catch { return d; } };
const fmtNum = (n) => n ? Number(n).toLocaleString() : "—";
const isOverdue = (d, s) => d && new Date(d) < new Date() && !["Completed", "Closed", "Approved"].includes(s);
const getInit = (e) => e ? e.substring(0, 2).toUpperCase() : "??";

const SC = {
  Open: "bg-red-100 text-red-700 border-red-200",
  "In Progress": "bg-blue-100 text-blue-700 border-blue-200",
  "On Hold": "bg-amber-100 text-amber-700 border-amber-200",
  Completed: "bg-green-100 text-green-700 border-green-200",
  Closed: "bg-slate-100 text-slate-600 border-slate-200",
  "Under Rectification": "bg-orange-100 text-orange-700 border-orange-200",
  "Ready for Review": "bg-purple-100 text-purple-700 border-purple-200",
  Rejected: "bg-red-100 text-red-700 border-red-200",
  Draft: "bg-slate-100 text-slate-600 border-slate-200",
  Submitted: "bg-blue-100 text-blue-700 border-blue-200",
  Approved: "bg-green-100 text-green-700 border-green-200",
  Active: "bg-green-100 text-green-700 border-green-200",
  Tender: "bg-amber-100 text-amber-700 border-amber-200",
  Inactive: "bg-slate-100 text-slate-500 border-slate-200",
  Cancelled: "bg-red-100 text-red-600 border-red-200",
};
const PC = { Critical: "bg-red-600 text-white", High: "bg-orange-500 text-white", Medium: "bg-amber-400 text-white", Low: "bg-slate-400 text-white" };
const DC = { Architectural: "bg-blue-100 text-blue-700", Structural: "bg-orange-100 text-orange-700", MEP: "bg-purple-100 text-purple-700", Civil: "bg-green-100 text-green-700" };

const Badge = ({ text, cls }) => <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold border ${cls || SC[text] || "bg-slate-100 text-slate-600 border-slate-200"}`}>{text || "—"}</span>;
const Spinner = () => <div className="flex items-center justify-center py-24"><div className="w-9 h-9 border-4 border-amber-400 border-t-transparent rounded-full animate-spin"></div></div>;
const Lbl = ({ t, req }) => <label className="text-xs font-semibold text-slate-600 block mb-1">{t}{req && <span className="text-red-500 ml-0.5">*</span>}</label>;
const cls = "w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 bg-white";
const Inp = (p) => <input {...p} className={`${cls} ${p.className || ""}`} />;
const Sel = ({ children, ...p }) => <select {...p} className={`${cls} ${p.className || ""}`}>{children}</select>;
const Txta = ({ rows, ...p }) => <textarea rows={rows || 3} {...p} className={`${cls} resize-none`} />;

const Btn = ({ onClick, disabled, saving, label, color = "amber" }) => {
  const colors = { amber: "bg-amber-500 hover:bg-amber-600", red: "bg-red-500 hover:bg-red-600", slate: "bg-slate-200 hover:bg-slate-300 text-slate-700" };
  return (
    <button onClick={onClick} disabled={disabled || saving} className={`${colors[color]} ${color === "slate" ? "" : "text-white"} font-semibold text-sm px-5 py-2.5 rounded-lg flex items-center gap-2 disabled:opacity-60 transition-colors`}>
      {saving ? <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>Saving...</> : label}
    </button>
  );
};
const ActBtn = ({ onClick, label, color }) => {
  const c = { view: "text-blue-600 hover:bg-blue-50 border-blue-200", edit: "text-amber-600 hover:bg-amber-50 border-amber-200", del: "text-red-600 hover:bg-red-50 border-red-200" };
  return <button onClick={onClick} className={`px-2.5 py-1 rounded-lg text-xs font-bold border transition-colors ${c[color] || ""}`}>{label}</button>;
};
const BackBtn = ({ onClick }) => <button onClick={onClick} className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-800 font-medium mb-1">← Back</button>;
const PageTitle = ({ title, count, btn }) => (
  <div className="flex items-center justify-between mb-4">
    <div><h2 className="text-xl font-bold text-slate-800">{title}</h2>{count !== undefined && <p className="text-xs text-slate-400 mt-0.5">{count} records</p>}</div>
    {btn}
  </div>
);
const AddBtn = ({ onClick, label }) => (
  <button onClick={onClick} className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors shadow-sm">
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4"/></svg>
    {label}
  </button>
);
const SearchBar = ({ value, onChange, placeholder }) => (
  <div className="relative">
    <svg className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
    <Inp value={value} onChange={onChange} placeholder={placeholder || "Search..."} className="pl-9 w-56" />
  </div>
);
const EmptyState = ({ msg, onCreate }) => (
  <div className="text-center py-20 bg-white rounded-xl border border-slate-200">
    <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
      <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
    </div>
    <p className="text-slate-500 text-sm mb-3">{msg}</p>
    {onCreate && <button onClick={onCreate} className="text-amber-500 font-semibold text-sm hover:underline">+ Add First Record</button>}
  </div>
);
const FormCard = ({ children }) => <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4 shadow-sm">{children}</div>;
const Grid2 = ({ children }) => <div className="grid grid-cols-2 gap-4">{children}</div>;
const Grid3 = ({ children }) => <div className="grid grid-cols-3 gap-4">{children}</div>;
const FormActions = ({ saving, onSave, onCancel, label = "Save" }) => (
  <div className="flex gap-3 pt-2 border-t border-slate-100">
    <Btn saving={saving} onClick={onSave} label={label} />
    <Btn onClick={onCancel} label="Cancel" color="slate" />
  </div>
);

// ─────────────────────────────────────────────────────────────────────────────
// ICON
// ─────────────────────────────────────────────────────────────────────────────
const Icon = ({ name, cls: c = "w-5 h-5" }) => {
  const d = {
    dashboard: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
    projects: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
    tasks: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4",
    snags: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z",
    reports: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
    drawings: "M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01",
    inspections: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01",
    photos: "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z",
    subs: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z",
    bell: "M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9",
    logout: "M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1",
    map: "M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z",
    eye: "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z",
    warn: "M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z",
    edit: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z",
    trash: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16",
  };
  return <svg className={c} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d={d[name] || ""}/></svg>;
};

// ─────────────────────────────────────────────────────────────────────────────
// SIDEBAR & HEADER
// ─────────────────────────────────────────────────────────────────────────────
const NAV = [
  { id: "dashboard", label: "Dashboard", icon: "dashboard" },
  { id: "projects", label: "Projects", icon: "projects" },
  { id: "tasks", label: "Tasks", icon: "tasks" },
  { id: "snags", label: "Snag List", icon: "snags" },
  { id: "reports", label: "Daily Reports", icon: "reports" },
  { id: "inspections", label: "Inspections", icon: "inspections" },
  { id: "drawings", label: "Drawing Register", icon: "drawings" },
  { id: "photos", label: "Progress Photos", icon: "photos" },
  { id: "subcontractors", label: "Subcontractors", icon: "subs" },
];

const Sidebar = ({ active, onNav, collapsed, user, onSignOut }) => (
  <aside className={`${collapsed ? "w-16" : "w-60"} bg-slate-900 text-white flex flex-col transition-all duration-200 shrink-0`}>
    <div className="p-4 border-b border-slate-700 flex items-center gap-3 min-h-[57px]">
      <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center shrink-0">
        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
      </div>
      {!collapsed && <div><div className="text-sm font-bold leading-tight">AGBC</div><div className="text-xs text-slate-400">Site Management</div></div>}
    </div>
    <nav className="flex-1 py-2 overflow-y-auto">
      {NAV.map(n => (
        <button key={n.id} onClick={() => onNav(n.id)}
          className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${active === n.id ? "bg-amber-500 text-white font-semibold" : "text-slate-300 hover:bg-slate-800 hover:text-white"}`}>
          <Icon name={n.icon} cls="w-5 h-5 shrink-0" />
          {!collapsed && <span className="truncate">{n.label}</span>}
        </button>
      ))}
    </nav>
    <div className="p-4 border-t border-slate-700">
      {!collapsed ? (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center text-xs font-bold shrink-0">{getInit(user?.email)}</div>
            <div className="min-w-0"><div className="text-xs font-semibold truncate">{user?.email}</div><div className="text-xs text-slate-400">Al Ghaith Building</div></div>
          </div>
          <button onClick={onSignOut} className="w-full flex items-center justify-center gap-2 text-xs text-slate-400 hover:text-red-400 border border-slate-700 hover:border-red-500 px-3 py-1.5 rounded-lg transition-colors">
            <Icon name="logout" cls="w-3.5 h-3.5" />Sign Out
          </button>
        </div>
      ) : (
        <button onClick={onSignOut} className="w-full flex justify-center text-slate-400 hover:text-red-400 p-1"><Icon name="logout" cls="w-4 h-4" /></button>
      )}
    </div>
  </aside>
);

const Header = ({ title, onToggle, user }) => (
  <header className="h-14 bg-white border-b border-slate-200 flex items-center px-4 gap-3 shrink-0 shadow-sm">
    <button onClick={onToggle} className="text-slate-400 hover:text-slate-700 p-1 rounded-lg hover:bg-slate-100">
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
    </button>
    <span className="font-semibold text-slate-800">{title}</span>
    <div className="ml-auto flex items-center gap-2">
      <button className="relative p-2 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100">
        <Icon name="bell" cls="w-5 h-5" />
        <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
      </button>
      <div className="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center text-xs font-bold text-white">{getInit(user?.email)}</div>
    </div>
  </header>
);

const StatCard = ({ label, value, sub, color, icon }) => (
  <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-start gap-3 shadow-sm">
    <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${color}`}><Icon name={icon} cls="w-5 h-5 text-white" /></div>
    <div><div className="text-2xl font-bold text-slate-800">{value}</div><div className="text-xs text-slate-500">{label}</div>{sub && <div className="text-xs text-slate-400">{sub}</div>}</div>
  </div>
);

// ─────────────────────────────────────────────────────────────────────────────
// DASHBOARD
// ─────────────────────────────────────────────────────────────────────────────
const Dashboard = ({ projects, tasks, snags, inspections, reports }) => {
  const openTasks = tasks.filter(t => !["Completed", "Closed"].includes(t.status)).length;
  const openSnags = snags.filter(s => s.status !== "Closed").length;
  const today = new Date().toLocaleDateString("en-GB", { weekday: "long", day: "2-digit", month: "long", year: "numeric" });
  return (
    <div className="p-6 space-y-6">
      <div><h2 className="text-xl font-bold text-slate-800">Good morning 👋</h2><p className="text-sm text-slate-400 mt-0.5">{today} — Dubai, UAE</p></div>
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard label="Active Projects" value={projects.filter(p => p.status === "Active").length} sub={`${projects.length} total`} color="bg-blue-500" icon="projects" />
        <StatCard label="Open Tasks" value={openTasks} sub={`${tasks.length} total`} color="bg-amber-500" icon="tasks" />
        <StatCard label="Open Snags" value={openSnags} sub={`${snags.length} total`} color="bg-orange-500" icon="snags" />
        <StatCard label="Pending IR" value={inspections.filter(i => ["Draft", "Submitted"].includes(i.status)).length} sub="Inspection requests" color="bg-purple-500" icon="inspections" />
        <StatCard label="Reports" value={reports.length} sub="Total submitted" color="bg-green-500" icon="reports" />
        <StatCard label="Overdue" value={tasks.filter(t => isOverdue(t.due, t.status)).length} sub="Need attention" color="bg-red-500" icon="warn" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="px-5 py-3 border-b border-slate-100 flex items-center justify-between"><span className="font-semibold text-slate-800 text-sm">Projects Overview</span><span className="text-xs text-slate-400">{projects.length} projects</span></div>
          <div className="divide-y divide-slate-100">
            {projects.slice(0, 6).map(p => (
              <div key={p.id} className="px-5 py-3 flex items-center gap-3">
                <div className="flex-1 min-w-0"><div className="text-sm font-semibold text-slate-800 truncate">{p.number}</div><div className="text-xs text-slate-400 truncate">{p.location}</div></div>
                <div className="text-xs text-slate-500">{p.duration ? `${p.duration}M` : ""}</div>
                <Badge text={p.status} />
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="px-5 py-3 border-b border-slate-100 flex items-center justify-between"><span className="font-semibold text-slate-800 text-sm">Open Snags</span><span className="text-xs text-slate-400">{openSnags} open</span></div>
          <div className="divide-y divide-slate-100">
            {snags.filter(s => s.status !== "Closed").slice(0, 5).map(s => (
              <div key={s.id} className="px-5 py-3 flex items-center gap-3">
                <span className="text-xs font-mono font-bold text-amber-600">{s.num}</span>
                <div className="flex-1 min-w-0 text-sm text-slate-700 truncate">{s.title}</div>
                <Badge text={s.status} />
              </div>
            ))}
            {openSnags === 0 && <div className="px-5 py-8 text-center text-slate-400 text-sm">No open snags 🎉</div>}
          </div>
        </div>
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// PROJECTS MODULE — Full CRUD
// ─────────────────────────────────────────────────────────────────────────────
const PROJ_STATUS = ["Active", "Tender", "On Hold", "Completed", "Cancelled"];
const EMPTY_PROJ = { number: "", name: "", plot: "", location: "", plotArea: "", bua: "", duration: "", consultant: "", consultantContact: "", status: "Active", mapUrl: "" };

const Projects = ({ projects, loading, onAdd, onUpdate, onDelete, showToast }) => {
  const [mode, setMode] = useState("list"); // list | form | view
  const [sel, setSel] = useState(null);
  const [form, setForm] = useState(EMPTY_PROJ);
  const [search, setSearch] = useState("");
  const [saving, setSaving] = useState(false);
  const [confirmId, setConfirmId] = useState(null);

  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));

  const openCreate = () => { setForm(EMPTY_PROJ); setSel(null); setMode("form"); };
  const openEdit = p => {
    setSel(p);
    setForm({ number: p.number, name: p.name, plot: p.plot, location: p.location, plotArea: String(p.plotArea || ""), bua: String(p.bua || ""), duration: String(p.duration || ""), consultant: p.consultant, consultantContact: p.consultantContact, status: p.status, mapUrl: p.mapUrl });
    setMode("form");
  };
  const openView = p => { setSel(p); setMode("view"); };
  const goList = () => { setMode("list"); setSel(null); };

  const handleSave = async () => {
    if (!form.number.trim() || !form.name.trim()) { showToast("Project Number and Name are required", "error"); return; }
    setSaving(true);
    const res = sel ? await onUpdate(sel.id, form) : await onAdd(form);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Save failed", "error"); return; }
    showToast(sel ? "Project updated successfully!" : "Project created successfully!");
    goList();
  };

  const handleDelete = async id => {
    const res = await onDelete(id);
    if (!res.ok) { showToast(res.error || "Delete failed", "error"); return; }
    showToast("Project deleted!"); setConfirmId(null); if (mode !== "list") goList();
  };

  const filtered = projects.filter(p =>
    [p.number, p.name, p.location, p.consultant].join(" ").toLowerCase().includes(search.toLowerCase())
  );

  // ── VIEW ──
  if (mode === "view" && sel) return (
    <div className="p-6 max-w-3xl">
      {confirmId && <ConfirmDialog message={`Delete project "${sel.name}"? This cannot be undone.`} onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <BackBtn onClick={goList} />
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="bg-gradient-to-r from-slate-800 to-slate-700 px-6 py-5">
          <div className="flex items-start justify-between">
            <div><span className="text-amber-400 text-xs font-mono font-bold">{sel.number}</span><h2 className="text-xl font-bold text-white mt-1">{sel.name}</h2></div>
            <Badge text={sel.status} cls="bg-amber-500 text-white border-amber-400" />
          </div>
        </div>
        <div className="p-6 grid grid-cols-2 gap-5">
          {[["Location", sel.location], ["Plot Number", sel.plot], ["Duration", sel.duration ? `${sel.duration} Months` : null], ["Consultant", sel.consultant], ["Consultant Contact", sel.consultantContact], ["Plot Area", sel.plotArea ? `${fmtNum(sel.plotArea)} sqft` : null], ["BUA", sel.bua ? `${fmtNum(sel.bua)} sqft` : null]].filter(([, v]) => v).map(([k, v]) => (
            <div key={k}><div className="text-xs text-slate-400 font-medium mb-0.5">{k}</div><div className="text-sm font-semibold text-slate-800">{v}</div></div>
          ))}
        </div>
        {sel.mapUrl && <div className="px-6 pb-4"><a href={sel.mapUrl} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 text-blue-600 text-sm font-medium hover:underline"><Icon name="map" cls="w-4 h-4" />View on Map</a></div>}
        <div className="px-6 py-4 border-t border-slate-100 flex gap-3">
          <Btn onClick={() => openEdit(sel)} label="Edit Project" />
          <Btn onClick={() => setConfirmId(sel.id)} label="Delete" color="red" />
        </div>
      </div>
    </div>
  );

  // ── FORM ──
  if (mode === "form") return (
    <div className="p-6 max-w-2xl">
      <BackBtn onClick={goList} />
      <h2 className="text-xl font-bold text-slate-800 mb-4">{sel ? "Edit Project" : "New Project"}</h2>
      <FormCard>
        <Grid2>
          <div><Lbl t="Project Number" req /><Inp value={form.number} onChange={set("number")} placeholder="e.g. J224" /></div>
          <div><Lbl t="Status" /><Sel value={form.status} onChange={set("status")}>{PROJ_STATUS.map(s => <option key={s}>{s}</option>)}</Sel></div>
        </Grid2>
        <div><Lbl t="Project Name" req /><Inp value={form.name} onChange={set("name")} placeholder="e.g. G+5+Roof Residential Building" /></div>
        <Grid2>
          <div><Lbl t="Location" /><Inp value={form.location} onChange={set("location")} placeholder="e.g. Dubai South" /></div>
          <div><Lbl t="Plot Number" /><Inp value={form.plot} onChange={set("plot")} placeholder="e.g. 5132010" /></div>
        </Grid2>
        <Grid3>
          <div><Lbl t="Duration (Months)" /><Inp type="number" value={form.duration} onChange={set("duration")} placeholder="e.g. 15" /></div>
          <div><Lbl t="Plot Area (sqft)" /><Inp type="number" value={form.plotArea} onChange={set("plotArea")} placeholder="e.g. 6200" /></div>
          <div><Lbl t="BUA (sqft)" /><Inp type="number" value={form.bua} onChange={set("bua")} placeholder="e.g. 18500" /></div>
        </Grid3>
        <Grid2>
          <div><Lbl t="Consultant" /><Inp value={form.consultant} onChange={set("consultant")} placeholder="e.g. ANT Engineering" /></div>
          <div><Lbl t="Consultant Contact" /><Inp value={form.consultantContact} onChange={set("consultantContact")} placeholder="Phone or email" /></div>
        </Grid2>
        <div><Lbl t="Google Map URL" /><Inp value={form.mapUrl} onChange={set("mapUrl")} placeholder="https://maps.google.com/..." /></div>
        <FormActions saving={saving} onSave={handleSave} onCancel={goList} label={sel ? "Update Project" : "Save Project"} />
      </FormCard>
    </div>
  );

  // ── LIST ──
  return (
    <div className="p-6">
      {confirmId && <ConfirmDialog message="Delete this project? All related data may be affected." onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <PageTitle title="Projects" count={filtered.length} btn={<AddBtn onClick={openCreate} label="New Project" />} />
      <div className="mb-4"><SearchBar value={search} onChange={e => setSearch(e.target.value)} placeholder="Search projects..." /></div>
      {loading ? <Spinner /> : filtered.length === 0 ? <EmptyState msg="No projects found" onCreate={openCreate} /> : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>{["Project No.", "Name", "Location", "Consultant", "Duration", "Status", "Actions"].map(h => <th key={h} className="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase tracking-wide">{h}</th>)}</tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map(p => (
                <tr key={p.id} className="hover:bg-amber-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs font-bold text-amber-700">{p.number}</td>
                  <td className="px-4 py-3 font-medium text-slate-800 max-w-[200px]"><div className="truncate">{p.name}</div></td>
                  <td className="px-4 py-3 text-xs text-slate-600">{p.location}</td>
                  <td className="px-4 py-3 text-xs text-slate-600">{p.consultant}</td>
                  <td className="px-4 py-3 text-xs text-slate-600">{p.duration ? `${p.duration} M` : "—"}</td>
                  <td className="px-4 py-3"><Badge text={p.status} /></td>
                  <td className="px-4 py-3"><div className="flex gap-1.5"><ActBtn onClick={() => openView(p)} label="View" color="view" /><ActBtn onClick={() => openEdit(p)} label="Edit" color="edit" /><ActBtn onClick={() => setConfirmId(p.id)} label="Del" color="del" /></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// TASKS MODULE — Full CRUD
// ─────────────────────────────────────────────────────────────────────────────
const TASK_STATUS = ["Open", "In Progress", "On Hold", "Completed", "Closed"];
const TRADES = ["Civil / Structural", "Civil / Masonry", "Civil / Waterproofing", "MEP / HVAC", "MEP / Electrical", "MEP / Plumbing", "Finishing", "Aluminum / Glazing", "Aluminum / Cladding", "Safety", "Other"];
const EMPTY_TASK = { pid: "", title: "", desc: "", location: "", trade: "", assignee: "", priority: "Medium", status: "Open", due: "" };

const Tasks = ({ projects, tasks, loading, onAdd, onUpdate, onDelete, showToast }) => {
  const [mode, setMode] = useState("list");
  const [sel, setSel] = useState(null);
  const [form, setForm] = useState(EMPTY_TASK);
  const [search, setSearch] = useState("");
  const [fStatus, setFStatus] = useState("All");
  const [fProject, setFProject] = useState("All");
  const [saving, setSaving] = useState(false);
  const [confirmId, setConfirmId] = useState(null);
  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));

  const openCreate = () => { setForm(EMPTY_TASK); setSel(null); setMode("form"); };
  const openEdit = t => { setSel(t); setForm({ pid: t.pid, title: t.title, desc: t.desc, location: t.location, trade: t.trade, assignee: t.assignee, priority: t.priority, status: t.status, due: t.due }); setMode("form"); };
  const openView = t => { setSel(t); setMode("view"); };
  const goList = () => { setMode("list"); setSel(null); };

  const handleSave = async () => {
    if (!form.title.trim() || !form.pid) { showToast("Project and Title are required", "error"); return; }
    setSaving(true);
    const res = sel ? await onUpdate(sel.id, form) : await onAdd(form);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Save failed", "error"); return; }
    showToast(sel ? "Task updated!" : "Task created!"); goList();
  };
  const handleDelete = async id => {
    const res = await onDelete(id);
    if (!res.ok) { showToast(res.error || "Delete failed", "error"); return; }
    showToast("Task deleted!"); setConfirmId(null); if (mode !== "list") goList();
  };

  const filtered = tasks.filter(t => {
    if (fStatus !== "All" && t.status !== fStatus) return false;
    if (fProject !== "All" && t.pid !== fProject) return false;
    if (search && !`${t.title} ${t.assignee} ${t.location}`.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  if (mode === "view" && sel) return (
    <div className="p-6 max-w-2xl">
      {confirmId && <ConfirmDialog message="Delete this task?" onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <BackBtn onClick={goList} />
      <FormCard>
        <div className="flex items-start justify-between"><h2 className="text-lg font-bold text-slate-800">{sel.title}</h2><Badge text={sel.status} /></div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          {[["Project", projects.find(p => p.id === sel.pid)?.number], ["Location", sel.location], ["Trade", sel.trade], ["Assignee", sel.assignee], ["Priority", sel.priority], ["Due Date", fmtDate(sel.due)]].map(([k, v]) => (
            <div key={k}><div className="text-xs text-slate-400 font-medium">{k}</div><div className="font-semibold text-slate-800 mt-0.5">{v || "—"}</div></div>
          ))}
        </div>
        {sel.desc && <div><div className="text-xs text-slate-400 font-medium mb-1">Description</div><p className="text-sm text-slate-700 bg-slate-50 p-3 rounded-lg">{sel.desc}</p></div>}
        <div className="flex gap-3 pt-1"><Btn onClick={() => openEdit(sel)} label="Edit Task" /><Btn onClick={() => setConfirmId(sel.id)} label="Delete" color="red" /></div>
      </FormCard>
    </div>
  );

  if (mode === "form") return (
    <div className="p-6 max-w-2xl">
      <BackBtn onClick={goList} />
      <h2 className="text-xl font-bold text-slate-800 mb-4">{sel ? "Edit Task" : "New Task"}</h2>
      <FormCard>
        <div><Lbl t="Project" req /><Sel value={form.pid} onChange={set("pid")}><option value="">Select Project...</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}</Sel></div>
        <div><Lbl t="Task Title" req /><Inp value={form.title} onChange={set("title")} placeholder="e.g. Pour Grade Slab — Block A" /></div>
        <div><Lbl t="Description" /><Txta value={form.desc} onChange={set("desc")} placeholder="Task details..." /></div>
        <Grid2>
          <div><Lbl t="Location" /><Inp value={form.location} onChange={set("location")} placeholder="e.g. Level 3" /></div>
          <div><Lbl t="Trade" /><Sel value={form.trade} onChange={set("trade")}><option value="">Select...</option>{TRADES.map(t => <option key={t}>{t}</option>)}</Sel></div>
        </Grid2>
        <Grid3>
          <div><Lbl t="Assignee" /><Inp value={form.assignee} onChange={set("assignee")} placeholder="Engineer name" /></div>
          <div><Lbl t="Priority" /><Sel value={form.priority} onChange={set("priority")}>{["Low", "Medium", "High", "Critical"].map(p => <option key={p}>{p}</option>)}</Sel></div>
          <div><Lbl t="Due Date" /><Inp type="date" value={form.due} onChange={set("due")} /></div>
        </Grid3>
        {sel && <div><Lbl t="Status" /><Sel value={form.status} onChange={set("status")}>{TASK_STATUS.map(s => <option key={s}>{s}</option>)}</Sel></div>}
        <FormActions saving={saving} onSave={handleSave} onCancel={goList} label={sel ? "Update Task" : "Save Task"} />
      </FormCard>
    </div>
  );

  return (
    <div className="p-6">
      {confirmId && <ConfirmDialog message="Delete this task permanently?" onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <PageTitle title="Task Management" count={filtered.length} btn={<AddBtn onClick={openCreate} label="New Task" />} />
      <div className="flex flex-wrap gap-3 mb-4">
        <SearchBar value={search} onChange={e => setSearch(e.target.value)} placeholder="Search tasks..." />
        <Sel value={fStatus} onChange={e => setFStatus(e.target.value)} className="w-auto"><option value="All">All Status</option>{TASK_STATUS.map(s => <option key={s}>{s}</option>)}</Sel>
        <Sel value={fProject} onChange={e => setFProject(e.target.value)} className="w-auto"><option value="All">All Projects</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number}</option>)}</Sel>
      </div>
      {loading ? <Spinner /> : filtered.length === 0 ? <EmptyState msg="No tasks found" onCreate={openCreate} /> : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>{["Task", "Project", "Assignee", "Priority", "Due Date", "Status", "Actions"].map(h => <th key={h} className="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase tracking-wide">{h}</th>)}</tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map(t => (
                <tr key={t.id} className="hover:bg-amber-50 transition-colors">
                  <td className="px-4 py-3"><div className="font-medium text-slate-800 max-w-[160px] truncate">{t.title}</div><div className="text-xs text-slate-400">{t.location}</div></td>
                  <td className="px-4 py-3 text-xs text-slate-600">{projects.find(p => p.id === t.pid)?.number || "—"}</td>
                  <td className="px-4 py-3 text-xs text-slate-700">{t.assignee || "—"}</td>
                  <td className="px-4 py-3"><Badge text={t.priority} cls={PC[t.priority]} /></td>
                  <td className="px-4 py-3 text-xs"><span className={isOverdue(t.due, t.status) ? "text-red-600 font-bold" : "text-slate-600"}>{fmtDate(t.due)}</span></td>
                  <td className="px-4 py-3"><Badge text={t.status} /></td>
                  <td className="px-4 py-3"><div className="flex gap-1.5"><ActBtn onClick={() => openView(t)} label="View" color="view" /><ActBtn onClick={() => openEdit(t)} label="Edit" color="edit" /><ActBtn onClick={() => setConfirmId(t.id)} label="Del" color="del" /></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// SNAGS MODULE — Full CRUD
// ─────────────────────────────────────────────────────────────────────────────
const SNAG_STATUS = ["Open", "Under Rectification", "Ready for Review", "Closed", "Rejected"];
const SNAG_CATS = ["Architectural", "Structural", "MEP", "Finishing", "Civil", "Aluminum", "Safety", "Other"];
const EMPTY_SNAG = { pid: "", title: "", desc: "", location: "", category: "", sub: "", engineer: "", due: "", status: "Open", remarks: "", consultant: "", beforeUrl: "", afterUrl: "", beforeFile: null, afterFile: null };

const Snags = ({ projects, snags, loading, onAdd, onUpdate, onDelete, showToast }) => {
  const [mode, setMode] = useState("list");
  const [sel, setSel] = useState(null);
  const [form, setForm] = useState(EMPTY_SNAG);
  const [search, setSearch] = useState("");
  const [fStatus, setFStatus] = useState("All");
  const [fProject, setFProject] = useState("All");
  const [fCat, setFCat] = useState("All");
  const [saving, setSaving] = useState(false);
  const [confirmId, setConfirmId] = useState(null);
  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));

  const openCreate = () => { setForm(EMPTY_SNAG); setSel(null); setMode("form"); };
  const openEdit = s => {
    setSel(s);
    setForm({ pid: s.pid, title: s.title, desc: s.desc, location: s.location, category: s.category, sub: s.sub, engineer: s.engineer, due: s.due, status: s.status, remarks: s.remarks, consultant: s.consultant, beforeUrl: s.beforeUrl, afterUrl: s.afterUrl, beforeFile: null, afterFile: null });
    setMode("form");
  };
  const openView = s => { setSel(s); setMode("view"); };
  const goList = () => { setMode("list"); setSel(null); };

  const handleSave = async () => {
    if (!form.title.trim() || !form.pid) { showToast("Project and Title are required", "error"); return; }
    setSaving(true);
    const res = sel ? await onUpdate(sel.id, form) : await onAdd(form);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Save failed. Check your internet and try again.", "error"); return; }
    showToast(sel ? "Snag updated successfully!" : "Snag created successfully!");
    goList();
  };

  const handleDelete = async id => {
    const res = await onDelete(id);
    if (!res.ok) { showToast(res.error || "Delete failed", "error"); return; }
    showToast("Snag deleted!"); setConfirmId(null); if (mode !== "list") goList();
  };

  const filtered = snags.filter(s => {
    if (fStatus !== "All" && s.status !== fStatus) return false;
    if (fProject !== "All" && s.pid !== fProject) return false;
    if (fCat !== "All" && s.category !== fCat) return false;
    if (search && !`${s.title} ${s.location} ${s.sub} ${s.engineer} ${s.num}`.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  // ── VIEW ──
  if (mode === "view" && sel) return (
    <div className="p-6 max-w-3xl">
      {confirmId && <ConfirmDialog message={`Delete snag "${sel.num}"? This cannot be undone.`} onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <BackBtn onClick={goList} />
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="bg-gradient-to-r from-orange-600 to-red-600 px-6 py-5">
          <div className="flex items-start justify-between">
            <div><span className="text-orange-200 text-xs font-mono font-bold">{sel.num}</span><h2 className="text-lg font-bold text-white mt-1">{sel.title}</h2></div>
            <Badge text={sel.status} cls="bg-white/20 text-white border-white/30" />
          </div>
        </div>
        <div className="p-6 space-y-5">
          <div className="grid grid-cols-2 gap-4 text-sm">
            {[["Project", projects.find(p => p.id === sel.pid)?.number], ["Category", sel.category], ["Location", sel.location], ["Subcontractor", sel.sub], ["Engineer", sel.engineer], ["Due Date", fmtDate(sel.due)]].map(([k, v]) => (
              <div key={k}><div className="text-xs text-slate-400 font-medium">{k}</div><div className="font-semibold text-slate-800 mt-0.5">{v || "—"}</div></div>
            ))}
          </div>
          {sel.desc && <div className="border-t border-slate-100 pt-4"><div className="text-xs text-slate-400 font-medium mb-1">Description</div><p className="text-sm text-slate-700 bg-slate-50 p-3 rounded-lg">{sel.desc}</p></div>}
          {sel.remarks && <div><div className="text-xs text-slate-400 font-medium mb-1">Remarks</div><p className="text-sm text-slate-700 bg-slate-50 p-3 rounded-lg">{sel.remarks}</p></div>}
          {sel.consultant && <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-800"><strong>Consultant:</strong> {sel.consultant}</div>}
          {(sel.beforeUrl || sel.afterUrl) && (
            <div className="border-t border-slate-100 pt-4">
              <div className="text-xs text-slate-400 font-medium mb-3">Site Photos</div>
              <div className="grid grid-cols-2 gap-4">
                {sel.beforeUrl && <div><div className="text-xs font-semibold text-slate-600 mb-1.5">📷 Before</div><img src={sel.beforeUrl} alt="Before" className="w-full h-48 object-cover rounded-xl border border-slate-200" /></div>}
                {sel.afterUrl && <div><div className="text-xs font-semibold text-slate-600 mb-1.5">📷 After</div><img src={sel.afterUrl} alt="After" className="w-full h-48 object-cover rounded-xl border border-slate-200" /></div>}
              </div>
            </div>
          )}
          <div className="flex gap-3 pt-2 border-t border-slate-100"><Btn onClick={() => openEdit(sel)} label="Edit Snag" /><Btn onClick={() => setConfirmId(sel.id)} label="Delete" color="red" /></div>
        </div>
      </div>
    </div>
  );

  // ── FORM ──
  if (mode === "form") return (
    <div className="p-6 max-w-2xl">
      <BackBtn onClick={goList} />
      <h2 className="text-xl font-bold text-slate-800 mb-4">{sel ? `Edit Snag — ${sel.num}` : "New Snag"}</h2>
      <FormCard>
        <div><Lbl t="Project" req /><Sel value={form.pid} onChange={set("pid")}><option value="">Select Project...</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}</Sel></div>
        <div><Lbl t="Snag Title" req /><Inp value={form.title} onChange={set("title")} placeholder="e.g. Plastering crack — Column C7" /></div>
        <div><Lbl t="Description" /><Txta value={form.desc} onChange={set("desc")} placeholder="Describe the defect in detail..." /></div>
        <Grid2>
          <div><Lbl t="Location" /><Inp value={form.location} onChange={set("location")} placeholder="e.g. Level 2 – Grid C7" /></div>
          <div><Lbl t="Category" /><Sel value={form.category} onChange={set("category")}><option value="">Select...</option>{SNAG_CATS.map(c => <option key={c}>{c}</option>)}</Sel></div>
        </Grid2>
        <Grid2>
          <div><Lbl t="Responsible Subcontractor" /><Inp value={form.sub} onChange={set("sub")} placeholder="Company name" /></div>
          <div><Lbl t="Assigned Engineer" /><Inp value={form.engineer} onChange={set("engineer")} placeholder="Engineer name" /></div>
        </Grid2>
        <Grid2>
          <div><Lbl t="Due Date" /><Inp type="date" value={form.due} onChange={set("due")} /></div>
          {sel && <div><Lbl t="Status" /><Sel value={form.status} onChange={set("status")}>{SNAG_STATUS.map(s => <option key={s}>{s}</option>)}</Sel></div>}
        </Grid2>
        <div><Lbl t="Remarks" /><Txta value={form.remarks} onChange={set("remarks")} rows={2} placeholder="Additional notes..." /></div>
        <div><Lbl t="Consultant Comment / NCR" /><Inp value={form.consultant} onChange={set("consultant")} placeholder="e.g. NCR raised by SSH Eng." /></div>
        <div className="border-t border-slate-100 pt-3">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3">Site Photos</div>
          <Grid2>
            <div>
              <Lbl t="Before Photo" />
              <Inp type="file" accept="image/*" onChange={e => setForm(p => ({ ...p, beforeFile: e.target.files[0] }))} />
              {form.beforeUrl && !form.beforeFile && <img src={form.beforeUrl} alt="Before" className="mt-2 w-full h-28 object-cover rounded-lg border border-slate-200" />}
              {form.beforeFile && <p className="text-xs text-green-600 mt-1">✓ New photo selected: {form.beforeFile.name}</p>}
            </div>
            <div>
              <Lbl t="After Photo" />
              <Inp type="file" accept="image/*" onChange={e => setForm(p => ({ ...p, afterFile: e.target.files[0] }))} />
              {form.afterUrl && !form.afterFile && <img src={form.afterUrl} alt="After" className="mt-2 w-full h-28 object-cover rounded-lg border border-slate-200" />}
              {form.afterFile && <p className="text-xs text-green-600 mt-1">✓ New photo selected: {form.afterFile.name}</p>}
            </div>
          </Grid2>
        </div>
        <FormActions saving={saving} onSave={handleSave} onCancel={goList} label={sel ? "Update Snag" : "Save Snag"} />
      </FormCard>
    </div>
  );

  // ── LIST ──
  return (
    <div className="p-6">
      {confirmId && <ConfirmDialog message="Delete this snag permanently?" onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <PageTitle title="Snag / Punch List" count={filtered.length} btn={<AddBtn onClick={openCreate} label="New Snag" />} />

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-3">
        <SearchBar value={search} onChange={e => setSearch(e.target.value)} placeholder="Search snags..." />
        <Sel value={fProject} onChange={e => setFProject(e.target.value)} className="w-auto"><option value="All">All Projects</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number}</option>)}</Sel>
        <Sel value={fCat} onChange={e => setFCat(e.target.value)} className="w-auto"><option value="All">All Categories</option>{SNAG_CATS.map(c => <option key={c}>{c}</option>)}</Sel>
      </div>

      {/* Status filter pills */}
      <div className="flex flex-wrap gap-2 mb-4">
        {["All", ...SNAG_STATUS].map(s => {
          const count = s === "All" ? snags.length : snags.filter(sn => sn.status === s).length;
          return (
            <button key={s} onClick={() => setFStatus(s)}
              className={`px-3 py-1 rounded-full text-xs font-semibold border transition-colors ${fStatus === s ? "bg-amber-500 text-white border-amber-500" : "bg-white text-slate-600 border-slate-200 hover:border-amber-300"}`}>
              {s} ({count})
            </button>
          );
        })}
      </div>

      {loading ? <Spinner /> : filtered.length === 0 ? <EmptyState msg="No snags found" onCreate={openCreate} /> : (
        <div className="space-y-3">
          {filtered.map(s => (
            <div key={s.id} className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="text-xs font-mono font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded">{s.num}</span>
                    {s.category && <Badge text={s.category} cls="bg-slate-100 text-slate-600 border-slate-200" />}
                    <span className="text-xs text-slate-400">{projects.find(p => p.id === s.pid)?.number || ""}</span>
                  </div>
                  <h3 className="font-semibold text-slate-800 mb-2 leading-tight">{s.title}</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-1 text-xs text-slate-600">
                    {[["📍 Location", s.location], ["🏗️ Sub", s.sub], ["👷 Engineer", s.engineer], ["📅 Due", fmtDate(s.due)]].map(([k, v]) => (
                      <div key={k} className={k.includes("Due") && isOverdue(s.due, s.status) ? "text-red-600 font-bold" : ""}>
                        <span className="text-slate-400">{k}: </span>{v || "—"}
                      </div>
                    ))}
                  </div>
                  {s.consultant && <div className="mt-2 text-xs bg-amber-50 border border-amber-200 text-amber-700 px-2 py-1 rounded-lg">{s.consultant}</div>}
                </div>
                <div className="flex flex-col items-end gap-2 shrink-0">
                  <Badge text={s.status} />
                  <div className="flex gap-1 text-xs">
                    {s.beforeUrl && <span className="text-green-600 font-bold bg-green-50 px-1.5 py-0.5 rounded">📷B</span>}
                    {s.afterUrl && <span className="text-green-600 font-bold bg-green-50 px-1.5 py-0.5 rounded">📷A</span>}
                  </div>
                  <div className="flex gap-1.5">
                    <ActBtn onClick={() => openView(s)} label="View" color="view" />
                    <ActBtn onClick={() => openEdit(s)} label="Edit" color="edit" />
                    <ActBtn onClick={() => setConfirmId(s.id)} label="Del" color="del" />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// DAILY REPORTS MODULE
// ─────────────────────────────────────────────────────────────────────────────
const RPT_STATUS = ["Draft", "Submitted", "Approved"];
const EMPTY_RPT = { pid: "", date: "", weather: "Sunny", temp: "", manpower: "", activities: "", completed: "", issues: "", safety: "", materials: "", preparedBy: "", status: "Draft" };

const DailyReports = ({ projects, reports, loading, onAdd, onUpdate, onDelete, showToast }) => {
  const [mode, setMode] = useState("list");
  const [sel, setSel] = useState(null);
  const [form, setForm] = useState(EMPTY_RPT);
  const [fProject, setFProject] = useState("All");
  const [saving, setSaving] = useState(false);
  const [confirmId, setConfirmId] = useState(null);
  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));

  const openCreate = () => { setForm(EMPTY_RPT); setSel(null); setMode("form"); };
  const openEdit = r => { setSel(r); setForm({ pid: r.pid, date: r.date, weather: r.weather, temp: String(r.temp || ""), manpower: String(r.manpower || ""), activities: r.activities, completed: r.completed, issues: r.issues, safety: r.safety, materials: r.materials, preparedBy: r.preparedBy, status: r.status }); setMode("form"); };
  const openView = r => { setSel(r); setMode("view"); };
  const goList = () => { setMode("list"); setSel(null); };

  const handleSave = async () => {
    if (!form.pid || !form.date) { showToast("Project and Date are required", "error"); return; }
    setSaving(true);
    const res = sel ? await onUpdate(sel.id, form) : await onAdd(form);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Save failed", "error"); return; }
    showToast(sel ? "Report updated!" : "Report saved!"); goList();
  };
  const handleDelete = async id => {
    const res = await onDelete(id);
    if (!res.ok) { showToast(res.error || "Delete failed", "error"); return; }
    showToast("Report deleted!"); setConfirmId(null); if (mode !== "list") goList();
  };

  const filtered = reports.filter(r => fProject === "All" || r.pid === fProject);

  if (mode === "view" && sel) return (
    <div className="p-6 max-w-3xl">
      {confirmId && <ConfirmDialog message="Delete this report?" onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <BackBtn onClick={goList} />
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="bg-gradient-to-r from-green-700 to-emerald-600 px-6 py-5 flex items-center justify-between">
          <div><div className="text-green-200 text-xs">{projects.find(p => p.id === sel.pid)?.number}</div><h2 className="text-xl font-bold text-white">{fmtDate(sel.date)}</h2></div>
          <Badge text={sel.status} cls="bg-white/20 text-white border-white/30" />
        </div>
        <div className="p-6 space-y-5">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="bg-blue-50 rounded-xl p-4"><div className="text-3xl font-bold text-blue-700">{sel.manpower}</div><div className="text-xs text-blue-500 mt-1">Manpower</div></div>
            <div className="bg-amber-50 rounded-xl p-4"><div className="text-xl font-bold text-amber-700">{sel.weather}</div><div className="text-xs text-amber-500 mt-1">Weather</div></div>
            <div className="bg-green-50 rounded-xl p-4"><div className="text-xl font-bold text-green-700">{sel.temp ? `${sel.temp}°C` : "—"}</div><div className="text-xs text-green-500 mt-1">Temperature</div></div>
          </div>
          {[["Work Activities", sel.activities], ["Work Completed", sel.completed], ["Issues / Delays", sel.issues], ["Safety Observations", sel.safety], ["Materials Received", sel.materials]].filter(([, v]) => v).map(([k, v]) => (
            <div key={k}><div className="text-xs text-slate-400 font-bold uppercase tracking-wide mb-1">{k}</div><p className="text-sm text-slate-700 bg-slate-50 p-3 rounded-lg leading-relaxed">{v}</p></div>
          ))}
          <div className="text-xs text-slate-400 pt-2 border-t border-slate-100">Prepared by: <strong className="text-slate-600">{sel.preparedBy || "—"}</strong></div>
          <div className="flex gap-3"><Btn onClick={() => openEdit(sel)} label="Edit Report" /><Btn onClick={() => setConfirmId(sel.id)} label="Delete" color="red" /></div>
        </div>
      </div>
    </div>
  );

  if (mode === "form") return (
    <div className="p-6 max-w-2xl">
      <BackBtn onClick={goList} />
      <h2 className="text-xl font-bold text-slate-800 mb-4">{sel ? "Edit Report" : "New Daily Report"}</h2>
      <FormCard>
        <Grid2>
          <div><Lbl t="Project" req /><Sel value={form.pid} onChange={set("pid")}><option value="">Select...</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number}</option>)}</Sel></div>
          <div><Lbl t="Date" req /><Inp type="date" value={form.date} onChange={set("date")} /></div>
          <div><Lbl t="Weather" /><Inp value={form.weather} onChange={set("weather")} placeholder="e.g. Sunny, Cloudy" /></div>
          <div><Lbl t="Temperature (°C)" /><Inp type="number" value={form.temp} onChange={set("temp")} placeholder="e.g. 38" /></div>
          <div><Lbl t="Total Manpower" /><Inp type="number" value={form.manpower} onChange={set("manpower")} placeholder="e.g. 87" /></div>
          <div><Lbl t="Prepared By" /><Inp value={form.preparedBy} onChange={set("preparedBy")} placeholder="Engineer name" /></div>
        </Grid2>
        {[["Work Activities Today", "activities"], ["Work Completed", "completed"], ["Issues / Delays", "issues"], ["Safety Observations", "safety"], ["Materials Received", "materials"]].map(([label, key]) => (
          <div key={key}><Lbl t={label} /><Txta value={form[key]} onChange={set(key)} placeholder={`Enter ${label.toLowerCase()}...`} /></div>
        ))}
        {sel && <div><Lbl t="Status" /><Sel value={form.status} onChange={set("status")}>{RPT_STATUS.map(s => <option key={s}>{s}</option>)}</Sel></div>}
        <FormActions saving={saving} onSave={handleSave} onCancel={goList} label={sel ? "Update Report" : "Save Report"} />
      </FormCard>
    </div>
  );

  return (
    <div className="p-6">
      {confirmId && <ConfirmDialog message="Delete this report permanently?" onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <PageTitle title="Daily Site Reports" count={filtered.length} btn={<AddBtn onClick={openCreate} label="New Report" />} />
      <div className="mb-4"><Sel value={fProject} onChange={e => setFProject(e.target.value)} className="w-auto"><option value="All">All Projects</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number}</option>)}</Sel></div>
      {loading ? <Spinner /> : filtered.length === 0 ? <EmptyState msg="No reports yet" onCreate={openCreate} /> : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filtered.map(r => (
            <div key={r.id} className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div><div className="font-bold text-slate-800">{fmtDate(r.date)}</div><div className="text-xs text-slate-400">{projects.find(p => p.id === r.pid)?.number || "—"}</div></div>
                <Badge text={r.status} />
              </div>
              <div className="grid grid-cols-3 gap-2 mb-3 text-center text-xs">
                <div className="bg-blue-50 rounded-lg p-2"><div className="font-bold text-blue-700 text-lg">{r.manpower}</div><div className="text-blue-500">Manpower</div></div>
                <div className="bg-amber-50 rounded-lg p-2"><div className="font-bold text-amber-700">{r.weather}</div><div className="text-amber-500">Weather</div></div>
                <div className="bg-green-50 rounded-lg p-2"><div className="font-bold text-green-700">{r.temp ? `${r.temp}°C` : "—"}</div><div className="text-green-500">Temp</div></div>
              </div>
              {r.activities && <p className="text-xs text-slate-600 mb-3 line-clamp-2">{r.activities}</p>}
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">By: <strong className="text-slate-600">{r.preparedBy || "—"}</strong></span>
                <div className="flex gap-1.5"><ActBtn onClick={() => openView(r)} label="View" color="view" /><ActBtn onClick={() => openEdit(r)} label="Edit" color="edit" /><ActBtn onClick={() => setConfirmId(r.id)} label="Del" color="del" /></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// INSPECTIONS MODULE
// ─────────────────────────────────────────────────────────────────────────────
const IR_STATUS = ["Draft", "Submitted", "Approved", "Rejected", "Resubmitted"];
const IR_TYPES = ["WIR", "MIR", "IR", "MSIR"];
const EMPTY_IR = { pid: "", type: "WIR", desc: "", location: "", trade: "", submitted: "", inspection: "", status: "Draft", remarks: "", submittedBy: "" };

const Inspections = ({ projects, inspections, loading, onAdd, onUpdate, onDelete, showToast }) => {
  const [mode, setMode] = useState("list");
  const [sel, setSel] = useState(null);
  const [form, setForm] = useState(EMPTY_IR);
  const [fStatus, setFStatus] = useState("All");
  const [fProject, setFProject] = useState("All");
  const [saving, setSaving] = useState(false);
  const [confirmId, setConfirmId] = useState(null);
  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));
  const TC = { WIR: "bg-blue-100 text-blue-700", MIR: "bg-green-100 text-green-700", IR: "bg-purple-100 text-purple-700", MSIR: "bg-orange-100 text-orange-700" };

  const openCreate = () => { setForm(EMPTY_IR); setSel(null); setMode("form"); };
  const openEdit = i => { setSel(i); setForm({ pid: i.pid, type: i.type, desc: i.desc, location: i.location, trade: i.trade, submitted: i.submitted, inspection: i.inspection, status: i.status, remarks: i.remarks, submittedBy: i.submittedBy }); setMode("form"); };
  const openView = i => { setSel(i); setMode("view"); };
  const goList = () => { setMode("list"); setSel(null); };

  const handleSave = async () => {
    if (!form.pid || !form.desc.trim()) { showToast("Project and Description required", "error"); return; }
    setSaving(true);
    const res = sel ? await onUpdate(sel.id, form) : await onAdd(form);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Save failed", "error"); return; }
    showToast(sel ? "IR updated!" : "IR submitted!"); goList();
  };
  const handleDelete = async id => {
    const res = await onDelete(id);
    if (!res.ok) { showToast(res.error || "Delete failed", "error"); return; }
    showToast("IR deleted!"); setConfirmId(null); if (mode !== "list") goList();
  };

  const filtered = inspections.filter(i => (fStatus === "All" || i.status === fStatus) && (fProject === "All" || i.pid === fProject));

  if (mode === "view" && sel) return (
    <div className="p-6 max-w-2xl">
      {confirmId && <ConfirmDialog message="Delete this inspection request?" onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <BackBtn onClick={goList} />
      <FormCard>
        <div className="flex items-start justify-between">
          <div><span className="text-xs font-mono font-bold text-amber-600">{sel.num}</span><h2 className="text-lg font-bold text-slate-800 mt-1">{sel.desc}</h2></div>
          <Badge text={sel.status} />
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          {[["Type", sel.type], ["Project", projects.find(p => p.id === sel.pid)?.number], ["Location", sel.location], ["Trade", sel.trade], ["Submitted By", sel.submittedBy], ["Submit Date", fmtDate(sel.submitted)], ["Inspection Date", fmtDate(sel.inspection)]].map(([k, v]) => (
            <div key={k}><div className="text-xs text-slate-400 font-medium">{k}</div><div className="font-semibold text-slate-800 mt-0.5">{v || "—"}</div></div>
          ))}
        </div>
        {sel.remarks && <div className="bg-slate-50 p-3 rounded-lg"><div className="text-xs text-slate-400 font-medium mb-1">Remarks</div><p className="text-sm text-slate-700">{sel.remarks}</p></div>}
        <div className="flex gap-3 pt-2"><Btn onClick={() => openEdit(sel)} label="Edit IR" /><Btn onClick={() => setConfirmId(sel.id)} label="Delete" color="red" /></div>
      </FormCard>
    </div>
  );

  if (mode === "form") return (
    <div className="p-6 max-w-2xl">
      <BackBtn onClick={goList} />
      <h2 className="text-xl font-bold text-slate-800 mb-4">{sel ? `Edit — ${sel.num}` : "New Inspection Request"}</h2>
      <FormCard>
        <Grid2>
          <div><Lbl t="Project" req /><Sel value={form.pid} onChange={set("pid")}><option value="">Select...</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number}</option>)}</Sel></div>
          <div><Lbl t="IR Type" /><Sel value={form.type} onChange={set("type")}>{IR_TYPES.map(t => <option key={t}>{t}</option>)}</Sel></div>
        </Grid2>
        <div><Lbl t="Description" req /><Txta value={form.desc} onChange={set("desc")} placeholder="Describe what is being inspected..." /></div>
        <Grid2>
          <div><Lbl t="Location" /><Inp value={form.location} onChange={set("location")} placeholder="e.g. Level 3 Zone B" /></div>
          <div><Lbl t="Trade" /><Sel value={form.trade} onChange={set("trade")}><option value="">Select...</option>{["Civil / Structural", "MEP", "Finishing", "Aluminum", "Safety", "Other"].map(t => <option key={t}>{t}</option>)}</Sel></div>
        </Grid2>
        <Grid3>
          <div><Lbl t="Submit Date" /><Inp type="date" value={form.submitted} onChange={set("submitted")} /></div>
          <div><Lbl t="Inspection Date" /><Inp type="date" value={form.inspection} onChange={set("inspection")} /></div>
          <div><Lbl t="Submitted By" /><Inp value={form.submittedBy} onChange={set("submittedBy")} placeholder="Your name" /></div>
        </Grid3>
        {sel && <div><Lbl t="Status" /><Sel value={form.status} onChange={set("status")}>{IR_STATUS.map(s => <option key={s}>{s}</option>)}</Sel></div>}
        <div><Lbl t="Remarks" /><Txta value={form.remarks} onChange={set("remarks")} rows={2} placeholder="Consultant remarks..." /></div>
        <FormActions saving={saving} onSave={handleSave} onCancel={goList} label={sel ? "Update IR" : "Submit IR"} />
      </FormCard>
    </div>
  );

  return (
    <div className="p-6">
      {confirmId && <ConfirmDialog message="Delete this inspection request?" onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <PageTitle title="Inspection Requests" count={filtered.length} btn={<AddBtn onClick={openCreate} label="New IR / WIR" />} />
      <div className="flex flex-wrap gap-3 mb-3">
        <Sel value={fProject} onChange={e => setFProject(e.target.value)} className="w-auto"><option value="All">All Projects</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number}</option>)}</Sel>
      </div>
      <div className="flex flex-wrap gap-2 mb-4">{["All", ...IR_STATUS].map(s => <button key={s} onClick={() => setFStatus(s)} className={`px-3 py-1 rounded-full text-xs font-semibold border transition-colors ${fStatus === s ? "bg-amber-500 text-white border-amber-500" : "bg-white text-slate-600 border-slate-200 hover:border-amber-300"}`}>{s} ({s === "All" ? inspections.length : inspections.filter(i => i.status === s).length})</button>)}</div>
      {loading ? <Spinner /> : filtered.length === 0 ? <EmptyState msg="No inspections found" onCreate={openCreate} /> : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>{["IR Number", "Type", "Description", "Project", "Submitted", "Status", "Actions"].map(h => <th key={h} className="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase tracking-wide whitespace-nowrap">{h}</th>)}</tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map(i => (
                <tr key={i.id} className="hover:bg-amber-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs font-bold text-amber-700">{i.num}</td>
                  <td className="px-4 py-3"><span className={`text-xs font-bold px-2 py-0.5 rounded-full ${TC[i.type] || "bg-slate-100 text-slate-600"}`}>{i.type}</span></td>
                  <td className="px-4 py-3 text-xs text-slate-700 max-w-[200px] truncate">{i.desc}</td>
                  <td className="px-4 py-3 text-xs text-slate-500">{projects.find(p => p.id === i.pid)?.number || "—"}</td>
                  <td className="px-4 py-3 text-xs text-slate-600 whitespace-nowrap">{fmtDate(i.submitted)}</td>
                  <td className="px-4 py-3"><Badge text={i.status} /></td>
                  <td className="px-4 py-3"><div className="flex gap-1.5"><ActBtn onClick={() => openView(i)} label="View" color="view" /><ActBtn onClick={() => openEdit(i)} label="Edit" color="edit" /><ActBtn onClick={() => setConfirmId(i.id)} label="Del" color="del" /></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// DRAWINGS MODULE
// ─────────────────────────────────────────────────────────────────────────────
const DISC = ["Architectural", "Structural", "MEP", "Civil"];
const EMPTY_DWG = { pid: "", num: "", title: "", rev: "A", discipline: "", received: "", remarks: "", fileUrl: "", file: null };

const Drawings = ({ projects, drawings, loading, onAdd, onUpdate, onDelete, showToast }) => {
  const [mode, setMode] = useState("list");
  const [sel, setSel] = useState(null);
  const [form, setForm] = useState(EMPTY_DWG);
  const [search, setSearch] = useState("");
  const [fDisc, setFDisc] = useState("All");
  const [fProject, setFProject] = useState("All");
  const [saving, setSaving] = useState(false);
  const [confirmId, setConfirmId] = useState(null);
  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));

  const openCreate = () => { setForm(EMPTY_DWG); setSel(null); setMode("form"); };
  const openEdit = d => { setSel(d); setForm({ pid: d.pid, num: d.num, title: d.title, rev: d.rev, discipline: d.discipline, received: d.received, remarks: d.remarks, fileUrl: d.fileUrl, file: null }); setMode("form"); };
  const openView = d => { setSel(d); setMode("view"); };
  const goList = () => { setMode("list"); setSel(null); };

  const handleSave = async () => {
    if (!form.pid || !form.num.trim() || !form.title.trim()) { showToast("Project, Number and Title required", "error"); return; }
    setSaving(true);
    const res = sel ? await onUpdate(sel.id, form) : await onAdd(form);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Save failed", "error"); return; }
    showToast(sel ? "Drawing updated!" : "Drawing added!"); goList();
  };
  const handleDelete = async id => {
    const res = await onDelete(id);
    if (!res.ok) { showToast(res.error || "Delete failed", "error"); return; }
    showToast("Drawing deleted!"); setConfirmId(null); if (mode !== "list") goList();
  };

  const filtered = drawings.filter(d => (fDisc === "All" || d.discipline === fDisc) && (fProject === "All" || d.pid === fProject) && (!search || `${d.num} ${d.title}`.toLowerCase().includes(search.toLowerCase())));

  if (mode === "view" && sel) return (
    <div className="p-6 max-w-2xl">
      {confirmId && <ConfirmDialog message="Delete this drawing?" onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <BackBtn onClick={goList} />
      <FormCard>
        <div className="flex items-start justify-between"><div><div className="font-mono text-sm font-bold text-slate-700">{sel.num}</div><h2 className="text-lg font-bold text-slate-800 mt-1">{sel.title}</h2></div><span className="font-mono text-xs font-bold bg-amber-100 text-amber-700 px-2 py-1 rounded-lg">Rev {sel.rev}</span></div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          {[["Discipline", sel.discipline], ["Project", projects.find(p => p.id === sel.pid)?.number], ["Date Received", fmtDate(sel.received)], ["Status", sel.latest ? "Current" : "Superseded"]].map(([k, v]) => (
            <div key={k}><div className="text-xs text-slate-400 font-medium">{k}</div><div className="font-semibold text-slate-800 mt-0.5">{v || "—"}</div></div>
          ))}
        </div>
        {sel.remarks && <div className="bg-slate-50 p-3 rounded-lg text-sm text-slate-700">{sel.remarks}</div>}
        {sel.fileUrl && <a href={sel.fileUrl} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold text-sm px-4 py-2 rounded-lg transition-colors"><Icon name="eye" cls="w-4 h-4" />Open Drawing File</a>}
        <div className="flex gap-3 pt-2"><Btn onClick={() => openEdit(sel)} label="Edit Drawing" /><Btn onClick={() => setConfirmId(sel.id)} label="Delete" color="red" /></div>
      </FormCard>
    </div>
  );

  if (mode === "form") return (
    <div className="p-6 max-w-2xl">
      <BackBtn onClick={goList} />
      <h2 className="text-xl font-bold text-slate-800 mb-4">{sel ? "Edit Drawing" : "Add Drawing"}</h2>
      <FormCard>
        <div><Lbl t="Project" req /><Sel value={form.pid} onChange={set("pid")}><option value="">Select...</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number}</option>)}</Sel></div>
        <Grid2>
          <div><Lbl t="Drawing Number" req /><Inp value={form.num} onChange={set("num")} placeholder="e.g. AGBC-001-AR-001" /></div>
          <div><Lbl t="Revision" /><Inp value={form.rev} onChange={set("rev")} placeholder="e.g. A" /></div>
        </Grid2>
        <div><Lbl t="Drawing Title" req /><Inp value={form.title} onChange={set("title")} placeholder="e.g. Ground Floor Plan" /></div>
        <Grid2>
          <div><Lbl t="Discipline" /><Sel value={form.discipline} onChange={set("discipline")}><option value="">Select...</option>{DISC.map(d => <option key={d}>{d}</option>)}</Sel></div>
          <div><Lbl t="Date Received" /><Inp type="date" value={form.received} onChange={set("received")} /></div>
        </Grid2>
        <div><Lbl t="Remarks" /><Txta value={form.remarks} onChange={set("remarks")} rows={2} placeholder="Any remarks..." /></div>
        <div>
          <Lbl t="Drawing File (PDF / DWG / Image)" />
          <Inp type="file" accept=".pdf,.dwg,.dxf,.jpg,.jpeg,.png" onChange={e => setForm(p => ({ ...p, file: e.target.files[0] }))} />
          <p className="text-xs text-slate-400 mt-1">Accepts: PDF, DWG, DXF, JPG, PNG</p>
          {form.fileUrl && !form.file && <a href={form.fileUrl} target="_blank" rel="noreferrer" className="text-xs text-blue-600 mt-1 inline-flex items-center gap-1 hover:underline"><Icon name="eye" cls="w-3 h-3" />Current file attached — click to view</a>}
          {form.file && <p className="text-xs text-green-600 mt-1">✓ New file selected: {form.file.name}</p>}
        </div>
        <FormActions saving={saving} onSave={handleSave} onCancel={goList} label={sel ? "Update Drawing" : "Save Drawing"} />
      </FormCard>
    </div>
  );

  return (
    <div className="p-6">
      {confirmId && <ConfirmDialog message="Delete this drawing?" onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <PageTitle title="Drawing Register" count={filtered.length} btn={<AddBtn onClick={openCreate} label="Add Drawing" />} />
      <div className="flex flex-wrap gap-3 mb-4">
        <SearchBar value={search} onChange={e => setSearch(e.target.value)} placeholder="Search drawings..." />
        <Sel value={fProject} onChange={e => setFProject(e.target.value)} className="w-auto"><option value="All">All Projects</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number}</option>)}</Sel>
        <div className="flex gap-1">{["All", ...DISC].map(d => <button key={d} onClick={() => setFDisc(d)} className={`px-3 py-2 text-xs font-semibold rounded-lg border transition-colors ${fDisc === d ? "bg-amber-500 text-white border-amber-500" : "bg-white border-slate-200 text-slate-600 hover:border-amber-300"}`}>{d}</button>)}</div>
      </div>
      {loading ? <Spinner /> : filtered.length === 0 ? <EmptyState msg="No drawings found" onCreate={openCreate} /> : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>{["Drawing No.", "Title", "Discipline", "Rev", "Project", "Date", "File", "Actions"].map(h => <th key={h} className="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase tracking-wide">{h}</th>)}</tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map(d => (
                <tr key={d.id} className="hover:bg-amber-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs font-bold text-slate-700">{d.num}</td>
                  <td className="px-4 py-3 text-sm font-medium text-slate-800 max-w-[180px] truncate">{d.title}</td>
                  <td className="px-4 py-3"><span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${DC[d.discipline] || "bg-slate-100 text-slate-600"}`}>{d.discipline || "—"}</span></td>
                  <td className="px-4 py-3"><span className="font-mono text-xs font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded">Rev {d.rev}</span></td>
                  <td className="px-4 py-3 text-xs text-slate-500">{projects.find(p => p.id === d.pid)?.number || "—"}</td>
                  <td className="px-4 py-3 text-xs text-slate-600">{fmtDate(d.received)}</td>
                  <td className="px-4 py-3">{d.fileUrl ? <a href={d.fileUrl} target="_blank" rel="noreferrer" className="text-xs text-blue-600 font-semibold hover:underline flex items-center gap-1"><Icon name="eye" cls="w-3.5 h-3.5" />View</a> : <span className="text-xs text-slate-300">No file</span>}</td>
                  <td className="px-4 py-3"><div className="flex gap-1.5"><ActBtn onClick={() => openView(d)} label="View" color="view" /><ActBtn onClick={() => openEdit(d)} label="Edit" color="edit" /><ActBtn onClick={() => setConfirmId(d.id)} label="Del" color="del" /></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// PHOTOS MODULE — Full CRUD + Lightbox
// ─────────────────────────────────────────────────────────────────────────────
const EMPTY_PHOTO_UPLOAD = { pid: "", caption: "", area: "", file: null };
const EMPTY_PHOTO_EDIT = { pid: "", caption: "", area: "" };

const Photos = ({ projects, photos, loading, onAdd, onUpdate, onDelete, showToast }) => {
  const [mode, setMode] = useState("list"); // list | upload | edit
  const [sel, setSel] = useState(null);
  const [lightbox, setLightbox] = useState(null);
  const [uploadForm, setUploadForm] = useState(EMPTY_PHOTO_UPLOAD);
  const [editForm, setEditForm] = useState(EMPTY_PHOTO_EDIT);
  const [fProject, setFProject] = useState("All");
  const [saving, setSaving] = useState(false);
  const [confirmId, setConfirmId] = useState(null);

  const openEdit = p => { setSel(p); setEditForm({ pid: p.project_id, caption: p.caption || "", area: p.area || "" }); setMode("edit"); };
  const goList = () => { setMode("list"); setSel(null); };

  const handleUpload = async () => {
    if (!uploadForm.file || !uploadForm.pid) { showToast("Please select a project and photo", "error"); return; }
    setSaving(true);
    const res = await onAdd(uploadForm);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Upload failed", "error"); return; }
    showToast("Photo uploaded successfully!"); setMode("list"); setUploadForm(EMPTY_PHOTO_UPLOAD);
  };

  const handleUpdate = async () => {
    setSaving(true);
    const res = await onUpdate(sel.id, editForm);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Update failed", "error"); return; }
    showToast("Photo details updated!"); goList();
  };

  const handleDelete = async id => {
    const res = await onDelete(id);
    if (!res.ok) { showToast(res.error || "Delete failed", "error"); return; }
    showToast("Photo deleted!"); setConfirmId(null);
  };

  const filtered = photos.filter(p => fProject === "All" || p.project_id === fProject);

  // Lightbox
  if (lightbox) return (
    <div className="fixed inset-0 bg-black/90 z-[999] flex items-center justify-center p-4" onClick={() => setLightbox(null)}>
      <div className="max-w-5xl w-full space-y-3" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between">
          <div><p className="text-white font-semibold">{lightbox.caption || "No caption"}</p><p className="text-slate-400 text-sm">{lightbox.area} · {projects.find(p => p.id === lightbox.project_id)?.number}</p></div>
          <button onClick={() => setLightbox(null)} className="text-white text-4xl leading-none hover:text-red-400 transition-colors">×</button>
        </div>
        <img src={lightbox.file_url} alt={lightbox.caption} className="max-h-[80vh] max-w-full mx-auto rounded-xl object-contain" />
      </div>
    </div>
  );

  // Upload form
  if (mode === "upload") return (
    <div className="p-6 max-w-lg">
      <BackBtn onClick={goList} />
      <h2 className="text-xl font-bold text-slate-800 mb-4">Upload Progress Photo</h2>
      <FormCard>
        <div><Lbl t="Project" req /><Sel value={uploadForm.pid} onChange={e => setUploadForm(p => ({ ...p, pid: e.target.value }))}><option value="">Select Project...</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}</Sel></div>
        <div><Lbl t="Caption" /><Inp value={uploadForm.caption} onChange={e => setUploadForm(p => ({ ...p, caption: e.target.value }))} placeholder="e.g. Grade slab pour — Block A" /></div>
        <div><Lbl t="Area / Location" /><Inp value={uploadForm.area} onChange={e => setUploadForm(p => ({ ...p, area: e.target.value }))} placeholder="e.g. Ground Floor Block A" /></div>
        <div>
          <Lbl t="Photo" req />
          <Inp type="file" accept="image/*" onChange={e => setUploadForm(p => ({ ...p, file: e.target.files[0] }))} />
          {uploadForm.file && <p className="text-xs text-green-600 mt-1">✓ Selected: {uploadForm.file.name}</p>}
        </div>
        <FormActions saving={saving} onSave={handleUpload} onCancel={goList} label="Upload Photo" />
      </FormCard>
    </div>
  );

  // Edit form
  if (mode === "edit" && sel) return (
    <div className="p-6 max-w-lg">
      <BackBtn onClick={goList} />
      <h2 className="text-xl font-bold text-slate-800 mb-4">Edit Photo Details</h2>
      <FormCard>
        <div className="h-52 bg-slate-100 rounded-xl overflow-hidden">
          <img src={sel.file_url} alt="" className="w-full h-full object-cover" />
        </div>
        <div><Lbl t="Project" /><Sel value={editForm.pid} onChange={e => setEditForm(p => ({ ...p, pid: e.target.value }))}><option value="">Select...</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}</Sel></div>
        <div><Lbl t="Caption" /><Inp value={editForm.caption} onChange={e => setEditForm(p => ({ ...p, caption: e.target.value }))} placeholder="e.g. Grade slab pour — Block A" /></div>
        <div><Lbl t="Area / Location" /><Inp value={editForm.area} onChange={e => setEditForm(p => ({ ...p, area: e.target.value }))} placeholder="e.g. Ground Floor" /></div>
        <FormActions saving={saving} onSave={handleUpdate} onCancel={goList} label="Update Photo" />
      </FormCard>
    </div>
  );

  // List
  return (
    <div className="p-6">
      {confirmId && <ConfirmDialog message="Delete this photo permanently?" onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <PageTitle title="Progress Photos" count={filtered.length} btn={<AddBtn onClick={() => setMode("upload")} label="Upload Photos" />} />
      <div className="mb-4"><Sel value={fProject} onChange={e => setFProject(e.target.value)} className="w-auto"><option value="All">All Projects</option>{projects.map(p => <option key={p.id} value={p.id}>{p.number}</option>)}</Sel></div>
      {loading ? <Spinner /> : filtered.length === 0 ? <EmptyState msg="No photos yet" onCreate={() => setMode("upload")} /> : (
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map(p => (
            <div key={p.id} className="bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-lg transition-shadow group">
              <div className="h-44 bg-slate-100 relative overflow-hidden cursor-pointer" onClick={() => setLightbox(p)}>
                <img src={p.file_url} alt={p.caption} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all flex items-center justify-center">
                  <Icon name="eye" cls="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
              <div className="p-3">
                <div className="text-xs font-semibold text-slate-700 mb-0.5 leading-tight">{p.caption || "No caption"}</div>
                <div className="text-xs text-slate-400">{p.area}</div>
                <div className="text-xs text-slate-400">{projects.find(pr => pr.id === p.project_id)?.number || ""} · {fmtDate(p.uploaded_at?.split("T")[0])}</div>
                <div className="flex gap-1.5 mt-2">
                  <ActBtn onClick={() => setLightbox(p)} label="View" color="view" />
                  <ActBtn onClick={() => openEdit(p)} label="Edit" color="edit" />
                  <ActBtn onClick={() => setConfirmId(p.id)} label="Del" color="del" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// SUBCONTRACTORS MODULE — Full CRUD
// ─────────────────────────────────────────────────────────────────────────────
const EMPTY_SUB = { name: "", contact: "", phone: "", email: "", tradesInput: "", trades: [], notes: "", active: true };

const Subcontractors = ({ subs, loading, onAdd, onUpdate, onDelete, showToast }) => {
  const [mode, setMode] = useState("list");
  const [sel, setSel] = useState(null);
  const [form, setForm] = useState(EMPTY_SUB);
  const [search, setSearch] = useState("");
  const [saving, setSaving] = useState(false);
  const [confirmId, setConfirmId] = useState(null);
  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));

  const openCreate = () => { setForm(EMPTY_SUB); setSel(null); setMode("form"); };
  const openEdit = s => { setSel(s); setForm({ name: s.name, contact: s.contact, phone: s.phone, email: s.email, trades: s.trades || [], tradesInput: (s.trades || []).join(", "), notes: s.notes, active: s.active }); setMode("form"); };
  const openView = s => { setSel(s); setMode("view"); };
  const goList = () => { setMode("list"); setSel(null); };

  const handleSave = async () => {
    if (!form.name.trim()) { showToast("Company name is required", "error"); return; }
    const trades = form.tradesInput.split(",").map(t => t.trim()).filter(Boolean);
    setSaving(true);
    const res = sel ? await onUpdate(sel.id, { ...form, trades }) : await onAdd({ ...form, trades });
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Save failed", "error"); return; }
    showToast(sel ? "Subcontractor updated!" : "Subcontractor added!"); goList();
  };
  const handleDelete = async id => {
    const res = await onDelete(id);
    if (!res.ok) { showToast(res.error || "Delete failed", "error"); return; }
    showToast("Subcontractor deleted!"); setConfirmId(null); if (mode !== "list") goList();
  };

  const filtered = subs.filter(s => `${s.name} ${s.contact} ${s.email} ${(s.trades || []).join(" ")}`.toLowerCase().includes(search.toLowerCase()));

  if (mode === "view" && sel) return (
    <div className="p-6 max-w-2xl">
      {confirmId && <ConfirmDialog message={`Delete "${sel.name}"?`} onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <BackBtn onClick={goList} />
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="bg-gradient-to-r from-slate-700 to-slate-600 px-6 py-5">
          <div className="flex items-start justify-between">
            <div><h2 className="text-xl font-bold text-white">{sel.name}</h2><p className="text-slate-300 text-sm mt-1">{sel.contact}</p></div>
            <span className={`px-3 py-1 text-xs font-bold rounded-full border ${sel.active ? "bg-green-400/20 text-green-300 border-green-400/30" : "bg-slate-400/20 text-slate-300 border-slate-400/30"}`}>{sel.active ? "Active" : "Inactive"}</span>
          </div>
        </div>
        <div className="p-6 space-y-5">
          <Grid2>
            <div><div className="text-xs text-slate-400 font-medium">Phone</div><div className="font-semibold text-slate-800 mt-0.5">{sel.phone || "—"}</div></div>
            <div><div className="text-xs text-slate-400 font-medium">Email</div><div className="font-semibold text-slate-800 mt-0.5">{sel.email || "—"}</div></div>
          </Grid2>
          <div>
            <div className="text-xs text-slate-400 font-medium mb-2">Trades & Specializations</div>
            <div className="flex flex-wrap gap-2">{(sel.trades || []).length > 0 ? sel.trades.map((t, i) => <span key={i} className="bg-amber-50 border border-amber-200 text-amber-700 text-xs font-semibold px-3 py-1 rounded-full">{t}</span>) : <span className="text-slate-400 text-sm">No trades listed</span>}</div>
          </div>
          {sel.notes && <div><div className="text-xs text-slate-400 font-medium mb-1">Performance Notes</div><p className="text-sm text-slate-700 bg-slate-50 p-3 rounded-lg leading-relaxed">{sel.notes}</p></div>}
          <div className="flex gap-3 pt-2 border-t border-slate-100"><Btn onClick={() => openEdit(sel)} label="Edit" /><Btn onClick={() => setConfirmId(sel.id)} label="Delete" color="red" /></div>
        </div>
      </div>
    </div>
  );

  if (mode === "form") return (
    <div className="p-6 max-w-lg">
      <BackBtn onClick={goList} />
      <h2 className="text-xl font-bold text-slate-800 mb-4">{sel ? "Edit Subcontractor" : "Add Subcontractor"}</h2>
      <FormCard>
        <div><Lbl t="Company Name" req /><Inp value={form.name} onChange={set("name")} placeholder="e.g. Al Futtaim MEP LLC" /></div>
        <div><Lbl t="Contact Person" /><Inp value={form.contact} onChange={set("contact")} placeholder="Contact name" /></div>
        <Grid2>
          <div><Lbl t="Phone" /><Inp value={form.phone} onChange={set("phone")} placeholder="+971-50-..." /></div>
          <div><Lbl t="Email" /><Inp value={form.email} onChange={set("email")} placeholder="email@company.com" /></div>
        </Grid2>
        <div><Lbl t="Trades (comma separated)" /><Inp value={form.tradesInput} onChange={set("tradesInput")} placeholder="e.g. MEP, HVAC, Plumbing, Electrical" /></div>
        <div><Lbl t="Performance Notes" /><Txta value={form.notes} onChange={set("notes")} rows={3} placeholder="Any notes about this subcontractor's performance..." /></div>
        {sel && <div><Lbl t="Status" /><Sel value={form.active ? "Active" : "Inactive"} onChange={e => setForm(p => ({ ...p, active: e.target.value === "Active" }))}><option>Active</option><option>Inactive</option></Sel></div>}
        <FormActions saving={saving} onSave={handleSave} onCancel={goList} label={sel ? "Update Subcontractor" : "Save Subcontractor"} />
      </FormCard>
    </div>
  );

  return (
    <div className="p-6">
      {confirmId && <ConfirmDialog message="Delete this subcontractor?" onConfirm={() => handleDelete(confirmId)} onCancel={() => setConfirmId(null)} />}
      <PageTitle title="Subcontractors" count={filtered.length} btn={<AddBtn onClick={openCreate} label="Add Subcontractor" />} />
      <div className="mb-4"><SearchBar value={search} onChange={e => setSearch(e.target.value)} placeholder="Search subcontractors..." /></div>
      {loading ? <Spinner /> : filtered.length === 0 ? <EmptyState msg="No subcontractors found" onCreate={openCreate} /> : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          {filtered.map(s => (
            <div key={s.id} className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between gap-3 mb-3">
                <div><div className="font-bold text-slate-800">{s.name}</div><div className="text-xs text-slate-500 mt-0.5">{s.contact}</div></div>
                <span className={`px-2 py-0.5 text-xs font-bold rounded-full border shrink-0 ${s.active ? "bg-green-100 text-green-700 border-green-200" : "bg-slate-100 text-slate-500 border-slate-200"}`}>{s.active ? "Active" : "Inactive"}</span>
              </div>
              <div className="flex flex-wrap gap-1 mb-3">{(s.trades || []).map((t, i) => <span key={i} className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">{t}</span>)}</div>
              <div className="flex items-center justify-between">
                <div className="text-xs text-slate-500 space-y-0.5"><div>{s.phone}</div><div className="truncate max-w-[160px]">{s.email}</div></div>
                <div className="flex gap-1.5"><ActBtn onClick={() => openView(s)} label="View" color="view" /><ActBtn onClick={() => openEdit(s)} label="Edit" color="edit" /><ActBtn onClick={() => setConfirmId(s.id)} label="Del" color="del" /></div>
              </div>
              {s.notes && <div className="mt-2 text-xs text-slate-500 bg-slate-50 px-3 py-2 rounded-lg border border-slate-100 line-clamp-2">{s.notes}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────────
// APP ROOT
// ─────────────────────────────────────────────────────────────────────────────
const PAGE_TITLES = {
  dashboard: "Dashboard", projects: "Projects", tasks: "Task Management",
  snags: "Snag / Punch List", reports: "Daily Site Reports",
  inspections: "Inspection Request Tracker", drawings: "Drawing Register",
  photos: "Progress Photos", subcontractors: "Subcontractors",
};

export default function App() {
  const { user, loading: authLoading } = useAuth();
  const { projects, loading: plLoad, add: addP, update: updP, remove: delP } = useProjects();
  const { tasks, loading: tlLoad, add: addT, update: updT, remove: delT } = useTasks();
  const { snags, loading: slLoad, add: addS, update: updS, remove: delS } = useSnags();
  const { reports, loading: rlLoad, add: addR, update: updR, remove: delR } = useDailyReports();
  const { inspections, loading: ilLoad, add: addI, update: updI, remove: delI } = useInspections();
  const { drawings, loading: dlLoad, add: addD, update: updD, remove: delD } = useDrawings();
  const { subs, loading: sbLoad, add: addSub, update: updSub, remove: delSub } = useSubcontractors();
  const { photos, loading: phLoad, add: addPh, update: updPh, remove: delPh } = usePhotos();

  const { toast, showToast, hideToast } = useToast();
  const [page, setPage] = useState("dashboard");
  const [collapsed, setCollapsed] = useState(false);

  if (authLoading) return (
    <div className="flex h-screen items-center justify-center bg-slate-50">
      <div className="text-center space-y-3">
        <div className="w-12 h-12 border-4 border-amber-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-sm text-slate-500 font-medium">Loading AGBC...</p>
      </div>
    </div>
  );

  if (!user) return <Login onLogin={() => {}} />;

  const pp = { projects, showToast };

  const renderPage = () => {
    switch (page) {
      case "dashboard":      return <Dashboard projects={projects} tasks={tasks} snags={snags} inspections={inspections} reports={reports} />;
      case "projects":       return <Projects {...pp} loading={plLoad} onAdd={addP} onUpdate={updP} onDelete={delP} />;
      case "tasks":          return <Tasks {...pp} tasks={tasks} loading={tlLoad} onAdd={addT} onUpdate={updT} onDelete={delT} />;
      case "snags":          return <Snags {...pp} snags={snags} loading={slLoad} onAdd={addS} onUpdate={updS} onDelete={delS} />;
      case "reports":        return <DailyReports {...pp} reports={reports} loading={rlLoad} onAdd={addR} onUpdate={updR} onDelete={delR} />;
      case "inspections":    return <Inspections {...pp} inspections={inspections} loading={ilLoad} onAdd={addI} onUpdate={updI} onDelete={delI} />;
      case "drawings":       return <Drawings {...pp} drawings={drawings} loading={dlLoad} onAdd={addD} onUpdate={updD} onDelete={delD} />;
      case "photos":         return <Photos {...pp} photos={photos} loading={phLoad} onAdd={addPh} onUpdate={updPh} onDelete={delPh} />;
      case "subcontractors": return <Subcontractors subs={subs} loading={sbLoad} onAdd={addSub} onUpdate={updSub} onDelete={delSub} showToast={showToast} />;
      default: return <div className="p-12 text-center text-slate-400 text-lg font-semibold">Module coming soon</div>;
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans text-slate-800">
      <style>{`
        * { box-sizing: border-box; }
        body { margin: 0; font-family: 'Inter', system-ui, -apple-system, sans-serif; }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 99px; }
        .line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
      `}</style>
      {toast && <Toast message={toast.message} type={toast.type} onClose={hideToast} />}
      <Sidebar active={page} onNav={setPage} collapsed={collapsed} user={user} onSignOut={() => supabase.auth.signOut()} />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header title={PAGE_TITLES[page] || "AGBC"} onToggle={() => setCollapsed(c => !c)} user={user} />
        <main className="flex-1 overflow-y-auto">{renderPage()}</main>
      </div>
    </div>
  );
}