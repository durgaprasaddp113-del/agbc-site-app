import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# ══════════════════════════════════════════════════════════════════
# FIX 1: Add recharts import at top of file
# ══════════════════════════════════════════════════════════════════
old_import = 'import Login from "./Login";'
new_import = '''import Login from "./Login";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, RadialBarChart, RadialBar } from "recharts";'''
if old_import in content and 'from "recharts"' not in content:
    content = content.replace(old_import, new_import, 1)
    changes += 1
    print("FIX 1: Recharts import added")

# ══════════════════════════════════════════════════════════════════
# FIX 2: Update ACTIVITIES list with all required activities
# ══════════════════════════════════════════════════════════════════
old_activities = '''const ACTIVITIES = ["Excavation","Shoring","Piling","Concrete","Steel Reinforcement","Block Work","Plaster","MEP First Fix","MEP Second Fix","Waterproofing","Tiling","Painting","Doors & Windows","Lift Installation","Garbage Chute Installation","External Works","Landscaping","Testing & Commissioning","Other (Custom)"];'''
new_activities = '''const ACTIVITIES = ["Mobilization","Excavation","Shoring / Piling","Concrete Works","Steel Reinforcement","Block Work / Masonry","Waterproofing","Plaster Work","Electrical Work","Plumbing Work","HVAC Work","Fire Fighting","Tiles","False Ceiling","Painting","Joinery / Carpentry","Doors & Windows","Aluminum & Glazing","External Works","Landscaping","Lift Installation","Testing & Commissioning","Other (Custom)"];
const PROG_UNITS = ["NOS","CUM","SQM","RM","KG","TON","Lumpsum"];'''
if old_activities in content:
    content = content.replace(old_activities, new_activities, 1)
    changes += 1
    print("FIX 2: ACTIVITIES + PROG_UNITS updated")

# ══════════════════════════════════════════════════════════════════
# FIX 3: Update EMPTY_PG with new fields
# ══════════════════════════════════════════════════════════════════
old_empty = 'const EMPTY_PG = { pid:"",activity:"",recordDate:"",plannedStart:"",plannedEnd:"",actualStart:"",actualEnd:"",pct:0,status:"Not Started",remarks:"" };'
new_empty = 'const EMPTY_PG = { pid:"",activity:"",customActivity:"",unit:"NOS",actualQty:"",workDoneQty:"",balanceQty:"",recordDate:"",plannedStart:"",plannedEnd:"",actualStart:"",actualEnd:"",pct:0,status:"Not Started",remarks:"" };'
if old_empty in content:
    content = content.replace(old_empty, new_empty, 1)
    changes += 1
    print("FIX 3: EMPTY_PG updated with qty fields")
else:
    # fallback for original
    old_empty2 = 'const EMPTY_PG = { pid:"",activity:"",plannedStart:"",plannedEnd:"",actualStart:"",actualEnd:"",pct:0,status:"Not Started",remarks:"" };'
    if old_empty2 in content:
        content = content.replace(old_empty2, new_empty, 1)
        changes += 1
        print("FIX 3b: EMPTY_PG (original) updated")

# ══════════════════════════════════════════════════════════════════
# FIX 4: Update useProjectProgress hook map
# ══════════════════════════════════════════════════════════════════
old_map = '''      activity: p.activity_name || "", recordDate: p.record_date || "",\n      plannedStart: p.planned_start_date'''
new_map = '''      activity: p.activity_name || "", customActivity: p.custom_activity || "",
      unit: p.unit || "NOS", actualQty: Number(p.actual_qty)||0,
      workDoneQty: Number(p.work_done_qty)||0, balanceQty: Number(p.balance_qty)||0,
      recordDate: p.record_date || "",
      plannedStart: p.planned_start_date'''
if old_map in content:
    content = content.replace(old_map, new_map, 1)
    changes += 1
    print("FIX 4: useProjectProgress map updated")
else:
    old_map2 = '      activity: p.activity_name || "",\n      plannedStart: p.planned_start_date'
    new_map2 = '''      activity: p.activity_name || "", customActivity: p.custom_activity || "",
      unit: p.unit || "NOS", actualQty: Number(p.actual_qty)||0,
      workDoneQty: Number(p.work_done_qty)||0, balanceQty: Number(p.balance_qty)||0,
      recordDate: p.record_date || "",
      plannedStart: p.planned_start_date'''
    if old_map2 in content:
        content = content.replace(old_map2, new_map2, 1)
        changes += 1
        print("FIX 4b: useProjectProgress map updated (fallback)")

# ══════════════════════════════════════════════════════════════════
# FIX 5: Update useProjectProgress add function
# ══════════════════════════════════════════════════════════════════
old_add = '''      project_id: f.pid, activity_name: f.activity, record_date: f.recordDate || null,\n      planned_start_date: f.plannedStart'''
new_add = '''      project_id: f.pid,
      activity_name: f.unit==="Other (Custom)"&&f.customActivity ? f.customActivity : f.activity,
      custom_activity: f.customActivity || null,
      unit: f.unit || "NOS",
      actual_qty: f.unit==="Lumpsum" ? null : (Number(f.actualQty)||0),
      work_done_qty: f.unit==="Lumpsum" ? null : (Number(f.workDoneQty)||0),
      balance_qty: f.unit==="Lumpsum" ? null : Math.max(0,(Number(f.actualQty)||0)-(Number(f.workDoneQty)||0)),
      record_date: f.recordDate || null,
      planned_start_date: f.plannedStart'''
if old_add in content:
    content = content.replace(old_add, new_add, 1)
    changes += 1
    print("FIX 5: useProjectProgress add updated")
else:
    old_add2 = '      project_id: f.pid, activity_name: f.activity,\n      planned_start_date: f.plannedStart'
    new_add2 = '''      project_id: f.pid,
      activity_name: f.unit==="Other (Custom)"&&f.customActivity ? f.customActivity : f.activity,
      custom_activity: f.customActivity || null,
      unit: f.unit || "NOS",
      actual_qty: f.unit==="Lumpsum" ? null : (Number(f.actualQty)||0),
      work_done_qty: f.unit==="Lumpsum" ? null : (Number(f.workDoneQty)||0),
      balance_qty: f.unit==="Lumpsum" ? null : Math.max(0,(Number(f.actualQty)||0)-(Number(f.workDoneQty)||0)),
      record_date: f.recordDate || null,
      planned_start_date: f.plannedStart'''
    if old_add2 in content:
        content = content.replace(old_add2, new_add2, 1)
        changes += 1
        print("FIX 5b: useProjectProgress add updated (fallback)")

# ══════════════════════════════════════════════════════════════════
# FIX 6: Update useProjectProgress update function
# ══════════════════════════════════════════════════════════════════
old_upd = '''      activity_name: f.activity, record_date: f.recordDate || null,\n      planned_start_date: f.plannedStart'''
new_upd = '''      activity_name: f.unit==="Other (Custom)"&&f.customActivity ? f.customActivity : f.activity,
      custom_activity: f.customActivity || null,
      unit: f.unit || "NOS",
      actual_qty: f.unit==="Lumpsum" ? null : (Number(f.actualQty)||0),
      work_done_qty: f.unit==="Lumpsum" ? null : (Number(f.workDoneQty)||0),
      balance_qty: f.unit==="Lumpsum" ? null : Math.max(0,(Number(f.actualQty)||0)-(Number(f.workDoneQty)||0)),
      record_date: f.recordDate || null,
      planned_start_date: f.plannedStart'''
if old_upd in content:
    content = content.replace(old_upd, new_upd, 1)
    changes += 1
    print("FIX 6: useProjectProgress update fn updated")

# ══════════════════════════════════════════════════════════════════
# FIX 7: Update openEditPg to include new fields
# ══════════════════════════════════════════════════════════════════
old_edit = "setSelPg(pg); setPgForm({pid:pg.pid,activity:pg.activity,recordDate:pg.recordDate||'',plannedStart:pg.plannedStart,plannedEnd:pg.plannedEnd,actualStart:pg.actualStart,actualEnd:pg.actualEnd,pct:pg.pct,status:pg.status,remarks:pg.remarks});"
new_edit = "setSelPg(pg); setPgForm({pid:pg.pid,activity:pg.activity,customActivity:pg.customActivity||'',unit:pg.unit||'NOS',actualQty:String(pg.actualQty||''),workDoneQty:String(pg.workDoneQty||''),balanceQty:String(pg.balanceQty||''),recordDate:pg.recordDate||'',plannedStart:pg.plannedStart,plannedEnd:pg.plannedEnd,actualStart:pg.actualStart,actualEnd:pg.actualEnd,pct:pg.pct,status:pg.status,remarks:pg.remarks});"
if old_edit in content:
    content = content.replace(old_edit, new_edit, 1)
    changes += 1
    print("FIX 7: openEditPg updated")
else:
    old_edit2 = "setSelPg(pg); setPgForm({pid:pg.pid,activity:pg.activity,plannedStart:pg.plannedStart,plannedEnd:pg.plannedEnd,actualStart:pg.actualStart,actualEnd:pg.actualEnd,pct:pg.pct,status:pg.status,remarks:pg.remarks});"
    if old_edit2 in content:
        content = content.replace(old_edit2, new_edit, 1)
        changes += 1
        print("FIX 7b: openEditPg updated (fallback)")

# ══════════════════════════════════════════════════════════════════
# FIX 8: Update getOverall to use qty-based calc
# ══════════════════════════════════════════════════════════════════
old_overall = '''  const getOverall = (pid) => {
    const items = progressItems.filter(p => p.pid === pid);
    if (!items.length) return 0;
    return Math.round(items.reduce((a,i) => a + (Number(i.pct)||0), 0) / items.length);
  };'''
new_overall = '''  const getOverall = (pid) => {
    const items = progressItems.filter(p => p.pid === pid);
    if (!items.length) return 0;
    // Use qty-based calculation when actual qty exists
    const withQty = items.filter(i => i.unit !== "Lumpsum" && (Number(i.actualQty)||0) > 0);
    if (withQty.length > 0) {
      const totalActual = withQty.reduce((s,i) => s + (Number(i.actualQty)||0), 0);
      const totalDone   = withQty.reduce((s,i) => s + (Number(i.workDoneQty)||0), 0);
      const qtyPct      = totalActual > 0 ? Math.round((totalDone/totalActual)*100) : 0;
      // Also include lumpsum items
      const lumpItems = items.filter(i => i.unit === "Lumpsum" || (Number(i.actualQty)||0) === 0);
      const lumpAvg   = lumpItems.length > 0 ? lumpItems.reduce((s,i) => s+(Number(i.pct)||0), 0)/lumpItems.length : null;
      if (lumpAvg !== null) return Math.round((qtyPct + lumpAvg) / 2);
      return Math.min(100, qtyPct);
    }
    return Math.round(items.reduce((a,i) => a + (Number(i.pct)||0), 0) / items.length);
  };'''
if old_overall in content:
    content = content.replace(old_overall, new_overall, 1)
    changes += 1
    print("FIX 8: getOverall updated with qty-based calc")

# ══════════════════════════════════════════════════════════════════
# FIX 9: Insert ProgressDashboard component before Projects component
# ══════════════════════════════════════════════════════════════════
PROGRESS_DASHBOARD = '''
// ─────────────────────────────────────────────────────────────────────────────
// PROGRESS DASHBOARD COMPONENT — Charts + Summary Table
// ─────────────────────────────────────────────────────────────────────────────
const ProgressDashboard = ({ items, projectName, overallPct }) => {
  if (!items || items.length === 0) return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-8 text-center text-slate-400 text-sm">
      📊 No activities yet. Add activities above to see progress charts.
    </div>
  );

  // Build chart data
  const chartData = items.map(i => {
    const isLump   = i.unit === "Lumpsum";
    const actual   = isLump ? 100 : (Number(i.actualQty)||0);
    const done     = isLump ? (Number(i.pct)||0) : (Number(i.workDoneQty)||0);
    const balance  = Math.max(0, actual - done);
    const pct      = isLump ? (Number(i.pct)||0) : (actual > 0 ? Math.min(100,Math.round((done/actual)*100)) : (Number(i.pct)||0));
    const shortName = (i.activity||"").length > 11 ? (i.activity||"").slice(0,11)+"…" : (i.activity||"");
    return { name: shortName, fullName: i.activity||"", actual, done, balance, pct, remaining: 100-pct, unit: i.unit||"NOS", status: i.status, isLump };
  }).filter(d => d.actual > 0 || d.pct > 0);

  if (chartData.length === 0) return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-8 text-center text-slate-400 text-sm">
      📊 Enter quantities or percentages to see charts.
    </div>
  );

  const STS_CLR = {"Completed":"#10b981","In Progress":"#3b82f6","On Hold":"#f59e0b","Not Started":"#94a3b8"};
  const PCT_CLR = (p) => p>=100?"#10b981":p>=60?"#3b82f6":p>=30?"#f59e0b":"#ef4444";

  // Summary stats
  const totalAct  = chartData.filter(d=>!d.isLump).reduce((s,d)=>s+d.actual,0);
  const totalDone = chartData.filter(d=>!d.isLump).reduce((s,d)=>s+d.done,0);
  const totalBal  = chartData.filter(d=>!d.isLump).reduce((s,d)=>s+d.balance,0);

  return (
    <div className="space-y-4 mt-4">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          {l:"Overall Progress",  v:overallPct+"%",   c:"from-blue-600 to-blue-500",   icon:"📈"},
          {l:"Activities Done",   v:items.filter(i=>i.status==="Completed").length+"/"+items.length, c:"from-green-600 to-green-500", icon:"✅"},
          {l:"In Progress",       v:items.filter(i=>i.status==="In Progress").length, c:"from-amber-500 to-amber-400", icon:"⚙️"},
          {l:"Not Started",       v:items.filter(i=>i.status==="Not Started").length, c:"from-red-500 to-red-400", icon:"⏳"},
        ].map(c=>(
          <div key={c.l} className={`bg-gradient-to-br ${c.c} text-white rounded-xl p-3 shadow-sm`}>
            <div className="flex items-center justify-between">
              <div><div className="text-2xl font-black">{c.v}</div><div className="text-xs opacity-80 mt-0.5">{c.l}</div></div>
              <span className="text-2xl opacity-80">{c.icon}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Overall progress bar */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-700 rounded-xl p-4 text-white">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-bold">Overall Project Progress — {projectName}</span>
          <span className="text-2xl font-black text-amber-400">{overallPct}%</span>
        </div>
        <div className="h-4 bg-white/20 rounded-full overflow-hidden">
          <div className="h-4 rounded-full transition-all duration-700"
            style={{width:overallPct+"%", background:"linear-gradient(90deg,#f59e0b,#10b981)"}}/>
        </div>
        <div className="flex justify-between text-xs text-slate-400 mt-1">
          <span>0%</span><span>Work Done: {overallPct}%</span><span>Balance: {100-overallPct}%</span><span>100%</span>
        </div>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

        {/* Qty Bar Chart */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3">📦 Quantity Progress (Actual vs Done vs Balance)</div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={chartData} margin={{top:5,right:5,left:-10,bottom:40}} barCategoryGap="20%">
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false}/>
              <XAxis dataKey="name" tick={{fontSize:9,fill:"#64748b"}} angle={-35} textAnchor="end" interval={0} height={55}/>
              <YAxis tick={{fontSize:9,fill:"#94a3b8"}}/>
              <Tooltip
                contentStyle={{fontSize:"11px",borderRadius:"8px",border:"1px solid #e2e8f0"}}
                formatter={(v,n,p)=>[`${p.payload.isLump?v+"%":v+" "+p.payload.unit}`,n]}
                labelFormatter={(l,items)=>items[0]?.payload?.fullName||l}
              />
              <Legend iconSize={8} wrapperStyle={{fontSize:"10px",paddingTop:"8px"}}/>
              <Bar dataKey="actual"  name="Actual Qty"   fill="#3b82f6" radius={[3,3,0,0]} maxBarSize={22}/>
              <Bar dataKey="done"    name="Work Done"    fill="#10b981" radius={[3,3,0,0]} maxBarSize={22}/>
              <Bar dataKey="balance" name="Balance"      fill="#ef4444" radius={[3,3,0,0]} maxBarSize={22}/>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Horizontal % Bar Chart */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3">📊 Work Done % vs Remaining % per Activity</div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={chartData} layout="vertical" margin={{top:5,right:30,left:5,bottom:5}} barSize={14}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false}/>
              <XAxis type="number" domain={[0,100]} tick={{fontSize:9,fill:"#94a3b8"}} tickFormatter={v=>v+"%"}/>
              <YAxis type="category" dataKey="name" tick={{fontSize:9,fill:"#64748b"}} width={68}/>
              <Tooltip
                contentStyle={{fontSize:"11px",borderRadius:"8px",border:"1px solid #e2e8f0"}}
                formatter={(v,n,p)=>[v+"%",n]}
                labelFormatter={(l,items)=>items[0]?.payload?.fullName||l}
              />
              <Legend iconSize={8} wrapperStyle={{fontSize:"10px"}}/>
              <Bar dataKey="pct"       name="Work Done %"  stackId="a" radius={[0,0,0,0]}>
                {chartData.map((e,i)=><Cell key={i} fill={PCT_CLR(e.pct)}/>)}
              </Bar>
              <Bar dataKey="remaining" name="Remaining %" stackId="a" fill="#f1f5f9" radius={[0,3,3,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Summary Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-x-auto">
        <div className="px-4 py-3 bg-gradient-to-r from-amber-50 to-slate-50 border-b border-slate-200">
          <span className="font-bold text-slate-800 text-sm">📋 Activity Progress Summary</span>
          {totalAct > 0 && <span className="text-xs text-slate-500 ml-2">Total Actual: {totalAct.toLocaleString()} | Done: {totalDone.toLocaleString()} | Balance: {totalBal.toLocaleString()}</span>}
        </div>
        <table className="w-full text-xs min-w-[700px]">
          <thead className="bg-amber-500">
            <tr>{["#","Activity","Unit","Actual Qty","Work Done","Balance Qty","Work Done %","Remaining %","Status"].map(h=>(
              <th key={h} className="px-3 py-2.5 text-left font-bold text-white">{h}</th>
            ))}</tr>
          </thead>
          <tbody>
            {chartData.map((r,i)=>(
              <tr key={i} className={`border-t border-slate-100 ${i%2===0?"bg-white":"bg-slate-50/50"}`}>
                <td className="px-3 py-2 text-slate-400 text-center">{i+1}</td>
                <td className="px-3 py-2 font-semibold text-slate-800">{r.fullName}</td>
                <td className="px-3 py-2"><span className="bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-semibold">{r.unit}</span></td>
                <td className="px-3 py-2 text-center font-bold text-slate-700">{r.isLump?"L/S":r.actual.toLocaleString()}</td>
                <td className="px-3 py-2 text-center font-bold text-green-700">{r.isLump?r.pct+"%":r.done.toLocaleString()}</td>
                <td className="px-3 py-2 text-center font-bold text-red-600">{r.isLump?(100-r.pct)+"%":r.balance.toLocaleString()}</td>
                <td className="px-3 py-2">
                  <div className="flex items-center gap-1.5">
                    <div className="flex-1 h-3 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-3 rounded-full transition-all" style={{width:r.pct+"%",backgroundColor:PCT_CLR(r.pct)}}/>
                    </div>
                    <span className="font-black w-8 text-right" style={{color:PCT_CLR(r.pct)}}>{r.pct}%</span>
                  </div>
                </td>
                <td className="px-3 py-2">
                  <div className="flex items-center gap-1.5">
                    <div className="flex-1 h-3 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-3 bg-red-400 rounded-full transition-all" style={{width:(100-r.pct)+"%"}}/>
                    </div>
                    <span className="font-black text-red-500 w-8 text-right">{100-r.pct}%</span>
                  </div>
                </td>
                <td className="px-3 py-2"><span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${PROG_STATUS_COLOR[r.status]||"bg-slate-100 text-slate-600"}`}>{r.status}</span></td>
              </tr>
            ))}
            {/* Totals row */}
            {totalAct > 0 && (
              <tr className="bg-amber-50 border-t-2 border-amber-300">
                <td colSpan={3} className="px-3 py-2 font-black text-slate-800 text-right">TOTALS →</td>
                <td className="px-3 py-2 font-black text-slate-800 text-center">{totalAct.toLocaleString()}</td>
                <td className="px-3 py-2 font-black text-green-700 text-center">{totalDone.toLocaleString()}</td>
                <td className="px-3 py-2 font-black text-red-600 text-center">{totalBal.toLocaleString()}</td>
                <td className="px-3 py-2"><div className="flex items-center gap-1.5"><div className="flex-1 h-3 bg-amber-100 rounded-full overflow-hidden"><div className="h-3 bg-amber-500 rounded-full" style={{width:overallPct+"%"}}/></div><span className="font-black text-amber-700 w-8">{overallPct}%</span></div></td>
                <td className="px-3 py-2"><span className="font-black text-red-500">{100-overallPct}%</span></td>
                <td className="px-3 py-2"/>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

'''

# Insert before Projects component
if 'const Projects = (' in content and 'ProgressDashboard' not in content:
    content = content.replace('const Projects = (', PROGRESS_DASHBOARD + 'const Projects = (', 1)
    changes += 1
    print("FIX 9: ProgressDashboard component inserted")

# ══════════════════════════════════════════════════════════════════
# FIX 10: Update progress form to show qty fields + lumpsum logic
# ══════════════════════════════════════════════════════════════════
old_form_qty = '''                <div className="grid grid-cols-2 gap-3">
                  <div><Lbl t="Record / Entry Date"/><Inp type="date" value={pgForm.recordDate||""} onChange={e=>setPgForm(p=>({...p,recordDate:e.target.value}))}/></div>
                  <div></div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div><Lbl t="Activity Name" req/>
                    <Sel value={pgForm.activity.startsWith("Other:")||(!ACTIVITIES.includes(pgForm.activity)&&pgForm.activity)?"Other (Custom)":pgForm.activity} onChange={pg=>{const v=pg.target.value;if(v==="Other (Custom)"){setPgForm(p=>({...p,activity:"Other: "}))}else{setPgForm(p=>({...p,activity:v}))}}}>
                      <option value="">Select Activity...</option>{ACTIVITIES.map(a=><option key={a}>{a}</option>)}
                    </Sel>
                  </div>
                  <div><Lbl t="Status"/><Sel value={pgForm.status} onChange={e=>setPgForm(p=>({...p,status:e.target.value}))}>{PROG_STATUS.map(s=><option key={s}>{s}</option>)}</Sel></div>
                </div>'''

new_form_qty = '''                {/* Activity Name + Unit + Status */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div className="sm:col-span-2">
                    <Lbl t="Activity Name" req/>
                    <Sel value={pgForm.activity} onChange={e=>setPgForm(p=>({...p,activity:e.target.value,customActivity:""}))} >
                      <option value="">Select Activity...</option>{ACTIVITIES.map(a=><option key={a}>{a}</option>)}
                    </Sel>
                    {pgForm.activity==="Other (Custom)"&&<Inp value={pgForm.customActivity||""} onChange={e=>setPgForm(p=>({...p,customActivity:e.target.value}))} placeholder="Enter activity name..." className="mt-1.5 border-amber-400"/>}
                  </div>
                  <div><Lbl t="Unit"/><Sel value={pgForm.unit||"NOS"} onChange={e=>setPgForm(p=>({...p,unit:e.target.value,actualQty:"",workDoneQty:"",balanceQty:""}))}>
                    {(PROG_UNITS||["NOS","CUM","SQM","RM","KG","TON","Lumpsum"]).map(u=><option key={u}>{u}</option>)}
                  </Sel></div>
                </div>
                {/* Quantity fields — hidden for Lumpsum */}
                {pgForm.unit !== "Lumpsum" ? (
                  <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 space-y-2">
                    <div className="text-xs font-bold text-blue-700 uppercase tracking-wide mb-1">Quantity Details ({pgForm.unit||"NOS"})</div>
                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <Lbl t="Actual Qty"/>
                        <Inp type="number" value={pgForm.actualQty||""} placeholder="0" onChange={e=>{const a=Number(e.target.value)||0;const d=Number(pgForm.workDoneQty)||0;const bal=Math.max(0,a-d);const p=a>0?Math.min(100,Math.round((d/a)*100)):0;setPgForm(prev=>({...prev,actualQty:e.target.value,balanceQty:String(bal),pct:p}));}}/>
                      </div>
                      <div>
                        <Lbl t="Work Done Qty"/>
                        <Inp type="number" value={pgForm.workDoneQty||""} placeholder="0" onChange={e=>{const d=Number(e.target.value)||0;const a=Number(pgForm.actualQty)||0;const bal=Math.max(0,a-d);const p=a>0?Math.min(100,Math.round((d/a)*100)):0;setPgForm(prev=>({...prev,workDoneQty:e.target.value,balanceQty:String(bal),pct:p}));}}/>
                      </div>
                      <div>
                        <Lbl t="Balance Qty"/>
                        <Inp type="number" value={pgForm.balanceQty||""} readOnly className="bg-slate-100 text-slate-600" placeholder="Auto"/>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 text-xs">
                      <span className="text-green-700 font-bold">Work Done: {pgForm.pct||0}%</span>
                      <span className="text-red-600 font-bold">Remaining: {100-(pgForm.pct||0)}%</span>
                      <div className="flex-1 h-2 bg-white rounded-full overflow-hidden border border-blue-200">
                        <div className="h-2 bg-green-500 rounded-full transition-all" style={{width:(pgForm.pct||0)+"%"}}/>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-amber-50 border border-amber-200 rounded-xl p-3">
                    <div className="text-xs font-bold text-amber-700 uppercase tracking-wide mb-2">Lumpsum — Enter % Directly</div>
                    <div className="space-y-2">
                      <Lbl t={`Progress % (${pgForm.pct||0}%)`}/>
                      <input type="range" min="0" max="100" step="5" value={pgForm.pct||0}
                        onChange={e=>setPgForm(p=>({...p,pct:Number(e.target.value)}))}
                        className="w-full h-3 bg-amber-100 rounded-lg appearance-none cursor-pointer accent-amber-500"/>
                      <div className="flex justify-between text-xs">
                        <span className="text-green-700 font-bold">Done: {pgForm.pct||0}%</span>
                        <span className="text-red-600 font-bold">Remaining: {100-(pgForm.pct||0)}%</span>
                      </div>
                      <div className="h-3 bg-white rounded-full overflow-hidden border border-amber-200">
                        <div className="h-3 rounded-full transition-all" style={{width:(pgForm.pct||0)+"%",background:"linear-gradient(90deg,#f59e0b,#10b981)"}}/>
                      </div>
                    </div>
                  </div>
                )}
                <div className="grid grid-cols-2 gap-3">
                  <div><Lbl t="Status"/><Sel value={pgForm.status} onChange={e=>setPgForm(p=>({...p,status:e.target.value}))}>{PROG_STATUS.map(s=><option key={s}>{s}</option>)}</Sel></div>
                  <div><Lbl t="Record / Entry Date"/><Inp type="date" value={pgForm.recordDate||""} onChange={e=>setPgForm(p=>({...p,recordDate:e.target.value}))}/></div>
                </div>'''

if old_form_qty in content:
    content = content.replace(old_form_qty, new_form_qty, 1)
    changes += 1
    print("FIX 10: Progress form qty fields + lumpsum logic added")
else:
    # Find the activity sel in the form and add qty before dates
    old_form_simple = '''                <div className="grid grid-cols-2 gap-3">
                  <div><Lbl t="Activity Name" req/>
                    <Sel value={pgForm.activity.startsWith("Other:")||(!ACTIVITIES.includes(pgForm.activity)&&pgForm.activity)?"Other (Custom)":pgForm.activity} onChange={pg=>{const v=pg.target.value;if(v==="Other (Custom)"){setPgForm(p=>({...p,activity:"Other: "}))}else{setPgForm(p=>({...p,activity:v}))}}}>
                      <option value="">Select Activity...</option>{ACTIVITIES.map(a=><option key={a}>{a}</option>)}
                    </Sel>
                  </div>
                  <div><Lbl t="Status"/><Sel value={pgForm.status} onChange={e=>setPgForm(p=>({...p,status:e.target.value}))}>{PROG_STATUS.map(s=><option key={s}>{s}</option>)}</Sel></div>
                </div>'''
    if old_form_simple in content:
        content = content.replace(old_form_simple, new_form_qty, 1)
        changes += 1
        print("FIX 10b: Progress form qty fields (fallback)")

# ══════════════════════════════════════════════════════════════════
# FIX 11: Show ProgressDashboard in Project view page
# Find where progress activities section ends and add dashboard
# ══════════════════════════════════════════════════════════════════
# After the Activities Table in view mode, add the dashboard
old_view_end = '''        {/* Activities Table */}
          {filteredPg.length===0?('''
new_view_end = '''        {/* Progress Dashboard */}
          {progTab==="list"&&projPgItems.length>0&&<ProgressDashboard items={projPgItems} projectName={sel.name} overallPct={overallPct}/>}

        {/* Activities Table */}
          {filteredPg.length===0?('''
if old_view_end in content:
    content = content.replace(old_view_end, new_view_end, 1)
    changes += 1
    print("FIX 11: ProgressDashboard shown in project view")

# ══════════════════════════════════════════════════════════════════
# WRITE FILE
# ══════════════════════════════════════════════════════════════════
with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved. Total changes: {changes}")
print("\n⚠️  ALSO RUN THIS SQL IN SUPABASE:")
print("  ALTER TABLE project_progress_items ADD COLUMN IF NOT EXISTS unit VARCHAR(20) DEFAULT 'NOS';")
print("  ALTER TABLE project_progress_items ADD COLUMN IF NOT EXISTS actual_qty NUMERIC DEFAULT 0;")
print("  ALTER TABLE project_progress_items ADD COLUMN IF NOT EXISTS work_done_qty NUMERIC DEFAULT 0;")
print("  ALTER TABLE project_progress_items ADD COLUMN IF NOT EXISTS balance_qty NUMERIC DEFAULT 0;")
print("  ALTER TABLE project_progress_items ADD COLUMN IF NOT EXISTS custom_activity VARCHAR(200);")
print("  NOTIFY pgrst, 'reload schema';")
print("\nTHEN RUN:")
print("  npm install recharts")
print("  set CI=false && npm run build")
print("  git add src/App.js && git commit -m 'feat: progress charts + qty tracking' && git push")
input("\nPress Enter...")
