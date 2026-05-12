import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
changes = 0

# ── FIX 1: L4033 — list row uses OLD manpower array instead of manpowerTotal
# Current: const mp=(r.manpower||[]).reduce((s,x)=>s+(Number(x.count)||0),0);
# Fix:     const mp = r.manpowerTotal || 0;
target = 4032  # 0-based
if "const mp=(r.manpower||[]).reduce" in lines[target]:
    lines[target] = lines[target].replace(
        "const mp=(r.manpower||[]).reduce((s,x)=>s+(Number(x.count)||0),0);",
        "const mp = r.manpowerTotal || 0;"
    )
    changes += 1
    print("FIX 1: list mp now uses r.manpowerTotal at L4033")
else:
    # Search nearby
    for j in range(4025, 4045):
        if "const mp=" in lines[j] and "reduce" in lines[j]:
            lines[j] = lines[j].replace(
                lines[j].strip(),
                "                const mp = r.manpowerTotal || 0;"
            )
            # More precise replacement
            import re
            lines[j] = re.sub(
                r'const mp=\(r\.manpower\|\|\[\]\)\.reduce\([^;]+\);',
                'const mp = r.manpowerTotal || 0;',
                lines[j]
            )
            changes += 1
            print("FIX 1: list mp fixed at L"+str(j+1))
            break

# ── FIX 2: L3955 — Excel/PDF export also uses old manpower array
# L3955: manpowerTotal:(r.manpower||[]).reduce(...)
target2 = 3954  # 0-based
if "manpowerTotal:(r.manpower||[]).reduce" in lines[target2]:
    lines[target2] = lines[target2].replace(
        "manpowerTotal:(r.manpower||[]).reduce((s,x)=>s+(Number(x.count)||0),0),",
        "manpowerTotal: r.manpowerTotal || 0,"
    )
    changes += 1
    print("FIX 2: export manpowerTotal fixed at L3955")

# ── FIX 3: View mode Total Manpower card
# Already fixed via sel.manpowerTotal — verify
dr = next((i for i,l in enumerate(lines) if "const DailyReports = ({" in l),-1)
if dr != -1:
    for j in range(dr, min(dr+900,len(lines))):
        if "const totalMP" in lines[j] and "sel.manpower" in lines[j]:
            old = lines[j]
            lines[j] = lines[j].replace(
                "const totalMP = (sel.manpower||[]).reduce((s,r)=>s+(Number(r.count)||0),0);",
                "const totalMP = sel.manpowerTotal || (sel.manpower||[]).reduce((s,r)=>s+(Number(r.count)||0),0);"
            )
            if lines[j] != old:
                changes += 1
                print("FIX 3: View totalMP uses sel.manpowerTotal at L"+str(j+1))
            break

# ── VERIFY ───────────────────────────────────────────────────────────
print("\n── VERIFY ──")
for j in range(4025, 4045):
    if "const mp" in lines[j]:
        print("L"+str(j+1)+": "+s(lines[j].rstrip())[:100])
print("L3955: "+s(lines[3954].rstrip())[:100])

# Write
with open(APP,"w",encoding="utf-8") as f:
    f.writelines(lines)

print("\nSaved. Changes: "+str(changes))
print("\nRUN:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
input("\nPress Enter...")
