import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
changes = 0

# L898 (0-based: 897): }]);  → }]).select('id');
# L900 (0-based: 899): await loadData(); return { ok: true, reportNum };
# → const newId=(data&&data[0])?data[0].id:null; await loadData(); return {ok:true,id:newId,reportNum};

# Fix L898
target_898 = 897  # 0-based
if "    }]);" in lines[target_898] and "select" not in lines[target_898]:
    lines[target_898] = lines[target_898].replace("    }]);", "    }]).select('id');")
    changes += 1
    print(f"FIX L898: .select added → {s(lines[target_898].rstrip())}")
else:
    # Search around that area
    for j in range(895, 905):
        if "}]);" in lines[j] and "select" not in lines[j] and "daily_reports" in "".join(lines[max(0,j-20):j]):
            lines[j] = lines[j].replace("}]);", "}]).select('id');")
            changes += 1
            print(f"FIX L{j+1}: .select added → {s(lines[j].rstrip())}")
            break

# Fix L900
target_900 = 899  # 0-based
if "return { ok: true, reportNum };" in lines[target_900]:
    lines[target_900] = lines[target_900].replace(
        "await loadData(); return { ok: true, reportNum };",
        "const newId = (data && data[0]) ? data[0].id : null; await loadData(); return { ok: true, id: newId, reportNum };"
    )
    changes += 1
    print(f"FIX L900: return now has id → {s(lines[target_900].rstrip())[:100]}")
else:
    for j in range(896, 906):
        if "return { ok: true, reportNum }" in lines[j]:
            lines[j] = lines[j].replace(
                "return { ok: true, reportNum };",
                "const newId = (data && data[0]) ? data[0].id : null; await loadData(); return { ok: true, id: newId, reportNum };"
            )
            changes += 1
            print(f"FIX L{j+1}: return → {s(lines[j].rstrip())[:100]}")
            break

# Verify
print("\n── Verify add function L879-902 ──")
for j in range(878, min(903, len(lines))):
    print(f"L{j+1}: {s(lines[j].rstrip())[:120]}")

# Write
out = "".join(lines)
with open(APP,"w",encoding="utf-8") as f:
    f.write(out)
print(f"\nSaved. Changes: {changes}")
print("RUN: set CI=false && npm run build")
input("Press Enter...")
