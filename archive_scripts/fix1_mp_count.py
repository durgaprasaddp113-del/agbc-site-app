import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# FIX 1: loadData in useDailyReports - add attendance count query
# Find: setLoading(false); in loadData and add att count merge before it
old = """        if (data) setReports(data.map(r => {
          const parse = (field) => { try { return JSON.parse(r[field]||"[]"); } catch { return []; } };
          return {
            id: r.id, pid: r.project_id, date: r.report_date || "",
            reportNum: r.report_number || "",
            weather: r.weather || "Sunny", temp: r.temperature_high || "",
            workHours: r.work_hours || "8",
            manpower: parse("manpower_json"),
            equipment: parse("equipment_json"),
            activities: parse("activities_json"),
            materials: parse("materials_json"),
            inspections: parse("inspections_json"),
            safety: parse("safety_json"),
            manpowerTotal: r.manpower_total || 0,
            issues: r.issues_delays || "",
            visitors: r.visitors || "",
            remarks: r.remarks || "",
            status: r.status || "Draft",
            preparedBy: r.prepared_by_name || "",
          };
        }));
        setLoading(false);"""

new = """        if (data) setReports(data.map(r => {
          const parse = (field) => { try { return JSON.parse(r[field]||"[]"); } catch { return []; } };
          return {
            id: r.id, pid: r.project_id, date: r.report_date || "",
            reportNum: r.report_number || "",
            weather: r.weather || "Sunny", temp: r.temperature_high || "",
            workHours: r.work_hours || "8",
            manpower: parse("manpower_json"),
            equipment: parse("equipment_json"),
            activities: parse("activities_json"),
            materials: parse("materials_json"),
            inspections: parse("inspections_json"),
            safety: parse("safety_json"),
            manpowerTotal: r.manpower_total || 0,
            issues: r.issues_delays || "",
            visitors: r.visitors || "",
            remarks: r.remarks || "",
            status: r.status || "Draft",
            preparedBy: r.prepared_by_name || "",
          };
        }));
        // Merge attendance counts from dpr_attendance table
        const { data: attC } = await supabase.from("dpr_attendance").select("dpr_id,am_count,pm_count");
        if (attC && attC.length && data) {
          const mp = {};
          attC.forEach(a => { if (!mp[a.dpr_id]) mp[a.dpr_id]=0; if(a.am_count===1||a.pm_count===1) mp[a.dpr_id]++; });
          setReports(prev => prev.map(r => ({...r, manpowerTotal: mp[r.id] || r.manpowerTotal})));
        }
        setLoading(false);"""

if old in content:
    content = content.replace(old, new, 1)
    changes += 1
    print("FIX 1: loadData now merges attendance counts")
else:
    print("WARN: Pattern not found")

with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print("Changes:", changes)
print("\nRUN:")
print("  set CI=false && npm run build")
print("  git add src/App.js && git commit -m 'fix1: manpower count from attendance' && git push")
input("\nPress Enter...")
