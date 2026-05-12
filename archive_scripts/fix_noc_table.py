import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print("Backup:", bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# Find the NOC table headers to confirm count
print("── NOC TABLE HEADERS ──")
noc = next((i for i,l in enumerate(lines) if "const NOCModule = (" in l), -1)
for j in range(noc, min(noc+800, len(lines))):
    if '<thead' in lines[j]:
        for k in range(j, min(j+6, len(lines))):
            print(f"L{k+1}: {s(lines[k].rstrip())[:160]}")
        break

# Fix: Remove the extra Priority <td> block (L11631-11633 area)
# Pattern to find and remove:
OLD_PRIORITY_TD = '''                      <td className="px-4 py-3">
                        <span className={`text-xs font-semibold px-1.5 py-0.5 rounded ${NOC_PRI_COLOR[n.priority]||""}`}>{n.priority}</span>
                      </td>'''

changes = 0
content = "".join(lines)

if OLD_PRIORITY_TD in content:
    content = content.replace(OLD_PRIORITY_TD, "", 1)
    changes += 1
    print("\nFIX 1: Removed extra Priority <td> from NOC table row")
else:
    print("\nWARN: Exact pattern not found — trying line-by-line...")
    new_lines = []
    i = 0
    llist = content.split('\n')
    while i < len(llist):
        l = llist[i]
        # Detect the 3-line priority td block
        if 'NOC_PRI_COLOR' in l and 'n.priority' in l:
            # Remove this line and check adjacent td tags
            # Remove prev line if it's <td
            if new_lines and '<td' in new_lines[-1] and 'py-3' in new_lines[-1]:
                new_lines.pop()
            # Skip current line
            # Skip next line if it's </td>
            if i+1 < len(llist) and '</td>' in llist[i+1]:
                i += 2
            else:
                i += 1
            changes += 1
            print(f"  FIX 1b: Removed Priority cell at L{i+1}")
            continue
        new_lines.append(l)
        i += 1
    content = '\n'.join(new_lines)

# Write
with open(APP, "w", encoding="utf-8") as f:
    f.write(content)

# Verify: count td cells in NOC row vs th headers
print("\n── VERIFY: NOC headers vs row cells ──")
with open(APP, "r", encoding="utf-8", errors="replace") as f:
    vlines = f.readlines()

noc2 = next((i for i,l in enumerate(vlines) if "const NOCModule = (" in l), -1)

# Count th headers
th_count = 0
for j in range(noc2, min(noc2+800, len(vlines))):
    if '<thead' in vlines[j]:
        for k in range(j, min(j+6, len(vlines))):
            th_count += vlines[k].count('<th ')
            if '</thead>' in vlines[k]: break
        break
print(f"Header <th> count: {th_count}")

# Count td cells in first data row
td_count = 0
in_row = False
for j in range(noc2, min(noc2+900, len(vlines))):
    if '<tbody' in vlines[j]: in_row = True
    if in_row and '<tr key=' in vlines[j]:
        for k in range(j, min(j+30, len(vlines))):
            td_count += vlines[k].count('<td ')
            if '</tr>' in vlines[k]: break
        break
print(f"Row <td> count:    {td_count}")
if th_count == td_count:
    print("✓ MATCH — columns aligned!")
else:
    print(f"✗ MISMATCH — {abs(th_count-td_count)} extra cell(s)")

print()
print("="*50)
print("TOTAL FIXES:", changes)
print()
print("RUN NOW:")
print("  set CI=false && npm run build")
print("  npx vercel --prod --force")
print("  git add src/App.js")
print('  git commit -m "Fix: NOC table priority column mismatch"')
print("  git push")
print("="*50)
input("Press Enter...")
