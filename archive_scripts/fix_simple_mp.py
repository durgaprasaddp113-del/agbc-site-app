import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# ── THE ONLY REAL FIX NEEDED ─────────────────────────────────────────
# In useDailyReports.loadData, compute manpowerTotal from dpr_attendance
# instead of from manpower_total column (which is never updated correctly)
#
# Change:
#   manpowerTotal: r.manpower_total || 0,
# To:
#   manpowerTotal: r.manpower_total || 0,   (keep for now)
#
# AND fix the View mode to show attendance count instead of manpowerTotal
# The View already shows correct attendance via DprAttendanceViewPanel
# Just need to fix the "Total Manpower" summary card in View mode
# ─────────────────────────────────────────────────────────────────────

# FIX 1: In View mode, the totalMP card reads sel.manpowerTotal
# Change it to read from the attendance panel's count
# Find: sel.manpowerTotal || (sel.manpower...)
old1 = "const totalMP = sel.manpowerTotal || (sel.manpower||[]).reduce((s,r)=>s+(Number(r.count)||0),0);"
if old1 in content:
    print("FIX 1: totalMP line found - already uses manpowerTotal")
else:
    print("FIX 1: searching for totalMP...")
    import re
    m = re.search(r'const totalMP = [^;]+;', content)
    if m:
        print("Found: "+m.group()[:100])

# FIX 2: In saveAttendance, the update to daily_reports is the key
# Make sure it runs - check exact code
old_sa = 'await supabase.from("daily_reports").update({ manpower_total: presentCount }).eq("id", dprId);'
if old_sa in content:
    print("FIX 2: saveAttendance DB update exists ✓")
else:
    print("FIX 2: saveAttendance DB update MISSING - adding...")
    # Find the return in saveAttendance and add the update before it
    old_ret = 'if (error) return { ok: false, error: error.message };\n      return { ok: true };'
    new_ret = ('if (error) return { ok: false, error: error.message };\n'
               '      const presentCount = valid.filter(r => r.am==="P" || r.pm==="P").length;\n'
               '      await supabase.from("daily_reports").update({ manpower_total: presentCount }).eq("id", dprId);\n'
               '      return { ok: true };')
    # Find in saveAttendance context
    sa_idx = content.find("saveAttendance = async (dprId, rows)")
    if sa_idx != -1:
        chunk = content[sa_idx:sa_idx+500]
        if 'if (error) return { ok: false' in chunk and 'presentCount' not in chunk:
            new_chunk = chunk.replace(
                'if (error) return { ok: false, error: error.message };\n      return { ok: true };',
                'if (error) return { ok: false, error: error.message };\n      const presentCount = valid.filter(r => r.am==="P" || r.pm==="P").length;\n      await supabase.from("daily_reports").update({ manpower_total: presentCount }).eq("id", dprId);\n      return { ok: true };'
            )
            content = content[:sa_idx] + new_chunk + content[sa_idx+500:]
            changes += 1
            print("FIX 2: DB update added to saveAttendance")

# FIX 3: The list shows mp which comes from r.manpowerTotal
# After user saves DPR, loadData runs and reads manpower_total from DB
# But saveAttendance hasn't run yet
# Simple fix: in useDailyReports.update, also read from dpr_attendance
# via a join or separate query

# Actually the REAL simple fix:
# Change the list to read attendance count via a LEFT JOIN in the select query
# But that requires changing the Supabase query...

# SIMPLEST FIX: Change loadData in useDailyReports to do a second query
# for attendance counts and merge them

udr_idx = content.find('const { data, error } = await supabase.from("daily_reports").select("*")')
if udr_idx != -1:
    # Find the end of loadData function - after setReports
    load_end = content.find("setLoading(false);", udr_idx)
    if load_end != -1:
        chunk = content[udr_idx:load_end+20]
        if "dpr_attendance" not in chunk:
            # Add attendance count query after reports load
            old_chunk_end = 'setLoading(false);'
            new_chunk_end = (
                'const { data: attCounts } = await supabase.from("dpr_attendance")\n'
                '          .select("dpr_id, am_count, pm_count");\n'
                '        if (attCounts && attCounts.length && data) {\n'
                '          const cntMap = {};\n'
                '          attCounts.forEach(a => {\n'
                '            if (!cntMap[a.dpr_id]) cntMap[a.dpr_id] = 0;\n'
                '            if (a.am_count===1 || a.pm_count===1) cntMap[a.dpr_id]++;\n'
                '          });\n'
                '          setReports(prev => prev.map(r => ({ ...r, manpowerTotal: cntMap[r.id] || r.manpowerTotal })));\n'
                '        }\n'
                '        setLoading(false);'
            )
            # Find the exact setLoading(false) in loadData
            load_end2 = content.find("setLoading(false);", udr_idx)
            if load_end2 != -1:
                content = content[:load_end2] + new_chunk_end + content[load_end2+len("setLoading(false);"):]
                changes += 1
                print("FIX 3: loadData now merges attendance counts from dpr_attendance")
        else:
            print("FIX 3: loadData already queries dpr_attendance")

# Write
checks = ["const DailyReports","DprAttendancePanel","saveAttendance"]
failed = [c for c in checks if c not in content]
if failed:
    print("SAFETY FAIL: "+str(failed))
    shutil.copy2(bk, APP)
else:
    with open(APP,"w",encoding="utf-8") as f:
        f.write(content)
    print("\nSaved OK")

print("TOTAL CHANGES: "+str(changes))
print("\nRUN: set CI=false && npm run build")
input("\nPress Enter...")
