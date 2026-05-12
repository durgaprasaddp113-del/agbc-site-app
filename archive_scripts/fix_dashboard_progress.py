import shutil, re
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print(f"Backup: {bk}")

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# ══════════════════════════════════════════════════════════════════
# FIX 1: After progressItems destructure in App, compute
#         getOverallPct(pid) and projectsWithPct array
#         These are at App level so Dashboard can use them
# ══════════════════════════════════════════════════════════════════
OLD_HOOK = '  const { progressItems, add: addPg, update: updPg, remove: delPg } = useProjectProgress();'
NEW_HOOK = '''  const { progressItems, add: addPg, update: updPg, remove: delPg } = useProjectProgress();

  // App-level overall progress calculator — used by Dashboard + Projects card
  const getOverallPct = (pid) => {
    const items = progressItems.filter(p => p.pid === pid);
    if (!items.length) return 0;
    const withQty = items.filter(i => i.unit !== "Lumpsum" && (Number(i.actualQty)||0) > 0);
    if (withQty.length > 0) {
      const totalActual = withQty.reduce((s,i) => s + (Number(i.actualQty)||0), 0);
      const totalDone   = withQty.reduce((s,i) => s + (Number(i.workDoneQty)||0), 0);
      const qtyPct      = totalActual > 0 ? Math.round((totalDone / totalActual) * 100) : 0;
      const lumpItems   = items.filter(i => i.unit === "Lumpsum" || (Number(i.actualQty)||0) === 0);
      const lumpAvg     = lumpItems.length > 0 ? lumpItems.reduce((s,i) => s + (Number(i.pct)||0), 0) / lumpItems.length : null;
      if (lumpAvg !== null) return Math.round((qtyPct + lumpAvg) / 2);
      return Math.min(100, qtyPct);
    }
    return Math.round(items.reduce((a,i) => a + (Number(i.pct)||0), 0) / items.length);
  };

  // Enrich projects array with live overallPct — auto-updates when progressItems changes
  const projectsWithPct = projects.map(p => ({ ...p, overallPct: getOverallPct(p.id) }));'''

if OLD_HOOK in content:
    content = content.replace(OLD_HOOK, NEW_HOOK, 1)
    changes += 1
    print("FIX 1: getOverallPct + projectsWithPct added at App level ✅")
else:
    print("WARN FIX 1: progressItems destructure pattern not found")

# ══════════════════════════════════════════════════════════════════
# FIX 2: Pass projectsWithPct to Dashboard instead of projects
# ══════════════════════════════════════════════════════════════════
# Find the dashboard case line — it starts with case "dashboard":
OLD_DASH = 'case "dashboard":      return <Dashboard projects={projects} tasks={tasks}'
NEW_DASH = 'case "dashboard":      return <Dashboard projects={projectsWithPct} tasks={tasks}'
if OLD_DASH in content:
    content = content.replace(OLD_DASH, NEW_DASH, 1)
    changes += 1
    print("FIX 2: Dashboard receives projectsWithPct ✅")
else:
    # Try without extra spaces
    OLD_DASH2 = 'case "dashboard": return <Dashboard projects={projects} tasks={tasks}'
    NEW_DASH2 = 'case "dashboard": return <Dashboard projects={projectsWithPct} tasks={tasks}'
    if OLD_DASH2 in content:
        content = content.replace(OLD_DASH2, NEW_DASH2, 1)
        changes += 1
        print("FIX 2b: Dashboard receives projectsWithPct (alt spacing) ✅")
    else:
        # Regex approach
        import re
        pattern = r'(case "dashboard":\s+return <Dashboard projects=)\{projects\}'
        replacement = r'\1{projectsWithPct}'
        new_content, n = re.subn(pattern, replacement, content, count=1)
        if n > 0:
            content = new_content
            changes += 1
            print("FIX 2c: Dashboard receives projectsWithPct (regex) ✅")
        else:
            print("WARN FIX 2: dashboard case pattern not found — searching...")
            idx = content.find('case "dashboard"')
            if idx > -1:
                print(f"  Found at char {idx}: {repr(content[idx:idx+100])}")

# ══════════════════════════════════════════════════════════════════
# FIX 3: Pass projectsWithPct to Projects component too
#         So project cards show live % without needing getOverall
# ══════════════════════════════════════════════════════════════════
OLD_PROJ = 'case "projects":       return <Projects {...pp} loading={plLoad}'
NEW_PROJ = 'case "projects":       return <Projects {...pp} projects={projectsWithPct} loading={plLoad}'
if OLD_PROJ in content:
    content = content.replace(OLD_PROJ, NEW_PROJ, 1)
    changes += 1
    print("FIX 3: Projects receives projectsWithPct ✅")
else:
    OLD_PROJ2 = 'case "projects": return <Projects {...pp} loading={plLoad}'
    NEW_PROJ2 = 'case "projects": return <Projects {...pp} projects={projectsWithPct} loading={plLoad}'
    if OLD_PROJ2 in content:
        content = content.replace(OLD_PROJ2, NEW_PROJ2, 1)
        changes += 1
        print("FIX 3b: Projects receives projectsWithPct (alt) ✅")
    else:
        import re
        pattern = r'(case "projects":\s+return <Projects \{\.\.\.pp\}) loading=\{plLoad\}'
        replacement = r'\1 projects={projectsWithPct} loading={plLoad}'
        new_content, n = re.subn(pattern, replacement, content, count=1)
        if n > 0:
            content = new_content
            changes += 1
            print("FIX 3c: Projects receives projectsWithPct (regex) ✅")
        else:
            print("WARN FIX 3: projects case not found")

# ══════════════════════════════════════════════════════════════════
# FIX 4: Also pass projectsWithPct via pp object so ALL modules
#         (Tasks, Snags, etc.) get live overallPct when navigating
# ══════════════════════════════════════════════════════════════════
OLD_PP = 'const pp = { projects, showToast, userProfile, userCanEdit, userIsAdmin, permReqs, onAddPermReq: addPermReq, navFilter, onNavigate: navigate };'
NEW_PP = 'const pp = { projects: projectsWithPct, showToast, userProfile, userCanEdit, userIsAdmin, permReqs, onAddPermReq: addPermReq, navFilter, onNavigate: navigate };'
if OLD_PP in content:
    content = content.replace(OLD_PP, NEW_PP, 1)
    changes += 1
    print("FIX 4: pp object uses projectsWithPct ✅")
else:
    # Try without onNavigate
    OLD_PP2 = 'const pp = { projects, showToast, userProfile, userCanEdit, userIsAdmin, permReqs, onAddPermReq: addPermReq, navFilter };'
    NEW_PP2 = 'const pp = { projects: projectsWithPct, showToast, userProfile, userCanEdit, userIsAdmin, permReqs, onAddPermReq: addPermReq, navFilter };'
    if OLD_PP2 in content:
        content = content.replace(OLD_PP2, NEW_PP2, 1)
        changes += 1
        print("FIX 4b: pp object uses projectsWithPct (no onNavigate) ✅")
    else:
        import re
        pattern = r'const pp = \{ projects,'
        replacement = 'const pp = { projects: projectsWithPct,'
        new_content, n = re.subn(pattern, replacement, content, count=1)
        if n > 0:
            content = new_content
            changes += 1
            print("FIX 4c: pp uses projectsWithPct (regex) ✅")
        else:
            print("WARN FIX 4: pp pattern not found")

# ══════════════════════════════════════════════════════════════════
# FIX 5: Dashboard project card — make overallPct show with fallback
#         L1842: const pct = p.overallPct || 0;  (already correct)
#         Just verify it's not using something else
# ══════════════════════════════════════════════════════════════════
if 'const pct = p.overallPct || 0;' in content:
    print("FIX 5: Dashboard pct line already correct ✅")
else:
    # Try to find what it uses
    import re
    m = re.search(r'const pct = [^;]+;', content[1840*50:1860*50])
    if m:
        print(f"INFO FIX 5: pct line found: {m.group()}")

# ══════════════════════════════════════════════════════════════════
# WRITE FILE
# ══════════════════════════════════════════════════════════════════
with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved. Total changes: {changes}")
print("\nRUN:")
print("  set CI=false && npm run build")
print("  git add src/App.js && git commit -m 'fix: dashboard live progress from progressItems' && git push")
input("\nPress Enter...")
