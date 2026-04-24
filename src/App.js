import { useState, useMemo, useEffect } from "react";
import { supabase } from "./supabase";
import Login from "./Login";

function useProjects() {
  const [projects, setProjects] = useState([]);
  useEffect(() => {
    supabase.from("projects").select("*").then(({ data }) => {
      if (data) setProjects(data.map(p => ({
        id: p.id, number: p.project_number, name: p.project_name,
        plot: p.plot_number, location: p.location, client: p.client_name,
        consultant: p.consultant_name, pm: p.project_manager_id || "TBA",
        engineer: p.site_engineer_id || "TBA", start: p.start_date,
        end: p.end_date, value: p.contract_value || 0, status: p.status,
        progress: 0, openTasks: 0, openSnags: 0, pendingIR: 0
      })));
    });
  }, []);
  return projects;
}

// ── MOCK DATA ─────────────────────────────────────────────────────────────────
const PROJECTS = [
  { id: "p1", number: "AGBC-2024-001", name: "G+5+Roof Office & Retail Building", plot: "6457995", location: "Wadi Al Safa 3, Dubai", client: "Al Ansari Real Estate LLC", consultant: "Khatib & Alami", pm: "Ahmed Al Mansoori", engineer: "Ravi Kumar", start: "2024-03-01", end: "2025-09-30", value: 18500000, status: "Active", progress: 68, openTasks: 12, openSnags: 7, pendingIR: 3 },
  { id: "p2", number: "AGBC-2024-002", name: "G+4+Roof Residential Building", plot: "RG-80", location: "Dubai South", client: "Emirates South Properties", consultant: "SSH International", pm: "Tariq Hassan", engineer: "Sunil Menon", start: "2024-06-01", end: "2025-12-31", value: 12300000, status: "Active", progress: 41, openTasks: 8, openSnags: 14, pendingIR: 5 },
  { id: "p3", number: "AGBC-2024-003", name: "2B+G+12+R Residential Tower", plot: "DL-4521", location: "Dubai Land Residences", client: "Al Salam Real Estate", consultant: "Dar Al Handasah", pm: "Mohammed Al Farsi", engineer: "Pradeep Nair", start: "2025-01-01", end: "2026-12-31", value: 42000000, status: "Tender", progress: 5, openTasks: 3, openSnags: 0, pendingIR: 0 },
];

const TASKS = [
  { id: "t1", pid: "p1", title: "Pour Grade Slab — Block A", desc: "Concrete pour for grade slab, mix design M30, 85m³", location: "Ground Floor – Block A", trade: "Civil / Structural", assignee: "Ravi Kumar", priority: "Critical", status: "In Progress", due: "2025-01-28", created: "2025-01-20", comments: 3 },
  { id: "t2", pid: "p1", title: "Install HVAC Ducting — Level 3", desc: "Supply and fix GI ducting as per approved shop drawings", location: "Level 3 – Zone B", trade: "MEP / HVAC", assignee: "Arun Pillai", priority: "High", status: "Open", due: "2025-02-05", created: "2025-01-18", comments: 1 },
  { id: "t3", pid: "p1", title: "Fix Wall Tiling — Lobby", desc: "600×1200 porcelain tiling to lobby walls, approved sample ref: TL-003", location: "Ground Floor – Main Lobby", trade: "Finishing", assignee: "Ravi Kumar", priority: "Medium", status: "Open", due: "2025-02-10", created: "2025-01-15", comments: 0 },
  { id: "t4", pid: "p1", title: "Waterproofing Inspection — Roof", desc: "Post-waterproofing inspection before screed and tiling", location: "Roof Level", trade: "Civil / Waterproofing", assignee: "Sanjay Verma", priority: "High", status: "Completed", due: "2025-01-22", created: "2025-01-10", comments: 4 },
  { id: "t5", pid: "p2", title: "Blockwork Level 4 — All Zones", desc: "200mm AAC blockwork, complete internal partition layout", location: "Level 4 – All Zones", trade: "Civil / Masonry", assignee: "Sunil Menon", priority: "High", status: "In Progress", due: "2025-02-03", created: "2025-01-22", comments: 2 },
  { id: "t6", pid: "p2", title: "Electrical Conduit — Level 3", desc: "First fix electrical conduit before plaster", location: "Level 3", trade: "MEP / Electrical", assignee: "Deepak Raj", priority: "High", status: "On Hold", due: "2025-01-30", created: "2025-01-19", comments: 2 },
  { id: "t7", pid: "p2", title: "Aluminium Windows — Level 1 & 2", desc: "Fix aluminium windows as per approved shop drawings Rev B", location: "Level 1 & 2", trade: "Aluminium / Glazing", assignee: "Farid Al Ameri", priority: "Medium", status: "Open", due: "2025-02-15", created: "2025-01-25", comments: 0 },
  { id: "t8", pid: "p1", title: "Mock-up Approval — External Cladding", desc: "Submit and get approval for external aluminium cladding mock-up", location: "External — South Elevation", trade: "Aluminium / Cladding", assignee: "Arun Pillai", priority: "Medium", status: "Open", due: "2025-01-25", created: "2025-01-12", comments: 1 },
];

const SNAGS = [
  { id: "s1", pid: "p1", num: "SNF-001", title: "Plastering crack — Column C7", desc: "Hairline crack observed on plastered column, requires cutting, filling, re-plaster", location: "Level 2 – Grid C7", category: "Finishing", sub: "Green Emirates Contracting", engineer: "Ravi Kumar", due: "2025-01-30", status: "Under Rectification", before: true, after: false, consultant: "" },
  { id: "s2", pid: "p1", num: "SNF-002", title: "Tile misalignment — Staircase lobby", desc: "Floor tiles not aligned to datum, 3mm discrepancy noted at stair nosing", location: "Level 1 – Staircase Lobby", category: "Finishing", sub: "Gulf Tile & Marble", engineer: "Ravi Kumar", due: "2025-01-28", status: "Open", before: true, after: false, consultant: "NCR raised by SSH on 22-Jan" },
  { id: "s3", pid: "p1", num: "SNF-003", title: "Paint drips — Corridor ceiling", desc: "Emulsion paint runs/drips visible on corridor ceiling, L3", location: "Level 3 – Corridor", category: "Finishing", sub: "Desert Rose Painting", engineer: "Sanjay Verma", due: "2025-02-02", status: "Ready for Review", before: true, after: true, consultant: "" },
  { id: "s4", pid: "p2", num: "SNF-004", title: "MEP penetration not sealed — Level 2 slab", desc: "MEP slab penetrations identified without fire-rated sealant at 4 locations", location: "Level 2 – Slab", category: "MEP", sub: "Al Futtaim MEP", engineer: "Sunil Menon", due: "2025-01-29", status: "Open", before: true, after: false, consultant: "Critical — fire compliance" },
  { id: "s5", pid: "p2", num: "SNF-005", title: "Aluminium frame gap — Window W-12", desc: "6mm gap between aluminium frame and blockwork, not properly sealed", location: "Level 1 – Apartment 107", category: "Architectural", sub: "Al Madina Aluminum", engineer: "Sunil Menon", due: "2025-02-05", status: "Closed", before: true, after: true, consultant: "Accepted" },
];

const INSPECTIONS = [
  { id: "ir1", pid: "p1", num: "WIR/AGBC/001/25", type: "WIR", desc: "Reinforcement inspection before concrete pour — Grade Slab Block A", location: "Ground Floor – Block A", submitted: "2025-01-20", inspection: "2025-01-22", status: "Approved", remarks: "All reinforcement checked, approved with minor comment on cover" },
  { id: "ir2", pid: "p1", num: "WIR/AGBC/002/25", type: "WIR", desc: "Blockwork inspection — Level 3 internal partitions", location: "Level 3 – All Zones", submitted: "2025-01-23", inspection: "2025-01-27", status: "Submitted", remarks: "" },
  { id: "ir3", pid: "p1", num: "MIR/AGBC/001/25", type: "MIR", desc: "Concrete delivery inspection — 35 MPa ready-mix, Emirates Cement", location: "Block A – Ground", submitted: "2025-01-21", inspection: "2025-01-21", status: "Approved", remarks: "Slump 120mm, cube samples taken" },
  { id: "ir4", pid: "p2", num: "WIR/AGBC/003/25", type: "WIR", desc: "First fix MEP inspection before plaster — Level 3", location: "Level 3 – All Apartments", submitted: "2025-01-25", inspection: "2025-01-30", status: "Rejected", remarks: "Incomplete conduit installation in apartments 301-305" },
  { id: "ir5", pid: "p2", num: "WIR/AGBC/004/25", type: "WIR", desc: "Formwork inspection before slab pour — Level 4", location: "Level 4 – Full Floor", submitted: "2025-01-26", inspection: null, status: "Draft", remarks: "" },
];

const DRAWINGS = [
  { id: "d1", pid: "p1", num: "AGBC-001-AR-001", title: "Ground Floor Plan", rev: "C", discipline: "Architectural", received: "2024-11-10", latest: true },
  { id: "d2", pid: "p1", num: "AGBC-001-AR-002", title: "Typical Floor Plan", rev: "B", discipline: "Architectural", received: "2024-11-10", latest: true },
  { id: "d3", pid: "p1", num: "AGBC-001-ST-001", title: "Foundation Layout Plan", rev: "D", discipline: "Structural", received: "2024-12-01", latest: true },
  { id: "d4", pid: "p1", num: "AGBC-001-ST-002", title: "Beam & Column Schedule — Typical Floor", rev: "C", discipline: "Structural", received: "2024-12-01", latest: true },
  { id: "d5", pid: "p1", num: "AGBC-001-ME-001", title: "HVAC Ductwork Layout — Level 1-3", rev: "A", discipline: "MEP", received: "2025-01-05", latest: true },
  { id: "d6", pid: "p2", num: "AGBC-002-AR-001", title: "Ground Floor Plan", rev: "B", discipline: "Architectural", received: "2024-09-15", latest: true },
  { id: "d7", pid: "p2", num: "AGBC-002-ST-001", title: "Structural Foundation Plan", rev: "C", discipline: "Structural", received: "2024-09-20", latest: true },
];

const SUBCONTRACTORS = [
  { id: "sub1", name: "Al Futtaim MEP", contact: "Khalid Al Rashidi", phone: "+971-50-1234567", email: "khalid@alfuttaim.ae", trades: ["MEP","HVAC","Plumbing"], active: true, projects: 2, openTasks: 5, openSnags: 2 },
  { id: "sub2", name: "Green Emirates Contracting", contact: "Suresh Kumar", phone: "+971-55-9876543", email: "suresh@greenuae.com", trades: ["Civil","Masonry","Plastering"], active: true, projects: 2, openTasks: 3, openSnags: 3 },
  { id: "sub3", name: "Gulf Tile & Marble", contact: "Praveen Nair", phone: "+971-50-5551234", email: "praveen@gulftile.com", trades: ["Tiling","Marble","Flooring"], active: true, projects: 1, openTasks: 2, openSnags: 1 },
  { id: "sub4", name: "Al Madina Aluminum", contact: "Mohammed Al Balushi", phone: "+971-56-7778899", email: "info@almadina-al.com", trades: ["Aluminum","Glazing","Cladding"], active: true, projects: 2, openTasks: 4, openSnags: 1 },
  { id: "sub5", name: "Desert Rose Painting", contact: "Raj Sharma", phone: "+971-52-3334455", email: "raj@desertrose.ae", trades: ["Painting","Waterproofing"], active: false, projects: 1, openTasks: 0, openSnags: 1 },
];

const DAILY_REPORTS = [
  { id: "dr1", pid: "p1", date: "2025-01-27", weather: "Sunny", temp: "24°C", manpower: 87, status: "Submitted", preparedBy: "Ravi Kumar", activities: "Grade slab concrete pour Block A completed. Level 3 blockwork in progress. Roof waterproofing inspection done." },
  { id: "dr2", pid: "p1", date: "2025-01-26", weather: "Partly Cloudy", temp: "22°C", manpower: 79, status: "Approved", preparedBy: "Ravi Kumar", activities: "Reinforcement fixing for grade slab. Level 3 MEP first fix conduit. Mock-up preparation for external cladding." },
  { id: "dr3", pid: "p2", date: "2025-01-27", weather: "Sunny", temp: "25°C", manpower: 63, status: "Draft", preparedBy: "Sunil Menon", activities: "Level 4 blockwork 60% complete. Level 3 MEP conduit pending approval before plaster." },
];

// ── UTILITIES ─────────────────────────────────────────────────────────────────
const fmtAED = (n) => `AED ${(n / 1000000).toFixed(2)}M`;
const fmtDate = (d) => d ? new Date(d).toLocaleDateString("en-GB", { day:"2-digit", month:"short", year:"numeric" }) : "—";
const isOverdue = (d) => d && new Date(d) < new Date();

const STATUS_COLORS = {
  // Tasks / Snags
  Open: "bg-red-100 text-red-700 border-red-200",
  "In Progress": "bg-blue-100 text-blue-700 border-blue-200",
  "On Hold": "bg-amber-100 text-amber-700 border-amber-200",
  Completed: "bg-green-100 text-green-700 border-green-200",
  Closed: "bg-slate-100 text-slate-600 border-slate-200",
  "Under Rectification": "bg-orange-100 text-orange-700 border-orange-200",
  "Ready for Review": "bg-purple-100 text-purple-700 border-purple-200",
  Rejected: "bg-red-100 text-red-700 border-red-200",
  // Inspections
  Draft: "bg-slate-100 text-slate-600 border-slate-200",
  Submitted: "bg-blue-100 text-blue-700 border-blue-200",
  Approved: "bg-green-100 text-green-700 border-green-200",
  Resubmitted: "bg-amber-100 text-amber-700 border-amber-200",
  // Projects
  Active: "bg-green-100 text-green-700 border-green-200",
  Tender: "bg-amber-100 text-amber-700 border-amber-200",
  "On Hold": "bg-red-100 text-red-700 border-red-200",
};

const PRIORITY_COLORS = {
  Critical: "bg-red-600 text-white",
  High: "bg-orange-500 text-white",
  Medium: "bg-amber-400 text-white",
  Low: "bg-slate-400 text-white",
};

const DISC_COLORS = {
  Architectural: "bg-blue-100 text-blue-700",
  Structural: "bg-orange-100 text-orange-700",
  MEP: "bg-purple-100 text-purple-700",
  Civil: "bg-green-100 text-green-700",
};

const Badge = ({ text, colorClass }) => (
  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border ${colorClass || STATUS_COLORS[text] || "bg-slate-100 text-slate-600 border-slate-200"}`}>{text}</span>
);

// ── ICONS (SVG inline) ─────────────────────────────────────────────────────────
const Icon = ({ name, cls = "w-5 h-5" }) => {
  const icons = {
    dashboard: <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>,
    projects: <path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>,
    tasks: <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>,
    snags: <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>,
    reports: <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>,
    drawings: <path strokeLinecap="round" strokeLinejoin="round" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"/>,
    inspections: <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>,
    photos: <path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>,
    subs: <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>,
    bell: <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>,
    check: <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/>,
    plus: <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4"/>,
    filter: <path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>,
    search: <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>,
    chart: <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>,
    warn: <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>,
    kanban: <path strokeLinecap="round" strokeLinejoin="round" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"/>,
    list: <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16"/>,
    eye: <><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></>,
    map: <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>,
  };
  return (
    <svg className={cls} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      {icons[name]}
    </svg>
  );
};

// ── SIDEBAR ───────────────────────────────────────────────────────────────────
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

const Sidebar = ({ active, onNav, collapsed }) => (
  <aside className={`${collapsed ? "w-16" : "w-60"} bg-slate-900 text-white flex flex-col transition-all duration-200 shrink-0`}>
    <div className="p-4 border-b border-slate-700 flex items-center gap-3">
      <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center shrink-0">
        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
      </div>
      {!collapsed && <div>
        <div className="text-sm font-bold text-white leading-tight">AGBC</div>
        <div className="text-xs text-slate-400 leading-tight">Site Management</div>
      </div>}
    </div>
    <nav className="flex-1 py-3 overflow-y-auto">
      {NAV.map(n => (
        <button key={n.id} onClick={() => onNav(n.id)}
          className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${active === n.id ? "bg-amber-500 text-white font-semibold" : "text-slate-300 hover:bg-slate-800 hover:text-white"}`}>
          <Icon name={n.icon} cls="w-5 h-5 shrink-0" />
          {!collapsed && <span>{n.label}</span>}
        </button>
      ))}
    </nav>
    <div className="p-4 border-t border-slate-700">
      {!collapsed && <div className="flex items-center gap-2">
        <button onClick={async () => { await supabase.auth.signOut(); window.location.reload(); }}
        className="flex items-center gap-1 text-xs text-slate-500 hover:text-red-600 border border-slate-200 hover:border-red-300 px-3 py-1.5 rounded-lg transition-colors">
        Sign Out
</button>
        <div className="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center text-xs font-bold text-white">AM</div>
        <div>
          <div className="text-xs font-semibold text-white">Ahmed Al Mansoori</div>
          <div className="text-xs text-slate-400">Project Manager</div>
        </div>
      </div>}
    </div>
  </aside>
);

// ── HEADER ────────────────────────────────────────────────────────────────────
const Header = ({ title, onToggle }) => (
  <header className="h-14 bg-white border-b border-slate-200 flex items-center px-4 gap-3 shrink-0">
    <button onClick={onToggle} className="text-slate-400 hover:text-slate-700">
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16"/></svg>
    </button>
    <span className="font-semibold text-slate-800">{title}</span>
    <div className="ml-auto flex items-center gap-2">
      <div className="relative">
        <button className="relative p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg">
          <Icon name="bell" cls="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
      </div>
      <div className="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center text-xs font-bold text-white">AM</div>
    </div>
  </header>
);

// ── STAT CARD ─────────────────────────────────────────────────────────────────
const StatCard = ({ label, value, sub, color, icon }) => (
  <div className={`bg-white rounded-xl border border-slate-200 p-4 flex items-start gap-4`}>
    <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${color}`}>
      <Icon name={icon} cls="w-5 h-5 text-white" />
    </div>
    <div>
      <div className="text-2xl font-bold text-slate-800">{value}</div>
      <div className="text-sm text-slate-500">{label}</div>
      {sub && <div className="text-xs text-slate-400 mt-0.5">{sub}</div>}
    </div>
  </div>
);

// ── DASHBOARD ─────────────────────────────────────────────────────────────────
const Dashboard = () => {
  const totalTasks = TASKS.length;
  const openTasks = TASKS.filter(t => t.status !== "Completed" && t.status !== "Closed").length;
  const overdueTasks = TASKS.filter(t => isOverdue(t.due) && t.status !== "Completed").length;
  const openSnags = SNAGS.filter(s => s.status !== "Closed").length;
  const pendingIR = INSPECTIONS.filter(i => i.status === "Submitted" || i.status === "Draft").length;
  const activeProjects = PROJECTS.filter(p => p.status === "Active").length;

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-800 mb-1">Good morning, Ahmed</h2>
        <p className="text-sm text-slate-500">Tuesday, 28 January 2025 — Dubai, UAE</p>
      </div>

      {/* Stat grid */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard label="Active Projects" value={activeProjects} sub="1 in Tender" color="bg-blue-500" icon="projects" />
        <StatCard label="Open Tasks" value={openTasks} sub={`${totalTasks} total`} color="bg-amber-500" icon="tasks" />
        <StatCard label="Overdue Tasks" value={overdueTasks} sub="Needs attention" color="bg-red-500" icon="warn" />
        <StatCard label="Open Snags" value={openSnags} sub="2 projects" color="bg-orange-500" icon="snags" />
        <StatCard label="Pending IR/WIR" value={pendingIR} sub="Awaiting response" color="bg-purple-500" icon="inspections" />
        <StatCard label="Reports Today" value={2} sub="1 draft pending" color="bg-green-500" icon="reports" />
      </div>

      {/* Project overview table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <h3 className="font-semibold text-slate-800">Project Overview</h3>
          <span className="text-xs text-slate-400">{PROJECTS.length} projects</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                {["Project","Location","Contract Value","Progress","Open Tasks","Snags","Status"].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {PROJECTS.map(p => (
                <tr key={p.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="font-medium text-slate-800 text-xs">{p.number}</div>
                    <div className="text-slate-600 text-xs leading-tight max-w-[180px]">{p.name}</div>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-600">{p.location}</td>
                  <td className="px-4 py-3 text-xs font-mono text-slate-700">{fmtAED(p.value)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                        <div className="h-full bg-amber-500 rounded-full" style={{ width: `${p.progress}%` }}></div>
                      </div>
                      <span className="text-xs text-slate-600">{p.progress}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-xs text-center"><span className={`font-bold ${p.openTasks > 0 ? "text-amber-600" : "text-slate-400"}`}>{p.openTasks}</span></td>
                  <td className="px-4 py-3 text-xs text-center"><span className={`font-bold ${p.openSnags > 0 ? "text-red-600" : "text-slate-400"}`}>{p.openSnags}</span></td>
                  <td className="px-4 py-3"><Badge text={p.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recent tasks */}
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 font-semibold text-slate-800 text-sm">Recent Tasks</div>
          <div className="divide-y divide-slate-100">
            {TASKS.slice(0, 5).map(t => (
              <div key={t.id} className="px-5 py-3 flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full shrink-0 ${t.status === "Completed" ? "bg-green-500" : t.status === "In Progress" ? "bg-blue-500" : t.status === "On Hold" ? "bg-amber-500" : "bg-slate-300"}`}></div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-slate-700 truncate">{t.title}</div>
                  <div className="text-xs text-slate-400">{t.location}</div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Badge text={t.priority} colorClass={PRIORITY_COLORS[t.priority]} />
                  {isOverdue(t.due) && t.status !== "Completed" && <span className="text-xs text-red-500 font-medium">Overdue</span>}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Open snags */}
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 font-semibold text-slate-800 text-sm">Open Snags</div>
          <div className="divide-y divide-slate-100">
            {SNAGS.filter(s => s.status !== "Closed").slice(0, 5).map(s => (
              <div key={s.id} className="px-5 py-3 flex items-center gap-3">
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-semibold text-amber-600">{s.num}</div>
                  <div className="text-sm font-medium text-slate-700 truncate">{s.title}</div>
                  <div className="text-xs text-slate-400">{s.location}</div>
                </div>
                <Badge text={s.status} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ── PROJECTS ──────────────────────────────────────────────────────────────────
const Projects = () => {
  const [search, setSearch] = useState("");
  const dbProjects = useProjects();
  const allProjects = dbProjects.length > 0 ? dbProjects : PROJECTS;
  const filtered = allProjects.filter(p => p.name.toLowerCase().includes(search.toLowerCase()) || p.number.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">Projects</h2>
        <button className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg">
          <Icon name="plus" cls="w-4 h-4" /> New Project
        </button>
      </div>
      <div className="relative max-w-sm">
        <Icon name="search" cls="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search projects..." className="w-full pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {filtered.map(p => (
          <div key={p.id} className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between gap-3 mb-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400 font-mono">{p.number}</span>
                  <Badge text={p.status} />
                </div>
                <h3 className="font-semibold text-slate-800 mt-1 leading-tight">{p.name}</h3>
              </div>
              <div className="text-right shrink-0">
                <div className="text-xs text-slate-400">Contract Value</div>
                <div className="text-sm font-bold text-slate-700">{fmtAED(p.value)}</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-slate-600 mb-4">
              <div className="flex gap-1"><span className="text-slate-400">Plot:</span> {p.plot}</div>
              <div className="flex gap-1"><span className="text-slate-400">Location:</span> {p.location}</div>
              <div className="flex gap-1"><span className="text-slate-400">Client:</span> <span className="truncate">{p.client}</span></div>
              <div className="flex gap-1"><span className="text-slate-400">Consultant:</span> <span className="truncate">{p.consultant}</span></div>
              <div className="flex gap-1"><span className="text-slate-400">PM:</span> {p.pm}</div>
              <div className="flex gap-1"><span className="text-slate-400">End:</span> {fmtDate(p.end)}</div>
            </div>

            <div className="mb-4">
              <div className="flex justify-between text-xs text-slate-500 mb-1">
                <span>Progress</span><span className="font-semibold">{p.progress}%</span>
              </div>
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-amber-500 rounded-full transition-all" style={{ width: `${p.progress}%` }}></div>
              </div>
            </div>

            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1 text-amber-600 font-semibold"><Icon name="tasks" cls="w-3.5 h-3.5" /> {p.openTasks} Tasks</span>
              <span className="flex items-center gap-1 text-red-600 font-semibold"><Icon name="snags" cls="w-3.5 h-3.5" /> {p.openSnags} Snags</span>
              <span className="flex items-center gap-1 text-purple-600 font-semibold"><Icon name="inspections" cls="w-3.5 h-3.5" /> {p.pendingIR} IRs</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ── TASKS ─────────────────────────────────────────────────────────────────────
const TASK_STATUSES = ["Open", "In Progress", "On Hold", "Completed", "Closed"];

const Tasks = () => {
  const [view, setView] = useState("list");
  const [filterStatus, setFilterStatus] = useState("All");
  const [filterProject, setFilterProject] = useState("All");
  const [search, setSearch] = useState("");

  const filtered = TASKS.filter(t => {
    if (filterStatus !== "All" && t.status !== filterStatus) return false;
    if (filterProject !== "All" && t.pid !== filterProject) return false;
    if (search && !t.title.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const projectName = (pid) => PROJECTS.find(p => p.id === pid)?.name || "";

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">Tasks</h2>
        <button className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg">
          <Icon name="plus" cls="w-4 h-4" /> New Task
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative">
          <Icon name="search" cls="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search..." className="pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 w-48" />
        </div>
        <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-400">
          <option value="All">All Status</option>
          {TASK_STATUSES.map(s => <option key={s}>{s}</option>)}
        </select>
        <select value={filterProject} onChange={e => setFilterProject(e.target.value)} className="text-sm border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-400">
          <option value="All">All Projects</option>
          {PROJECTS.map(p => <option key={p.id} value={p.id}>{p.number}</option>)}
        </select>
        <div className="ml-auto flex gap-1 bg-slate-100 p-1 rounded-lg">
          <button onClick={() => setView("list")} className={`p-1.5 rounded ${view === "list" ? "bg-white shadow-sm text-amber-600" : "text-slate-400"}`}><Icon name="list" cls="w-4 h-4" /></button>
          <button onClick={() => setView("kanban")} className={`p-1.5 rounded ${view === "kanban" ? "bg-white shadow-sm text-amber-600" : "text-slate-400"}`}><Icon name="kanban" cls="w-4 h-4" /></button>
        </div>
      </div>

      {view === "list" ? (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                {["Task","Project","Location","Trade","Assignee","Priority","Due Date","Status"].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map(t => (
                <tr key={t.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="font-medium text-slate-800 text-sm max-w-[200px] leading-tight">{t.title}</div>
                    <div className="text-xs text-slate-400 mt-0.5 max-w-[200px] truncate">{t.desc}</div>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">{PROJECTS.find(p => p.id === t.pid)?.number}</td>
                  <td className="px-4 py-3 text-xs text-slate-600 max-w-[120px]">{t.location}</td>
                  <td className="px-4 py-3 text-xs text-slate-600">{t.trade}</td>
                  <td className="px-4 py-3 text-xs text-slate-700 font-medium">{t.assignee}</td>
                  <td className="px-4 py-3"><Badge text={t.priority} colorClass={PRIORITY_COLORS[t.priority]} /></td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-medium ${isOverdue(t.due) && t.status !== "Completed" ? "text-red-600" : "text-slate-600"}`}>{fmtDate(t.due)}</span>
                    {isOverdue(t.due) && t.status !== "Completed" && <div className="text-xs text-red-500">Overdue</div>}
                  </td>
                  <td className="px-4 py-3"><Badge text={t.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && <div className="text-center py-12 text-slate-400">No tasks found</div>}
        </div>
      ) : (
        // Kanban board
        <div className="flex gap-4 overflow-x-auto pb-4">
          {["Open","In Progress","On Hold","Completed"].map(col => {
            const colTasks = filtered.filter(t => t.status === col);
            return (
              <div key={col} className="min-w-[260px] w-[260px] shrink-0">
                <div className={`px-3 py-2 rounded-lg mb-3 flex items-center justify-between ${STATUS_COLORS[col]} border`}>
                  <span className="text-xs font-bold uppercase tracking-wide">{col}</span>
                  <span className="text-xs font-bold bg-white bg-opacity-60 rounded-full px-1.5 py-0.5">{colTasks.length}</span>
                </div>
                <div className="space-y-3">
                  {colTasks.map(t => (
                    <div key={t.id} className="bg-white rounded-xl border border-slate-200 p-4 cursor-pointer hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <p className="text-sm font-semibold text-slate-800 leading-tight">{t.title}</p>
                        <Badge text={t.priority} colorClass={PRIORITY_COLORS[t.priority]} />
                      </div>
                      <div className="text-xs text-slate-500 mb-2">{t.location}</div>
                      <div className="text-xs text-slate-400 mb-3">{t.trade}</div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          <div className="w-5 h-5 rounded-full bg-amber-500 flex items-center justify-center text-white text-xs font-bold">{t.assignee.charAt(0)}</div>
                          <span className="text-xs text-slate-600 truncate max-w-[100px]">{t.assignee}</span>
                        </div>
                        <span className={`text-xs ${isOverdue(t.due) && t.status !== "Completed" ? "text-red-500 font-semibold" : "text-slate-400"}`}>{fmtDate(t.due)}</span>
                      </div>
                    </div>
                  ))}
                  {colTasks.length === 0 && <div className="border-2 border-dashed border-slate-200 rounded-xl p-6 text-center text-xs text-slate-400">No tasks</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// ── SNAG LIST ─────────────────────────────────────────────────────────────────
const Snags = () => {
  const [filterStatus, setFilterStatus] = useState("All");
  const [search, setSearch] = useState("");
  const SNAG_STATUSES = ["Open", "Under Rectification", "Ready for Review", "Closed", "Rejected"];

  const filtered = SNAGS.filter(s => {
    if (filterStatus !== "All" && s.status !== filterStatus) return false;
    if (search && !s.title.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">Snag / Punch List</h2>
        <button className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg">
          <Icon name="plus" cls="w-4 h-4" /> New Snag
        </button>
      </div>

      {/* Summary counts */}
      <div className="flex gap-3 flex-wrap">
        {SNAG_STATUSES.map(s => {
          const count = SNAGS.filter(sn => sn.status === s).length;
          return (
            <button key={s} onClick={() => setFilterStatus(filterStatus === s ? "All" : s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors ${filterStatus === s ? (STATUS_COLORS[s] || "bg-slate-200") : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"}`}>
              {s} ({count})
            </button>
          );
        })}
      </div>

      <div className="relative max-w-sm">
        <Icon name="search" cls="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search snags..." className="w-full pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" />
      </div>

      <div className="space-y-3">
        {filtered.map(s => (
          <div key={s.id} className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-mono font-bold text-amber-600">{s.num}</span>
                  <Badge text={s.category} colorClass={`bg-slate-100 text-slate-600 border-slate-200`} />
                </div>
                <h3 className="font-semibold text-slate-800 mb-1">{s.title}</h3>
                <p className="text-sm text-slate-500 mb-2">{s.desc}</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-1 text-xs text-slate-600">
                  <div><span className="text-slate-400">Location: </span>{s.location}</div>
                  <div><span className="text-slate-400">Sub: </span>{s.sub}</div>
                  <div><span className="text-slate-400">Engineer: </span>{s.engineer}</div>
                  <div><span className={`${isOverdue(s.due) && s.status !== "Closed" ? "text-red-500 font-semibold" : "text-slate-400"}`}>Due: </span>{fmtDate(s.due)}</div>
                </div>
                {s.consultant && <div className="mt-2 text-xs bg-amber-50 border border-amber-200 text-amber-700 px-3 py-1.5 rounded-lg">{s.consultant}</div>}
              </div>
              <div className="flex flex-col items-end gap-2 shrink-0">
                <Badge text={s.status} />
                <div className="flex gap-2 text-xs text-slate-400">
                  <span className={`flex items-center gap-0.5 ${s.before ? "text-green-600" : "text-slate-300"}`}><Icon name="photos" cls="w-3.5 h-3.5" /> Before</span>
                  <span className={`flex items-center gap-0.5 ${s.after ? "text-green-600" : "text-slate-300"}`}><Icon name="photos" cls="w-3.5 h-3.5" /> After</span>
                </div>
              </div>
            </div>
          </div>
        ))}
        {filtered.length === 0 && <div className="text-center py-12 text-slate-400 bg-white rounded-xl border border-slate-200">No snags found</div>}
      </div>
    </div>
  );
};

// ── INSPECTIONS ───────────────────────────────────────────────────────────────
const Inspections = () => {
  const [filterStatus, setFilterStatus] = useState("All");
  const IR_STATUSES = ["Draft","Submitted","Approved","Rejected","Resubmitted"];

  const filtered = INSPECTIONS.filter(i => filterStatus === "All" || i.status === filterStatus);
  const projectName = (pid) => PROJECTS.find(p => p.id === pid)?.number || "";

  const typeColors = { WIR: "bg-blue-100 text-blue-700", MIR: "bg-green-100 text-green-700", IR: "bg-purple-100 text-purple-700", MSIR: "bg-orange-100 text-orange-700" };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">Inspection Request Tracker</h2>
        <button className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg">
          <Icon name="plus" cls="w-4 h-4" /> New IR/WIR
        </button>
      </div>

      <div className="flex gap-2 flex-wrap">
        {["All", ...IR_STATUSES].map(s => {
          const count = s === "All" ? INSPECTIONS.length : INSPECTIONS.filter(i => i.status === s).length;
          return (
            <button key={s} onClick={() => setFilterStatus(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors ${filterStatus === s ? "bg-amber-500 text-white border-amber-500" : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"}`}>
              {s} ({count})
            </button>
          );
        })}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              {["IR Number","Type","Description","Project","Location","Submitted","Inspection Date","Status","Remarks"].map(h => (
                <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map(i => (
              <tr key={i.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-mono text-xs font-semibold text-amber-700">{i.num}</td>
                <td className="px-4 py-3"><span className={`text-xs font-bold px-2 py-0.5 rounded-full ${typeColors[i.type] || "bg-slate-100 text-slate-600"}`}>{i.type}</span></td>
                <td className="px-4 py-3 text-xs text-slate-700 max-w-[180px] leading-tight">{i.desc}</td>
                <td className="px-4 py-3 text-xs text-slate-500">{projectName(i.pid)}</td>
                <td className="px-4 py-3 text-xs text-slate-600 max-w-[100px]">{i.location}</td>
                <td className="px-4 py-3 text-xs text-slate-600 whitespace-nowrap">{fmtDate(i.submitted)}</td>
                <td className="px-4 py-3 text-xs text-slate-600 whitespace-nowrap">{i.inspection ? fmtDate(i.inspection) : <span className="text-slate-300">TBD</span>}</td>
                <td className="px-4 py-3"><Badge text={i.status} /></td>
                <td className="px-4 py-3 text-xs text-slate-500 max-w-[140px] leading-tight">{i.remarks || <span className="text-slate-300">—</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ── DRAWING REGISTER ──────────────────────────────────────────────────────────
const Drawings = () => {
  const [filterDisc, setFilterDisc] = useState("All");
  const [search, setSearch] = useState("");
  const DISCIPLINES = ["Architectural","Structural","MEP","Civil"];

  const filtered = DRAWINGS.filter(d => {
    if (filterDisc !== "All" && d.discipline !== filterDisc) return false;
    if (search && !(d.num + d.title).toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">Drawing Register</h2>
        <button className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg">
          <Icon name="plus" cls="w-4 h-4" /> Upload Drawing
        </button>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative">
          <Icon name="search" cls="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search drawings..." className="pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 w-48" />
        </div>
        <div className="flex gap-1">
          {["All",...DISCIPLINES].map(d => (
            <button key={d} onClick={() => setFilterDisc(d)}
              className={`px-3 py-2 text-xs font-semibold rounded-lg border transition-colors ${filterDisc === d ? "bg-amber-500 text-white border-amber-500" : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"}`}>
              {d}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              {["Drawing No.","Title","Discipline","Rev","Project","Date Received","Latest",""].map(h => (
                <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map(d => (
              <tr key={d.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-mono text-xs font-semibold text-slate-700">{d.num}</td>
                <td className="px-4 py-3 text-sm text-slate-800 font-medium">{d.title}</td>
                <td className="px-4 py-3"><span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${DISC_COLORS[d.discipline] || "bg-slate-100 text-slate-600"}`}>{d.discipline}</span></td>
                <td className="px-4 py-3"><span className="font-mono text-xs font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">Rev {d.rev}</span></td>
                <td className="px-4 py-3 text-xs text-slate-500">{PROJECTS.find(p => p.id === d.pid)?.number}</td>
                <td className="px-4 py-3 text-xs text-slate-600 whitespace-nowrap">{fmtDate(d.received)}</td>
                <td className="px-4 py-3">
                  {d.latest ? <span className="flex items-center gap-1 text-xs text-green-600 font-semibold"><Icon name="check" cls="w-3.5 h-3.5" />Current</span> : <span className="text-xs text-slate-400">Superseded</span>}
                </td>
                <td className="px-4 py-3">
                  <button className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 font-medium">
                    <Icon name="eye" cls="w-3.5 h-3.5" /> View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ── DAILY REPORTS ─────────────────────────────────────────────────────────────
const DailyReports = () => {
  const [showForm, setShowForm] = useState(false);
  const [selectedDate] = useState("2025-01-27");

  if (showForm) {
    return (
      <div className="p-6 space-y-5">
        <div className="flex items-center gap-3">
          <button onClick={() => setShowForm(false)} className="text-slate-400 hover:text-slate-700 text-sm flex items-center gap-1">
            ← Back
          </button>
          <h2 className="text-xl font-bold text-slate-800">New Daily Site Report</h2>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5 max-w-3xl space-y-5">
          <div className="grid grid-cols-2 gap-4">
            {[["Date","date","2025-01-28"],["Project","text","AGBC-2024-001"],["Weather","text","Sunny"],["Temperature","text","24°C"],["Total Manpower","number","87"]].map(([label, type, def]) => (
              <div key={label}>
                <label className="text-xs font-semibold text-slate-600 block mb-1">{label}</label>
                <input type={type} defaultValue={def} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400" />
              </div>
            ))}
          </div>
          {["Work Activities Today","Work Completed","Issues / Delays","Inspections Done","Materials Received","Safety Observations"].map(field => (
            <div key={field}>
              <label className="text-xs font-semibold text-slate-600 block mb-1">{field}</label>
              <textarea rows={3} className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 resize-none" placeholder={`Enter ${field.toLowerCase()}...`} />
            </div>
          ))}
          <div>
            <label className="text-xs font-semibold text-slate-600 block mb-1">Site Photos</label>
            <div className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center cursor-pointer hover:border-amber-400 hover:bg-amber-50 transition-colors">
              <Icon name="photos" cls="w-8 h-8 mx-auto text-slate-300 mb-2" />
              <div className="text-sm text-slate-400">Click to upload site photos</div>
            </div>
          </div>
          <div className="flex gap-3">
            <button className="bg-amber-500 hover:bg-amber-600 text-white font-semibold text-sm px-6 py-2.5 rounded-lg">Submit Report</button>
            <button className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm px-6 py-2.5 rounded-lg">Save Draft</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">Daily Site Reports</h2>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg">
          <Icon name="plus" cls="w-4 h-4" /> New Report
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {DAILY_REPORTS.map(r => (
          <div key={r.id} className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between gap-3 mb-3">
              <div>
                <div className="font-bold text-slate-800">{fmtDate(r.date)}</div>
                <div className="text-xs text-slate-500">{PROJECTS.find(p => p.id === r.pid)?.name}</div>
              </div>
              <Badge text={r.status} />
            </div>
            <div className="grid grid-cols-3 gap-3 mb-3 text-center">
              <div className="bg-blue-50 rounded-lg p-2">
                <div className="text-lg font-bold text-blue-700">{r.manpower}</div>
                <div className="text-xs text-blue-500">Manpower</div>
              </div>
              <div className="bg-amber-50 rounded-lg p-2">
                <div className="text-sm font-bold text-amber-700">{r.weather}</div>
                <div className="text-xs text-amber-500">Weather</div>
              </div>
              <div className="bg-green-50 rounded-lg p-2">
                <div className="text-sm font-bold text-green-700">{r.temp}</div>
                <div className="text-xs text-green-500">Temp</div>
              </div>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed mb-3">{r.activities}</p>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Prepared by: <strong className="text-slate-600">{r.preparedBy}</strong></span>
              <button className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-medium">
                <Icon name="eye" cls="w-3.5 h-3.5" /> View Full Report
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ── SUBCONTRACTORS ────────────────────────────────────────────────────────────
const Subcontractors = () => (
  <div className="p-6 space-y-4">
    <div className="flex items-center justify-between">
      <h2 className="text-xl font-bold text-slate-800">Subcontractors</h2>
      <button className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg">
        <Icon name="plus" cls="w-4 h-4" /> Add Subcontractor
      </button>
    </div>
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
      {SUBCONTRACTORS.map(s => (
        <div key={s.id} className={`bg-white rounded-xl border p-4 hover:shadow-md transition-shadow ${s.active ? "border-slate-200" : "border-slate-200 opacity-60"}`}>
          <div className="flex items-start justify-between gap-3 mb-3">
            <div>
              <div className="font-semibold text-slate-800">{s.name}</div>
              <div className="text-xs text-slate-500">{s.contact}</div>
            </div>
            <span className={`px-2 py-0.5 text-xs font-bold rounded-full border ${s.active ? "bg-green-100 text-green-700 border-green-200" : "bg-slate-100 text-slate-500 border-slate-200"}`}>{s.active ? "Active" : "Inactive"}</span>
          </div>
          <div className="flex flex-wrap gap-1 mb-3">
            {s.trades.map(t => <span key={t} className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">{t}</span>)}
          </div>
          <div className="grid grid-cols-3 gap-3 text-center text-xs mb-3">
            <div className="bg-slate-50 rounded-lg p-2">
              <div className="font-bold text-slate-800">{s.projects}</div>
              <div className="text-slate-400">Projects</div>
            </div>
            <div className="bg-amber-50 rounded-lg p-2">
              <div className="font-bold text-amber-700">{s.openTasks}</div>
              <div className="text-amber-500">Open Tasks</div>
            </div>
            <div className="bg-red-50 rounded-lg p-2">
              <div className="font-bold text-red-600">{s.openSnags}</div>
              <div className="text-red-400">Open Snags</div>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs text-slate-500">
            <a href={`tel:${s.phone}`} className="hover:text-blue-600">{s.phone}</a>
            <a href={`mailto:${s.email}`} className="hover:text-blue-600 truncate">{s.email}</a>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// ── PHOTOS ────────────────────────────────────────────────────────────────────
const Photos = () => {
  const colors = ["bg-slate-200","bg-blue-100","bg-amber-100","bg-green-100","bg-purple-100","bg-red-100","bg-orange-100","bg-teal-100"];
  const mockPhotos = [
    { id:1, caption:"Grade slab concrete pour — Block A", area:"Ground Floor Block A", date:"27 Jan 2025", trade:"Civil / Structural", color:"bg-blue-100" },
    { id:2, caption:"Level 3 blockwork in progress", area:"Level 3 All Zones", date:"27 Jan 2025", trade:"Civil / Masonry", color:"bg-amber-100" },
    { id:3, caption:"HVAC ductwork installation — Level 2", area:"Level 2 Zone C", date:"26 Jan 2025", trade:"MEP / HVAC", color:"bg-green-100" },
    { id:4, caption:"External scaffolding — North Elevation", area:"External North", date:"25 Jan 2025", trade:"Civil", color:"bg-purple-100" },
    { id:5, caption:"Floor tile installation — Level 1 lobby", area:"Level 1 Lobby", date:"24 Jan 2025", trade:"Finishing / Tiling", color:"bg-orange-100" },
    { id:6, caption:"Roof waterproofing — main roof", area:"Roof Level", date:"22 Jan 2025", trade:"Civil / Waterproofing", color:"bg-teal-100" },
  ];
  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800">Progress Photos</h2>
        <button className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-4 py-2 rounded-lg">
          <Icon name="plus" cls="w-4 h-4" /> Upload Photos
        </button>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
        {mockPhotos.map(p => (
          <div key={p.id} className="bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer group">
            <div className={`${p.color} h-40 flex items-center justify-center relative overflow-hidden`}>
              <Icon name="photos" cls="w-10 h-10 text-slate-400" />
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-colors"></div>
            </div>
            <div className="p-3">
              <div className="text-xs font-semibold text-slate-700 leading-tight mb-1">{p.caption}</div>
              <div className="text-xs text-slate-400">{p.area}</div>
              <div className="flex items-center justify-between mt-2 text-xs text-slate-400">
                <span>{p.date}</span>
                <span className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-500">{p.trade}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ── APP ROOT ──────────────────────────────────────────────────────────────────
const PAGE_TITLES = {
  dashboard: "Dashboard",
  projects: "Projects",
  tasks: "Task Management",
  snags: "Snag / Punch List",
  reports: "Daily Site Reports",
  inspections: "Inspection Request Tracker",
  drawings: "Drawing Register",
  photos: "Progress Photos",
  subcontractors: "Subcontractors",
};

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [user, setUser] = useState(null); 
  const [collapsed, setCollapsed] = useState(false);
  if (!user) return <Login onLogin={() => setUser(true)} />;
  
  const renderPage = () => {
    switch(page) {
      case "dashboard": return <Dashboard />;
      case "projects": return <Projects />;
      case "tasks": return <Tasks />;
      case "snags": return <Snags />;
      case "reports": return <DailyReports />;
      case "inspections": return <Inspections />;
      case "drawings": return <Drawings />;
      case "photos": return <Photos />;
      case "subcontractors": return <Subcontractors />;
      default: return (
        <div className="p-12 text-center text-slate-400">
          <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Icon name="dashboard" cls="w-8 h-8 text-slate-300" />
          </div>
          <p className="text-lg font-semibold">Module coming soon</p>
          <p className="text-sm mt-1">This module is under development</p>
        </div>
      );
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans text-slate-800">
      <style>{`
        * { box-sizing: border-box; }
        body { margin: 0; font-family: 'Inter', system-ui, sans-serif; }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 99px; }
      `}</style>
      <Sidebar active={page} onNav={setPage} collapsed={collapsed} />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header title={PAGE_TITLES[page] || "AGBC"} onToggle={() => setCollapsed(!collapsed)} />
        <main className="flex-1 overflow-y-auto">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}

