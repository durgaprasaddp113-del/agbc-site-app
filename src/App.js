import { useState, useEffect } from "react";
import { supabase } from "./supabase";
import Login from "./Login";

function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_e, session) => {
      setUser(session?.user ?? null);
    });
    return () => subscription.unsubscribe();
  }, []);
  return { user, loading };
}

function useProjects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    supabase.from("projects").select("*").order("project_number").then(({ data, error }) => {
      if (error) console.error("Projects error:", error);
      if (data) setProjects(data.map(p => ({
        id: p.id, number: p.project_number, name: p.project_name,
        plot: p.plot_number, location: p.location,
        plotArea: p.plot_area_sqft, bua: p.bua_sqft,
        duration: p.duration_months, consultant: p.consultant_name,
        status: p.status || "Active", mapUrl: p.map_url,
        progress: 0, openTasks: 0, openSnags: 0, pendingIR: 0,
      })));
      setLoading(false);
    });
  }, []);
  return { projects, loading };
}

function useTasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const fetchTasks = async () => {
    const { data, error } = await supabase.from("tasks").select("*").order("created_at", { ascending: false });
    if (error) console.error("Tasks error:", error);
    if (data) setTasks(data.map(t => ({
      id: t.id, pid: t.project_id, title: t.title, desc: t.description || "",
      location: t.location || "", trade: t.trade || "",
      assignee: t.assignee_name || "Unassigned",
      priority: t.priority || "Medium", status: t.status || "Open",
      due: t.due_date || null,
    })));
    setLoading(false);
  };
  useEffect(() => { fetchTasks(); }, []);
  const addTask = async (form) => {
    const { error } = await supabase.from("tasks").insert([{
      project_id: form.project_id, title: form.title, description: form.description,
      location: form.location, trade: form.trade, assignee_name: form.assignee,
      priority: form.priority, status: "Open", due_date: form.due_date,
    }]);
    if (error) { console.error("Add task error:", error); return false; }
    await fetchTasks(); return true;
  };
  const updateTaskStatus = async (taskId, newStatus) => {
    const { error } = await supabase.from("tasks").update({ status: newStatus }).eq("id", taskId);
    if (error) return false;
    await fetchTasks(); return true;
  };
  return { tasks, loading, addTask, updateTaskStatus };
}

function useSnags() {
  const [snags, setSnags] = useState([]);
  const [loading, setLoading] = useState(true);
  const fetchSnags = async () => {
    const { data, error } = await supabase.from("snag_items").select("*").order("created_at", { ascending: false });
    if (error) console.error("Snags error:", error);
    if (data) setSnags(data.map(s => ({
      id: s.id, pid: s.project_id, num: s.snag_number, title: s.title,
      desc: s.description || "", location: s.location || "", category: s.category || "",
      sub: s.responsible_sub_name || "", engineer: s.assigned_engineer_name || "",
      due: s.due_date || null, status: s.status || "Open",
      before: !!s.before_photo_url, after: !!s.after_photo_url,
      consultant: s.consultant_comment || "",
    })));
    setLoading(false);
  };
  useEffect(() => { fetchSnags(); }, []);
  const addSnag = async (form) => {
    const { data: existing } = await supabase.from("snag_items").select("snag_number").order("created_at", { ascending: false }).limit(1);
    const lastNum = existing?.[0]?.snag_number || "SNF-000";
    const nextNum = "SNF-" + String(parseInt(lastNum.split("-")[1]) + 1).padStart(3, "0");
    const { error } = await supabase.from("snag_items").insert([{
      snag_number: nextNum, project_id: form.project_id, title: form.title,
      description: form.description, location: form.location, category: form.category,
      responsible_sub_name: form.sub, assigned_engineer_name: form.engineer,
      due_date: form.due_date, status: "Open",
    }]);
    if (error) { console.error("Add snag error:", error); return false; }
    await fetchSnags(); return true;
  };
  const updateSnagStatus = async (snagId, newStatus) => {
    const { error } = await supabase.from("snag_items").update({ status: newStatus }).eq("id", snagId);
    if (error) return false;
    await fetchSnags(); return true;
  };
  return { snags, loading, addSnag, updateSnagStatus };
}

function useDailyReports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const fetchReports = async () => {
    const { data, error } = await supabase.from("daily_reports").select("*").order("report_date", { ascending: false });
    if (error) console.error("Reports error:", error);
    if (data) setReports(data.map(r => ({
      id: r.id, pid: r.project_id, date: r.report_date,
      weather: r.weather || "", temp: r.temperature_high ? r.temperature_high + "C" : "",
      manpower: r.manpower_total || 0, activities: r.work_activities || "",
      status: r.status || "Draft", preparedBy: r.prepared_by_name || "",
    })));
    setLoading(false);
  };
  useEffect(() => { fetchReports(); }, []);
  const addReport = async (form) => {
    const { error } = await supabase.from("daily_reports").insert([{
      project_id: form.project_id, report_date: form.report_date,
      weather: form.weather, temperature_high: parseInt(form.temperature) || null,
      manpower_total: parseInt(form.manpower) || 0,
      work_activities: form.activities, work_completed: form.completed,
      issues_delays: form.issues, status: "Draft",
      prepared_by_name: form.preparedBy,
    }]);
    if (error) { console.error("Add report error:", error); return false; }
    await fetchReports(); return true;
  };
  return { reports, loading, addReport };
}

const INSPECTIONS = [
  { id:"ir1", pid:"p1", num:"WIR/AGBC/001/25", type:"WIR", desc:"Reinforcement inspection — Grade Slab Block A", location:"Ground Floor", submitted:"2025-01-20", inspection:"2025-01-22", status:"Approved", remarks:"Approved with minor comment" },
  { id:"ir2", pid:"p1", num:"WIR/AGBC/002/25", type:"WIR", desc:"Blockwork inspection — Level 3", location:"Level 3", submitted:"2025-01-23", inspection:"2025-01-27", status:"Submitted", remarks:"" },
  { id:"ir3", pid:"p2", num:"WIR/AGBC/003/25", type:"WIR", desc:"First fix MEP inspection — Level 3", location:"Level 3", submitted:"2025-01-25", inspection:"2025-01-30", status:"Rejected", remarks:"Incomplete conduit installation" },
];

const DRAWINGS = [
  { id:"d1", pid:"p1", num:"AGBC-001-AR-001", title:"Ground Floor Plan", rev:"C", discipline:"Architectural", received:"2024-11-10", latest:true },
  { id:"d2", pid:"p1", num:"AGBC-001-ST-001", title:"Foundation Layout Plan", rev:"D", discipline:"Structural", received:"2024-12-01", latest:true },
  { id:"d3", pid:"p1", num:"AGBC-001-ME-001", title:"HVAC Ductwork Layout", rev:"A", discipline:"MEP", received:"2025-01-05", latest:true },
  { id:"d4", pid:"p2", num:"AGBC-002-AR-001", title:"Ground Floor Plan", rev:"B", discipline:"Architectural", received:"2024-09-15", latest:true },
];

const SUBCONTRACTORS = [
  { id:"sub1", name:"Al Futtaim MEP", contact:"Khalid Al Rashidi", phone:"+971-50-1234567", email:"khalid@alfuttaim.ae", trades:["MEP","HVAC","Plumbing"], active:true, projects:2, openTasks:5, openSnags:2 },
  { id:"sub2", name:"Green Emirates Contracting", contact:"Suresh Kumar", phone:"+971-55-9876543", email:"suresh@greenuae.com", trades:["Civil","Masonry","Plastering"], active:true, projects:2, openTasks:3, openSnags:3 },
  { id:"sub3", name:"Gulf Tile & Marble", contact:"Praveen Nair", phone:"+971-50-5551234", email:"praveen@gulftile.com", trades:["Tiling","Marble","Flooring"], active:true, projects:1, openTasks:2, openSnags:1 },
  { id:"sub4", name:"Al Madina Aluminum", contact:"Mohammed Al Balushi", phone:"+971-56-7778899", email:"info@almadina-al.com", trades:["Aluminum","Glazing","Cladding"], active:true, projects:2, openTasks:4, openSnags:1 },
];

const fmtNum = (n) => n ? Number(n).toLocaleString("en-US", { maximumFractionDigits: 0 }) : "—";
const fmtDate = (d) => d ? new Date(d).toLocaleDateString("en-GB", { day:"2-digit", month:"short", year:"numeric" }) : "—";
const isOverdue = (d) => d && new Date(d) < new Date();
const getInitials = (email) => email ? email.substring(0, 2).toUpperCase() : "??";

const STATUS_COLORS = {
  Open:"bg-red-100 text-red-700 border-red-200",
  "In Progress":"bg-blue-100 text-blue-700 border-blue-200",
  "On Hold":"bg-amber-100 text-amber-700 border-amber-200",
  Completed:"bg-green-100 text-green-700 border-green-200",
  Closed:"bg-slate-100 text-slate-600 border-slate-200",
  "Under Rectification":"bg-orange-100 text-orange-700 border-orange-200",
  "Ready for Review":"bg-purple-100 text-purple-700 border-purple-200",
  Rejected:"bg-red-100 text-red-700 border-red-200",
  Draft:"bg-slate-100 text-slate-600 border-slate-200",
  Submitted:"bg-blue-100 text-blue-700 border-blue-200",
  Approved:"bg-green-100 text-green-700 border-green-200",
  Active:"bg-green-100 text-green-700 border-green-200",
  Tender:"bg-amber-100 text-amber-700 border-amber-200",
};

const PRIORITY_COLORS = {
  Critical:"bg-red-600 text-white", High:"bg-orange-500 text-white",
  Medium:"bg-amber-400 text-white", Low:"bg-slate-400 text-white",
};

const DISC_COLORS = {
  Architectural:"bg-blue-100 text-blue-700", Structural:"bg-orange-100 text-orange-700",
  MEP:"bg-purple-100 text-purple-700", Civil:"bg-green-100 text-green-700",
};

const Badge = ({ text, colorClass }) => (
  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border ${colorClass || STATUS_COLORS[text] || "bg-slate-100 text-slate-600 border-slate-200"}`}>{text}</span>
);

const Spinner = () => (
  <div className="flex items-center justify-center py-20">
    <div className="w-8 h-8 border-4 border-amber-400 border-t-transparent rounded-full animate-spin"></div>
  </div>
);

const Icon = ({ name, cls="w-5 h-5" }) => {
  const icons = {
    dashboard:<path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>,
    projects:<path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>,
    tasks:<path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>,
    snags:<path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>,
    reports:<path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>,
    drawings:<path strokeLinecap="round" strokeLinejoin="round" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"/>,
    inspections:<path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>,
    photos:<path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>,
    subs:<path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>,
    bell:<path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>,
    check:<path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/>,
    plus:<path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4"/>,
    search:<path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>,
    warn:<path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>,
    kanban:<path strokeLinecap="round" strokeLinejoin="round" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"/>,
    list:<path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16"/>,
    eye:<><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></>,
    map:<path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>,
    logout:<path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>,
  };
  return <svg className={cls} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>{icons[name]}</svg>;
};

const NAV = [
  { id:"dashboard", label:"Dashboard", icon:"dashboard" },
  { id:"projects", label:"Projects", icon:"projects" },
  { id:"tasks", label:"Tasks", icon:"tasks" },
  { id:"snags", label:"Snag List", icon:"snags" },
  { id:"reports", label:"Daily Reports", icon:"reports" },
  { id:"inspections", label:"Inspections", icon:"inspections" },
  { id:"drawings", label:"Drawing Register", icon:"drawings" },
  { id:"photos", label:"Progress Photos", icon:"photos" },
  { id:"subcontractors", label:"Subcontractors", icon:"subs" },
];

const Sidebar = ({ active, onNav, collapsed, user, onSignOut }) => (
  <aside className={`${collapsed?"w-16":"w-60"} bg-slate-900 text-white flex flex-col transition-all duration-200 shrink-0`}>
    <div className="p-4 border-b border-slate-700 flex items-center gap-3">
      <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center shrink-0">
        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
        </svg>
      </div>
      {!collapsed && <div><div className="text-sm font-bold text-white">AGBC</div><div className="text-xs text-slate-400">Site Management</div></div>}
    </div>
    <nav className="flex-1 py-3 overflow-y-auto">
      {NAV.map(n => (
        <button key={n.id} onClick={() => onNav(n.id)}
          className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${active===n.id?"bg-amber-500 text-white font-semibold":"text-slate-300 hover:bg-slate-800 hover:text-white"}`}>
          <Icon name={n.icon} cls="w-5 h-5 shrink-0" />
          {!collapsed && <span>{n.label}</span>}
        </button>
      ))}
    </nav>
    <div className="p-4 border-t border-slate-700">
      {!collapsed && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center text-xs font-bold text-white">{getInitials(user?.email)}</div>
            <div className="min-w-0"><div className="text-xs font-semibold text-white truncate">{user?.email}</div><div className="text-xs text-slate-400">Al Ghaith Building</div></div>
          </div>
          <button onClick={onSignOut} className="w-full flex items-center justify-center gap-2 text-xs text-slate-400 hover:text-red-400 border border-slate-700 hover:border-red-500 px-3 py-2 rounded-lg transition-colors">
            <Icon name="logout" cls="w-3.5 h-3.5" /> Sign Out
          </button>
        </div>
      )}
      {collapsed && <button onClick={onSignOut} className="w-full flex items-center justify-center text-slate-400 hover:text-red-400 p-2 rounded-lg"><Icon name="logout" cls="w-4 h-4" /></button>}
    </div>
  </aside>
);

const Header = ({ title, onToggle, user }) => (
  <header className="h-14 bg-white border-b border-slate-200 flex items-center px-4 gap-3 shrink-0">
    <button onClick={onToggle} className="text-slate-400 hover:text-slate-700">
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16"/></svg>
    </button>
    <span className="font-semibold text-slate-800">{title}</span>
    <div className="ml-auto flex items-center gap-2">
      <button className="relative p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg">
        <Icon name="bell" cls="w-5 h-5" />
        <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
      </button>
      <div className="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center text-xs font-bold text-white">{getInitials(user?.email)}</div>
    </div>
  </header>
);

const StatCard = ({ label, value, sub, color, icon }) => (
  <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-start gap-4">
    <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${color}`}><Icon name={icon} cls="w-5 h-5 text-white" /></div>
    <div><div className="text-2xl font-bold text-slate-800">{value}</div><div className="text-sm text-slate-500">{label}</div>{sub && <div className="text-xs text-slate-400 mt-0.5">{sub}</div>}</div>
  </div>
);

const Dashboard = ({ projects, tasks, snags }) => {
  const today = new Date().toLocaleDateString("en-GB", { weekday:"long", day:"2-digit", month:"long", year:"numeric" });
  const openTasks = tasks.filter(t => t.status !== "Completed" && t.status !== "Closed").length;
  const overdueTasks = tasks.filter(t => isOverdue(t.due) && t.status !== "Completed").length;
  const openSnags = snags.filter(s => s.status !== "Closed").length;
  const activeProjects = projects.filter(p => p.status === "Active").length;
  return (
    <div className="p-6 space-y-6">
      <div><h2 className="text-xl font-bold text-slate-800 mb-1">Good morning</h2><p className="text-sm text-slate-500">{today} — Dubai, UAE</p></div>
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard label="Active Projects" value={activeProjects} sub={`${projects.length} total`} color="bg-blue-500" icon="projects" />
        <StatCard label="Open Tasks" value={openTasks} sub={`${tasks.length} total`} color="bg-amber-500" icon="tasks" />
        <StatCard label="Overdue Tasks" value={overdueTasks} sub="Needs attention" color="bg-red-500" icon="warn" />
        <StatCard label="Open Snags" value={openSnags} sub={`${snags.length} total`} color="bg-orange-500" icon="snags" />
        <StatCard label="Pending IR/WIR" value={2} sub="Awaiting response" color="bg-purple-500" icon="inspections" />
        <StatCard label="Reports Today" value={0} sub="No reports yet" color="bg-green-500" icon="reports" />
      </div>
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <h3 className="font-semibold text-slate-800">Project Overview</h3>
          <span className="text-xs text-slate-400">{projects.length} projects</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50"><tr>{["Project","Location","Consultant","Duration","Open Tasks","Snags","Status"].map(h=><th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>)}</tr></thead>
            <tbody className="divide-y divide-slate-100">
              {projects.map(p=>(
                <tr key={p.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3"><div className="font-medium text-slate-800 text-xs">{p.number}</div><div className="text-slate-600 text-xs max-w-[180px]">{p.name}</div></td>
                  <td className="px-4 py-3 text-xs text-slate-600">{p.location}</td>
                  <td className="px-4 py-3 text-xs text-slate-600">{p.consultant}</td>
                  <td className="px-4 py-3 text-xs text-slate-600 whitespace-nowrap">{p.duration} Months</td>
                  <td className="px-4 py-3 text-xs text-center font-bold text-amber-600">{tasks.filter(t=>t.pid===p.id).length}</td>
                  <td className="px-4 py-3 text-xs text-center font-bold text-red-600">{snags.filter(s=>s.pid===p.id&&s.status!=="Closed").length}</td>
                  <td className="px-4 py-3"><Badge text={p.status} /></td>
                </tr>
              ))}
              {projects.length===0&&<tr><td colSpan={7} className="text-center py-10 text-slate-400">Loading projects...</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 font-semibold text-slate-800 text-sm">Recent Tasks ({tasks.length})</div>
          <div className="divide-y divide-slate-100">
            {tasks.slice(0,5).map(t=>(
              <div key={t.id} className="px-5 py-3 flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full shrink-0 ${t.status==="Completed"?"bg-green-500":t.status==="In Progress"?"bg-blue-500":"bg-slate-300"}`}></div>
                <div className="flex-1 min-w-0"><div className="text-sm font-medium text-slate-700 truncate">{t.title}</div><div className="text-xs text-slate-400">{t.location}</div></div>
                <Badge text={t.priority} colorClass={PRIORITY_COLORS[t.priority]} />
              </div>
            ))}
            {tasks.length===0&&<div className="px-5 py-8 text-center text-slate-400 text-sm">No tasks yet</div>}
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 font-semibold text-slate-800 text-sm">Open Snags ({openSnags})</div>
          <div className="divide-y divide-slate-100">
            {snags.filter(s=>s.status!=="Closed").slice(0,5).map(s=>(
              <div key={s.id} className="px-5 py-3 flex items-center gap-3">
                <div className="flex-1 min-w-0"><div className="text-xs font-semibold text-amber-600">{s.num}</div><div className="text-sm font-medium text-slate-700 truncate">{s.title}</div></div>
                <Badge text={s.status} />
              </div>
            ))}
            {openSnags===0&&<div className="px-5 py-8 text-center text-slate-400 text-sm">No open snags</div>}
          </div>
        </div>
      </div>
    </div>
  );
};

const Projects = ({ projects, loading }) => {
  const [search, setSearch] = useState("");
  const filtered = projects.filter(p => p.name.toLowerCase().includes(search.toLowerCase()) || p.number.toLowerCase().includes(search.toLowerCase()));
  if (loading) return <Spinner />;
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">Projects ({projects.length})</h2>
        <button className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg"><Icon name="plus" cls="w-4 h-4" /> New Project</button>
      </div>
      <div className="relative max-w-sm"><Icon name="search" cls="w-4 h-4 absolute left-3 top-2.5 text-slate-400" /><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search projects..." className="w-full pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {filtered.map(p=>(
          <div key={p.id} className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between gap-3 mb-4">
              <div><div className="flex items-center gap-2 mb-1"><span className="text-xs text-slate-400 font-mono font-bold">{p.number}</span><Badge text={p.status} /></div><h3 className="font-semibold text-slate-800 leading-tight">{p.name}</h3></div>
              {p.mapUrl&&<a href={p.mapUrl} target="_blank" rel="noreferrer" className="shrink-0 flex items-center gap-1 text-xs text-blue-600 border border-blue-200 px-2 py-1 rounded-lg"><Icon name="map" cls="w-3.5 h-3.5" /> Map</a>}
            </div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-xs text-slate-600 mb-4">
              <div><span className="text-slate-400">Location: </span>{p.location}</div>
              <div><span className="text-slate-400">Plot: </span>{p.plot}</div>
              <div><span className="text-slate-400">Consultant: </span>{p.consultant}</div>
              <div><span className="text-slate-400">Duration: </span>{p.duration} Months</div>
              {p.plotArea&&<div><span className="text-slate-400">Plot Area: </span>{fmtNum(p.plotArea)} sqft</div>}
              {p.bua&&<div><span className="text-slate-400">BUA: </span>{fmtNum(p.bua)} sqft</div>}
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1 text-amber-600 font-semibold"><Icon name="tasks" cls="w-3.5 h-3.5" /> {p.openTasks} Tasks</span>
              <span className="flex items-center gap-1 text-red-600 font-semibold"><Icon name="snags" cls="w-3.5 h-3.5" /> {p.openSnags} Snags</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const Tasks = ({ projects, tasks, loading, onAddTask, onUpdateStatus }) => {
  const [view, setView] = useState("list");
  const [filterStatus, setFilterStatus] = useState("All");
  const [filterProject, setFilterProject] = useState("All");
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ project_id:"", title:"", description:"", location:"", trade:"", assignee:"", priority:"Medium", due_date:"" });
  const filtered = tasks.filter(t => {
    if (filterStatus !== "All" && t.status !== filterStatus) return false;
    if (filterProject !== "All" && t.pid !== filterProject) return false;
    if (search && !t.title.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });
  const handleSubmit = async () => {
    if (!form.title || !form.project_id) { alert("Please fill in Task Title and Project"); return; }
    setSaving(true);
    const ok = await onAddTask(form);
    setSaving(false);
    if (ok) { setShowForm(false); setForm({ project_id:"", title:"", description:"", location:"", trade:"", assignee:"", priority:"Medium", due_date:"" }); }
  };
  if (showForm) return (
    <div className="p-6 space-y-5 max-w-2xl">
      <div className="flex items-center gap-3"><button onClick={()=>setShowForm(false)} className="text-slate-400 hover:text-slate-700 text-sm">Back</button><h2 className="text-xl font-bold text-slate-800">New Task</h2></div>
      <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
        <div><label className="text-xs font-semibold text-slate-600 block mb-1">Project *</label><select value={form.project_id} onChange={e=>setForm({...form,project_id:e.target.value})} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400"><option value="">Select Project...</option>{projects.map(p=><option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}</select></div>
        <div><label className="text-xs font-semibold text-slate-600 block mb-1">Task Title *</label><input value={form.title} onChange={e=>setForm({...form,title:e.target.value})} placeholder="e.g. Pour Grade Slab — Block A" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
        <div><label className="text-xs font-semibold text-slate-600 block mb-1">Description</label><textarea rows={3} value={form.description} onChange={e=>setForm({...form,description:e.target.value})} placeholder="Task details..." className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 resize-none" /></div>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Location</label><input value={form.location} onChange={e=>setForm({...form,location:e.target.value})} placeholder="e.g. Level 3" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Trade</label><select value={form.trade} onChange={e=>setForm({...form,trade:e.target.value})} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400"><option value="">Select...</option>{["Civil / Structural","Civil / Masonry","MEP / HVAC","MEP / Electrical","MEP / Plumbing","Finishing","Aluminum / Glazing","Safety"].map(t=><option key={t}>{t}</option>)}</select></div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Assignee</label><input value={form.assignee} onChange={e=>setForm({...form,assignee:e.target.value})} placeholder="Engineer name" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Priority</label><select value={form.priority} onChange={e=>setForm({...form,priority:e.target.value})} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400">{["Low","Medium","High","Critical"].map(p=><option key={p}>{p}</option>)}</select></div>
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Due Date</label><input type="date" value={form.due_date} onChange={e=>setForm({...form,due_date:e.target.value})} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
        </div>
        <div className="flex gap-3 pt-2">
          <button onClick={handleSubmit} disabled={saving} className="bg-amber-500 hover:bg-amber-600 disabled:opacity-60 text-white font-semibold text-sm px-6 py-2.5 rounded-lg flex items-center gap-2">{saving?<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>Saving...</>:"Save Task"}</button>
          <button onClick={()=>setShowForm(false)} className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm px-6 py-2.5 rounded-lg">Cancel</button>
        </div>
      </div>
    </div>
  );
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between"><h2 className="text-xl font-bold text-slate-800">Tasks ({tasks.length})</h2><button onClick={()=>setShowForm(true)} className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg"><Icon name="plus" cls="w-4 h-4" /> New Task</button></div>
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative"><Icon name="search" cls="w-4 h-4 absolute left-3 top-2.5 text-slate-400" /><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search..." className="pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 w-48" /></div>
        <select value={filterStatus} onChange={e=>setFilterStatus(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-2"><option value="All">All Status</option>{["Open","In Progress","On Hold","Completed","Closed"].map(s=><option key={s}>{s}</option>)}</select>
        <select value={filterProject} onChange={e=>setFilterProject(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-2"><option value="All">All Projects</option>{projects.map(p=><option key={p.id} value={p.id}>{p.number}</option>)}</select>
        <div className="ml-auto flex gap-1 bg-slate-100 p-1 rounded-lg">
          <button onClick={()=>setView("list")} className={`p-1.5 rounded ${view==="list"?"bg-white shadow-sm text-amber-600":"text-slate-400"}`}><Icon name="list" cls="w-4 h-4"/></button>
          <button onClick={()=>setView("kanban")} className={`p-1.5 rounded ${view==="kanban"?"bg-white shadow-sm text-amber-600":"text-slate-400"}`}><Icon name="kanban" cls="w-4 h-4"/></button>
        </div>
      </div>
      {loading ? <Spinner /> : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <table className="w-full text-sm"><thead className="bg-slate-50"><tr>{["Task","Project","Location","Trade","Assignee","Priority","Due Date","Status","Action"].map(h=><th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>)}</tr></thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map(t=>(
                <tr key={t.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3"><div className="font-medium text-slate-800 text-sm max-w-[200px] leading-tight">{t.title}</div><div className="text-xs text-slate-400 mt-0.5 max-w-[200px] truncate">{t.desc}</div></td>
                  <td className="px-4 py-3 text-xs text-slate-500">{projects.find(p=>p.id===t.pid)?.number||"—"}</td>
                  <td className="px-4 py-3 text-xs text-slate-600">{t.location}</td>
                  <td className="px-4 py-3 text-xs text-slate-600">{t.trade}</td>
                  <td className="px-4 py-3 text-xs text-slate-700 font-medium">{t.assignee}</td>
                  <td className="px-4 py-3"><Badge text={t.priority} colorClass={PRIORITY_COLORS[t.priority]} /></td>
                  <td className="px-4 py-3"><span className={`text-xs font-medium ${isOverdue(t.due)&&t.status!=="Completed"?"text-red-600":"text-slate-600"}`}>{fmtDate(t.due)}</span></td>
                  <td className="px-4 py-3"><Badge text={t.status} /></td>
                  <td className="px-4 py-3"><select value={t.status} onChange={e=>onUpdateStatus(t.id,e.target.value)} className="text-xs border border-slate-200 rounded-lg px-2 py-1">{["Open","In Progress","On Hold","Completed","Closed"].map(s=><option key={s}>{s}</option>)}</select></td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length===0&&<div className="text-center py-16 text-slate-400"><p>No tasks — <button onClick={()=>setShowForm(true)} className="text-amber-500 font-semibold">Add first task</button></p></div>}
        </div>
      )}
    </div>
  );
};

const Snags = ({ projects, snags, loading, onAddSnag, onUpdateStatus }) => {
  const [filterStatus, setFilterStatus] = useState("All");
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ project_id:"", title:"", description:"", location:"", category:"", sub:"", engineer:"", due_date:"" });
  const SNAG_STATUSES = ["Open","Under Rectification","Ready for Review","Closed","Rejected"];
  const filtered = snags.filter(s => {
    if (filterStatus !== "All" && s.status !== filterStatus) return false;
    if (search && !s.title.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });
  const handleSubmit = async () => {
    if (!form.title || !form.project_id) { alert("Please fill Title and Project"); return; }
    setSaving(true);
    const ok = await onAddSnag(form);
    setSaving(false);
    if (ok) { setShowForm(false); setForm({ project_id:"", title:"", description:"", location:"", category:"", sub:"", engineer:"", due_date:"" }); }
  };
  if (showForm) return (
    <div className="p-6 space-y-5 max-w-2xl">
      <div className="flex items-center gap-3"><button onClick={()=>setShowForm(false)} className="text-slate-400 hover:text-slate-700 text-sm">Back</button><h2 className="text-xl font-bold text-slate-800">New Snag</h2></div>
      <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
        <div><label className="text-xs font-semibold text-slate-600 block mb-1">Project *</label><select value={form.project_id} onChange={e=>setForm({...form,project_id:e.target.value})} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400"><option value="">Select Project...</option>{projects.map(p=><option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}</select></div>
        <div><label className="text-xs font-semibold text-slate-600 block mb-1">Snag Title *</label><input value={form.title} onChange={e=>setForm({...form,title:e.target.value})} placeholder="e.g. Plastering crack — Column C7" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
        <div><label className="text-xs font-semibold text-slate-600 block mb-1">Description</label><textarea rows={3} value={form.description} onChange={e=>setForm({...form,description:e.target.value})} placeholder="Describe the defect..." className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 resize-none" /></div>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Location</label><input value={form.location} onChange={e=>setForm({...form,location:e.target.value})} placeholder="e.g. Level 2" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Category</label><select value={form.category} onChange={e=>setForm({...form,category:e.target.value})} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400"><option value="">Select...</option>{["Architectural","Structural","MEP","Finishing","Civil","Safety"].map(c=><option key={c}>{c}</option>)}</select></div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Subcontractor</label><input value={form.sub} onChange={e=>setForm({...form,sub:e.target.value})} placeholder="Sub company" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Engineer</label><input value={form.engineer} onChange={e=>setForm({...form,engineer:e.target.value})} placeholder="Engineer name" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Due Date</label><input type="date" value={form.due_date} onChange={e=>setForm({...form,due_date:e.target.value})} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
        </div>
        <div className="flex gap-3 pt-2">
          <button onClick={handleSubmit} disabled={saving} className="bg-amber-500 hover:bg-amber-600 disabled:opacity-60 text-white font-semibold text-sm px-6 py-2.5 rounded-lg flex items-center gap-2">{saving?<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>Saving...</>:"Save Snag"}</button>
          <button onClick={()=>setShowForm(false)} className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm px-6 py-2.5 rounded-lg">Cancel</button>
        </div>
      </div>
    </div>
  );
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between"><h2 className="text-xl font-bold text-slate-800">Snag / Punch List ({snags.length})</h2><button onClick={()=>setShowForm(true)} className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg"><Icon name="plus" cls="w-4 h-4" /> New Snag</button></div>
      <div className="flex gap-3 flex-wrap">{SNAG_STATUSES.map(s=>{const count=snags.filter(sn=>sn.status===s).length;return <button key={s} onClick={()=>setFilterStatus(filterStatus===s?"All":s)} className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors ${filterStatus===s?(STATUS_COLORS[s]||"bg-slate-200"):"bg-white border-slate-200 text-slate-600 hover:bg-slate-50"}`}>{s} ({count})</button>;})}</div>
      <div className="relative max-w-sm"><Icon name="search" cls="w-4 h-4 absolute left-3 top-2.5 text-slate-400" /><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search snags..." className="w-full pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
      {loading ? <Spinner /> : (
        <div className="space-y-3">
          {filtered.map(s=>(
            <div key={s.id} className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1"><span className="text-xs font-mono font-bold text-amber-600">{s.num}</span><Badge text={s.category} colorClass="bg-slate-100 text-slate-600 border-slate-200" /><span className="text-xs text-slate-400">{projects.find(p=>p.id===s.pid)?.number||""}</span></div>
                  <h3 className="font-semibold text-slate-800 mb-1">{s.title}</h3>
                  <p className="text-sm text-slate-500 mb-2">{s.desc}</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-1 text-xs text-slate-600">
                    <div><span className="text-slate-400">Location: </span>{s.location}</div>
                    <div><span className="text-slate-400">Sub: </span>{s.sub||"—"}</div>
                    <div><span className="text-slate-400">Engineer: </span>{s.engineer||"—"}</div>
                    <div><span className="text-slate-400">Due: </span>{fmtDate(s.due)}</div>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2 shrink-0">
                  <select value={s.status} onChange={e=>onUpdateStatus(s.id,e.target.value)} className="text-xs border border-slate-200 rounded-lg px-2 py-1">{SNAG_STATUSES.map(st=><option key={st}>{st}</option>)}</select>
                </div>
              </div>
            </div>
          ))}
          {filtered.length===0&&<div className="text-center py-16 text-slate-400 bg-white rounded-xl border border-slate-200"><p>No snags — <button onClick={()=>setShowForm(true)} className="text-amber-500 font-semibold">Add first snag</button></p></div>}
        </div>
      )}
    </div>
  );
};

const DailyReports = ({ projects, reports, loading, onAddReport }) => {
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ project_id:"", report_date:"", weather:"Sunny", temperature:"", manpower:"", activities:"", completed:"", issues:"", preparedBy:"" });
  const handleSubmit = async () => {
    if (!form.project_id || !form.report_date) { alert("Please select Project and Date"); return; }
    setSaving(true);
    const ok = await onAddReport(form);
    setSaving(false);
    if (ok) { setShowForm(false); setForm({ project_id:"", report_date:"", weather:"Sunny", temperature:"", manpower:"", activities:"", completed:"", issues:"", preparedBy:"" }); }
  };
  if (showForm) return (
    <div className="p-6 space-y-5">
      <div className="flex items-center gap-3"><button onClick={()=>setShowForm(false)} className="text-slate-400 hover:text-slate-700 text-sm">Back</button><h2 className="text-xl font-bold text-slate-800">New Daily Site Report</h2></div>
      <div className="bg-white rounded-xl border border-slate-200 p-5 max-w-3xl space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Project *</label><select value={form.project_id} onChange={e=>setForm({...form,project_id:e.target.value})} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400"><option value="">Select Project...</option>{projects.map(p=><option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}</select></div>
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Date *</label><input type="date" value={form.report_date} onChange={e=>setForm({...form,report_date:e.target.value})} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Weather</label><input value={form.weather} onChange={e=>setForm({...form,weather:e.target.value})} placeholder="e.g. Sunny" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Temperature (C)</label><input value={form.temperature} onChange={e=>setForm({...form,temperature:e.target.value})} placeholder="e.g. 32" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Total Manpower</label><input value={form.manpower} onChange={e=>setForm({...form,manpower:e.target.value})} placeholder="e.g. 45" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
          <div><label className="text-xs font-semibold text-slate-600 block mb-1">Prepared By</label><input value={form.preparedBy} onChange={e=>setForm({...form,preparedBy:e.target.value})} placeholder="Your name" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
        </div>
        {[["Work Activities Today","activities"],["Work Completed","completed"],["Issues / Delays","issues"]].map(([label,key])=>(
          <div key={key}><label className="text-xs font-semibold text-slate-600 block mb-1">{label}</label><textarea rows={3} value={form[key]} onChange={e=>setForm({...form,[key]:e.target.value})} placeholder={`Enter ${label.toLowerCase()}...`} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 resize-none" /></div>
        ))}
        <div className="flex gap-3 pt-2">
          <button onClick={handleSubmit} disabled={saving} className="bg-amber-500 hover:bg-amber-600 disabled:opacity-60 text-white font-semibold text-sm px-6 py-2.5 rounded-lg flex items-center gap-2">{saving?<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>Saving...</>:"Save Report"}</button>
          <button onClick={()=>setShowForm(false)} className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm px-6 py-2.5 rounded-lg">Cancel</button>
        </div>
      </div>
    </div>
  );
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between"><h2 className="text-xl font-bold text-slate-800">Daily Site Reports ({reports.length})</h2><button onClick={()=>setShowForm(true)} className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg"><Icon name="plus" cls="w-4 h-4" /> New Report</button></div>
      {loading ? <Spinner /> : reports.length === 0 ? (
        <div className="text-center py-20 text-slate-400 bg-white rounded-xl border border-slate-200"><Icon name="reports" cls="w-10 h-10 mx-auto mb-3 text-slate-200" /><p>No reports yet — <button onClick={()=>setShowForm(true)} className="text-amber-500 font-semibold">Add first report</button></p></div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {reports.map(r=>(
            <div key={r.id} className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between gap-3 mb-3"><div><div className="font-bold text-slate-800">{fmtDate(r.date)}</div><div className="text-xs text-slate-500">{projects.find(p=>p.id===r.pid)?.name||"—"}</div></div><Badge text={r.status} /></div>
              <div className="grid grid-cols-3 gap-3 mb-3 text-center">
                <div className="bg-blue-50 rounded-lg p-2"><div className="text-lg font-bold text-blue-700">{r.manpower}</div><div className="text-xs text-blue-500">Manpower</div></div>
                <div className="bg-amber-50 rounded-lg p-2"><div className="text-sm font-bold text-amber-700">{r.weather}</div><div className="text-xs text-amber-500">Weather</div></div>
                <div className="bg-green-50 rounded-lg p-2"><div className="text-sm font-bold text-green-700">{r.temp}</div><div className="text-xs text-green-500">Temp</div></div>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed mb-3">{r.activities}</p>
              <div className="text-xs text-slate-400">By: <strong className="text-slate-600">{r.preparedBy}</strong></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const Inspections = ({ projects }) => {
  const [filterStatus, setFilterStatus] = useState("All");
  const IR_STATUSES = ["Draft","Submitted","Approved","Rejected","Resubmitted"];
  const filtered = INSPECTIONS.filter(i => filterStatus === "All" || i.status === filterStatus);
  const typeColors = { WIR:"bg-blue-100 text-blue-700", MIR:"bg-green-100 text-green-700" };
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between"><h2 className="text-xl font-bold text-slate-800">Inspection Request Tracker</h2><button className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg"><Icon name="plus" cls="w-4 h-4" /> New IR/WIR</button></div>
      <div className="flex gap-2 flex-wrap">{["All",...IR_STATUSES].map(s=>{const count=s==="All"?INSPECTIONS.length:INSPECTIONS.filter(i=>i.status===s).length;return <button key={s} onClick={()=>setFilterStatus(s)} className={`px-3 py-1.5 rounded-lg text-xs font-semibold border ${filterStatus===s?"bg-amber-500 text-white border-amber-500":"bg-white border-slate-200 text-slate-600"}`}>{s} ({count})</button>;})}</div>
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm"><thead className="bg-slate-50"><tr>{["IR Number","Type","Description","Project","Location","Submitted","Inspection Date","Status"].map(h=><th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">{h}</th>)}</tr></thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map(i=>(
              <tr key={i.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-mono text-xs font-semibold text-amber-700">{i.num}</td>
                <td className="px-4 py-3"><span className={`text-xs font-bold px-2 py-0.5 rounded-full ${typeColors[i.type]||"bg-slate-100 text-slate-600"}`}>{i.type}</span></td>
                <td className="px-4 py-3 text-xs text-slate-700 max-w-[180px] leading-tight">{i.desc}</td>
                <td className="px-4 py-3 text-xs text-slate-500">{projects.find(p=>p.id===i.pid)?.number||"—"}</td>
                <td className="px-4 py-3 text-xs text-slate-600">{i.location}</td>
                <td className="px-4 py-3 text-xs text-slate-600 whitespace-nowrap">{fmtDate(i.submitted)}</td>
                <td className="px-4 py-3 text-xs text-slate-600 whitespace-nowrap">{i.inspection?fmtDate(i.inspection):<span className="text-slate-300">TBD</span>}</td>
                <td className="px-4 py-3"><Badge text={i.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const Drawings = ({ projects }) => {
  const [filterDisc, setFilterDisc] = useState("All");
  const DISCIPLINES = ["Architectural","Structural","MEP","Civil"];
  const filtered = DRAWINGS.filter(d => filterDisc === "All" || d.discipline === filterDisc);
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between"><h2 className="text-xl font-bold text-slate-800">Drawing Register</h2><button className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg"><Icon name="plus" cls="w-4 h-4" /> Upload Drawing</button></div>
      <div className="flex gap-1">{["All",...DISCIPLINES].map(d=><button key={d} onClick={()=>setFilterDisc(d)} className={`px-3 py-2 text-xs font-semibold rounded-lg border ${filterDisc===d?"bg-amber-500 text-white border-amber-500":"bg-white border-slate-200 text-slate-600"}`}>{d}</button>)}</div>
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm"><thead className="bg-slate-50"><tr>{["Drawing No.","Title","Discipline","Rev","Project","Date Received","Status"].map(h=><th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>)}</tr></thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map(d=>(
              <tr key={d.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-mono text-xs font-semibold text-slate-700">{d.num}</td>
                <td className="px-4 py-3 text-sm text-slate-800 font-medium">{d.title}</td>
                <td className="px-4 py-3"><span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${DISC_COLORS[d.discipline]||"bg-slate-100 text-slate-600"}`}>{d.discipline}</span></td>
                <td className="px-4 py-3"><span className="font-mono text-xs font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">Rev {d.rev}</span></td>
                <td className="px-4 py-3 text-xs text-slate-500">{projects.find(p=>p.id===d.pid)?.number||"—"}</td>
                <td className="px-4 py-3 text-xs text-slate-600 whitespace-nowrap">{fmtDate(d.received)}</td>
                <td className="px-4 py-3">{d.latest?<span className="text-xs text-green-600 font-semibold">Current</span>:<span className="text-xs text-slate-400">Superseded</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const Subcontractors = () => (
  <div className="p-6 space-y-4">
    <div className="flex items-center justify-between"><h2 className="text-xl font-bold text-slate-800">Subcontractors</h2><button className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg"><Icon name="plus" cls="w-4 h-4" /> Add Subcontractor</button></div>
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
      {SUBCONTRACTORS.map(s=>(
        <div key={s.id} className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between gap-3 mb-3"><div><div className="font-semibold text-slate-800">{s.name}</div><div className="text-xs text-slate-500">{s.contact}</div></div><span className={`px-2 py-0.5 text-xs font-bold rounded-full border ${s.active?"bg-green-100 text-green-700 border-green-200":"bg-slate-100 text-slate-500 border-slate-200"}`}>{s.active?"Active":"Inactive"}</span></div>
          <div className="flex flex-wrap gap-1 mb-3">{s.trades.map(t=><span key={t} className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">{t}</span>)}</div>
          <div className="grid grid-cols-3 gap-3 text-center text-xs mb-3">
            <div className="bg-slate-50 rounded-lg p-2"><div className="font-bold text-slate-800">{s.projects}</div><div className="text-slate-400">Projects</div></div>
            <div className="bg-amber-50 rounded-lg p-2"><div className="font-bold text-amber-700">{s.openTasks}</div><div className="text-amber-500">Open Tasks</div></div>
            <div className="bg-red-50 rounded-lg p-2"><div className="font-bold text-red-600">{s.openSnags}</div><div className="text-red-400">Open Snags</div></div>
          </div>
          <div className="flex items-center gap-4 text-xs text-slate-500"><span>{s.phone}</span><span className="truncate">{s.email}</span></div>
        </div>
      ))}
    </div>
  </div>
);

const Photos = ({ projects }) => {
  const [photos, setPhotos] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ project_id:"", caption:"", area:"", file:null });

  const fetchPhotos = async () => {
    const { data, error } = await supabase.from("project_photos").select("*").order("uploaded_at", { ascending: false });
    if (error) console.error("Photos error:", error);
    if (data) setPhotos(data);
  };

  useEffect(() => { fetchPhotos(); }, []);

  const handleUpload = async () => {
    if (!form.file || !form.project_id) { alert("Please select a project and photo"); return; }
    setUploading(true);
    const fileExt = form.file.name.split(".").pop();
    const fileName = `${Date.now()}.${fileExt}`;
    const { data: uploadData, error: uploadError } = await supabase.storage
      .from("site-photos").upload(fileName, form.file);
    if (uploadError) { console.error("Upload error:", uploadError); setUploading(false); return; }
    const { data: { publicUrl } } = supabase.storage.from("site-photos").getPublicUrl(fileName);
    await supabase.from("project_photos").insert([{
      project_id: form.project_id, file_url: publicUrl,
      caption: form.caption, area: form.area,
    }]);
    await fetchPhotos();
    setUploading(false);
    setShowForm(false);
    setForm({ project_id:"", caption:"", area:"", file:null });
  };

  if (showForm) return (
    <div className="p-6 space-y-5 max-w-lg">
      <div className="flex items-center gap-3"><button onClick={()=>setShowForm(false)} className="text-slate-400 hover:text-slate-700 text-sm">Back</button><h2 className="text-xl font-bold text-slate-800">Upload Photo</h2></div>
      <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
        <div><label className="text-xs font-semibold text-slate-600 block mb-1">Project *</label>
          <select value={form.project_id} onChange={e=>setForm({...form,project_id:e.target.value})} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400">
            <option value="">Select Project...</option>{projects.map(p=><option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}</select></div>
        <div><label className="text-xs font-semibold text-slate-600 block mb-1">Caption</label>
          <input value={form.caption} onChange={e=>setForm({...form,caption:e.target.value})} placeholder="e.g. Grade slab pour — Block A" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
        <div><label className="text-xs font-semibold text-slate-600 block mb-1">Area / Location</label>
          <input value={form.area} onChange={e=>setForm({...form,area:e.target.value})} placeholder="e.g. Ground Floor Block A" className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
        <div><label className="text-xs font-semibold text-slate-600 block mb-1">Photo *</label>
          <input type="file" accept="image/*" onChange={e=>setForm({...form,file:e.target.files[0]})} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" /></div>
        <div className="flex gap-3 pt-2">
          <button onClick={handleUpload} disabled={uploading} className="bg-amber-500 hover:bg-amber-600 disabled:opacity-60 text-white font-semibold text-sm px-6 py-2.5 rounded-lg flex items-center gap-2">
            {uploading?<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>Uploading...</>:"Upload Photo"}</button>
          <button onClick={()=>setShowForm(false)} className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm px-6 py-2.5 rounded-lg">Cancel</button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">Progress Photos ({photos.length})</h2>
        <button onClick={()=>setShowForm(true)} className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg"><Icon name="plus" cls="w-4 h-4" /> Upload Photos</button>
      </div>
      {photos.length === 0 ? (
        <div className="text-center py-20 text-slate-400 bg-white rounded-xl border border-slate-200">
          <Icon name="photos" cls="w-10 h-10 mx-auto mb-3 text-slate-200" />
          <p>No photos yet — <button onClick={()=>setShowForm(true)} className="text-amber-500 font-semibold">Upload first photo</button></p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
          {photos.map(p=>(
            <div key={p.id} className="bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer group">
              <div className="h-40 overflow-hidden bg-slate-100">
                <img src={p.file_url} alt={p.caption} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200" />
              </div>
              <div className="p-3">
                <div className="text-xs font-semibold text-slate-700 leading-tight mb-1">{p.caption||"No caption"}</div>
                <div className="text-xs text-slate-400">{p.area}</div>
                <div className="text-xs text-slate-400 mt-1">{fmtDate(p.uploaded_at?.split("T")[0])}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const PAGE_TITLES = {
  dashboard:"Dashboard", projects:"Projects", tasks:"Task Management",
  snags:"Snag / Punch List", reports:"Daily Site Reports",
  inspections:"Inspection Request Tracker", drawings:"Drawing Register",
  photos:"Progress Photos", subcontractors:"Subcontractors",
};

export default function App() {
  const { user, loading: authLoading } = useAuth();
  const { projects, loading: projectsLoading } = useProjects();
  const { tasks, loading: tasksLoading, addTask, updateTaskStatus } = useTasks();
  const { snags, loading: snagsLoading, addSnag, updateSnagStatus } = useSnags();
  const { reports, loading: reportsLoading, addReport } = useDailyReports();
  const [page, setPage] = useState("dashboard");
  const [collapsed, setCollapsed] = useState(false);

  const handleSignOut = async () => { await supabase.auth.signOut(); };

  if (authLoading) return (
    <div className="flex h-screen items-center justify-center bg-slate-50">
      <div className="text-center"><div className="w-10 h-10 border-4 border-amber-400 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div><p className="text-sm text-slate-500">Loading AGBC...</p></div>
    </div>
  );

  if (!user) return <Login onLogin={() => {}} />;

  const renderPage = () => {
    switch (page) {
      case "dashboard":      return <Dashboard      projects={projects} tasks={tasks} snags={snags} />;
      case "projects":       return <Projects       projects={projects} loading={projectsLoading} />;
      case "tasks":          return <Tasks          projects={projects} tasks={tasks} loading={tasksLoading} onAddTask={addTask} onUpdateStatus={updateTaskStatus} />;
      case "snags":          return <Snags          projects={projects} snags={snags} loading={snagsLoading} onAddSnag={addSnag} onUpdateStatus={updateSnagStatus} />;
      case "reports":        return <DailyReports   projects={projects} reports={reports} loading={reportsLoading} onAddReport={addReport} />;
      case "inspections":    return <Inspections    projects={projects} />;
      case "drawings":       return <Drawings       projects={projects} />;
      case "photos":         return <Photos         projects={projects} />;
      case "subcontractors": return <Subcontractors />;
      default: return <div className="p-12 text-center text-slate-400"><p className="text-lg font-semibold">Module coming soon</p></div>;
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans text-slate-800">
      <style>{`* { box-sizing: border-box; } body { margin: 0; font-family: 'Inter', system-ui, sans-serif; } ::-webkit-scrollbar { width: 5px; height: 5px; } ::-webkit-scrollbar-track { background: #f1f5f9; } ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 99px; }`}</style>
      <Sidebar active={page} onNav={setPage} collapsed={collapsed} user={user} onSignOut={handleSignOut} />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header title={PAGE_TITLES[page]||"AGBC"} onToggle={()=>setCollapsed(!collapsed)} user={user} />
        <main className="flex-1 overflow-y-auto">{renderPage()}</main>
      </div>
    </div>
  );
}