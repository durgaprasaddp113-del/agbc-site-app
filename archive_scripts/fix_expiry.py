#!/usr/bin/env python3
"""
Fix ONLY the Expiry Date filter in NOC module.
Run from: C:\Apps\agbc-site-app\
Command:  python fix_expiry.py
"""
import os, shutil, re
from datetime import datetime

APP = r"src\App.js"
if not os.path.exists(APP):
    print("ERROR: src\\App.js not found"); input(); exit(1)

bk = APP + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(APP, bk)
print(f"Backup: {bk}")

with open(APP, "r", encoding="utf-8") as f:
    app = f.read()

# Find NOCModule
noc_start = app.find("const NOCModule = (")
if noc_start == -1:
    noc_start = app.find("const NOCModule=(")
if noc_start == -1:
    print("ERROR: NOCModule not found"); input(); exit(1)

# ── Find the expiry Sel/select in NOCModule and replace it entirely ───────────
noc_part = app[noc_start:]

# Find the expiry dropdown — look for "All Dates" option text
dates_idx = noc_part.find('"All Dates"')
if dates_idx == -1:
    dates_idx = noc_part.find("All Dates")

if dates_idx == -1:
    print("ERROR: 'All Dates' not found in NOCModule"); input(); exit(1)

# Find the opening tag of this dropdown (go backwards to find <Sel or <select)
before = noc_part[:dates_idx]
tag_start = max(before.rfind("<Sel "), before.rfind("<select "))
if tag_start == -1:
    print("ERROR: Dropdown opening tag not found"); input(); exit(1)

# Find closing tag
after = noc_part[dates_idx:]
close_sel = after.find("</Sel>")
close_select = after.find("</select>")

if close_sel != -1 and (close_select == -1 or close_sel < close_select):
    tag_end = dates_idx + close_sel + len("</Sel>")
    print("Found Sel dropdown")
elif close_select != -1:
    tag_end = dates_idx + close_select + len("</select>")
    print("Found select dropdown")
else:
    print("ERROR: Dropdown closing tag not found"); input(); exit(1)

old_dropdown = noc_part[tag_start:tag_end]
print(f"Old dropdown:\n{old_dropdown}\n")

# Replace with clean native select
new_dropdown = '''<select value={fExpiry} onChange={e => setFExpiry(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 bg-white">
            <option value="All">All Dates</option>
            <option value="expiring">Expiring Soon (within 30 days)</option>
            <option value="expired">Already Expired</option>
          </select>'''

noc_part = noc_part[:tag_start] + new_dropdown + noc_part[tag_end:]
app = app[:noc_start] + noc_part
print("Fixed: Expiry dropdown replaced with native select")

# ── Also fix the filter logic for expiry ─────────────────────────────────────
noc_part = app[noc_start:]

# Find the filtered = nocs.filter block
filter_match = re.search(
    r'const filtered = nocs\.filter\(n => \{[\s\S]*?\n  \}\);',
    noc_part
)

if filter_match:
    old_filter = filter_match.group(0)
    print(f"\nCurrent filter found ({len(old_filter)} chars)")
    
    # Check if expiry lines exist
    has_expiring = "fExpiry" in old_filter
    print(f"Has fExpiry in filter: {has_expiring}")
    
    NEW_FILTER = '''const filtered = nocs.filter(n => {
    const pid  = String(n.pid  || "").toLowerCase().trim();
    const fpid = String(fProject || "").toLowerCase().trim();
    if (fProject !== "All" && fpid && pid !== fpid) return false;
    if (fAuth    !== "All" && (n.authority || "") !== fAuth) return false;
    if (fStatus  !== "All" && (n.status    || "") !== fStatus) return false;
    if (fExpiry  === "expiring" && !isExpiringSoon(n.expiryDate, n.status)) return false;
    if (fExpiry  === "expired"  && !isExpired(n.expiryDate,      n.status)) return false;
    if (search) {
      const q   = search.toLowerCase();
      const hay = [n.nocNum, n.authority, n.nocType, n.responsible, n.desc]
                    .filter(Boolean).join(" ").toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });'''
    
    noc_part = noc_part[:filter_match.start()] + NEW_FILTER + noc_part[filter_match.end():]
    app = app[:noc_start] + noc_part
    print("Fixed: Filter logic rewritten")
else:
    print("WARNING: Filter block not found")

# ── Ensure fExpiry useState is clean (fix any "navFilter.expiry" reference) ──
noc_part = app[noc_start:]
lines = noc_part.split('\n')
for i, line in enumerate(lines):
    if 'fExpiry' in line and 'useState' in line:
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + 'const [fExpiry, setFExpiry] = useState("All");'
        print(f"Fixed: fExpiry useState on line {i}: {lines[i].strip()}")
        break
noc_part = '\n'.join(lines)
app = app[:noc_start] + noc_part

# ── Write ─────────────────────────────────────────────────────────────────────
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 50)
print("Done! Only expiry filter was changed.")
print(f"Backup: {bk}")
print()
print("Test: set CI=false && npm run build")
print("Deploy: npx vercel --prod")
print("=" * 50)
input("Press Enter to exit...")
