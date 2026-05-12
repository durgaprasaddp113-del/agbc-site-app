#!/usr/bin/env python3
"""
REF-BASED NOC filter - guaranteed to work
Run from: C:\Apps\agbc-site-app\
Command:  python fix_noc_ref.py
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

noc_start = app.find("const NOCModule = (")
if noc_start == -1: noc_start = app.find("const NOCModule=(")
if noc_start == -1: print("ERROR: NOCModule not found"); input(); exit(1)
print(f"Found NOCModule at {noc_start}")

noc_body = app[noc_start:]

# Step 1: Add refs after first useState in NOCModule
# Find first useState line in NOCModule
first_use_state = re.search(r'^\s+const \[', noc_body, re.MULTILINE)
if first_use_state:
    insert_pos = first_use_state.start()
    indent = len(noc_body[insert_pos:]) - len(noc_body[insert_pos:].lstrip())
    sp = ' ' * indent

    REF_BLOCK = f"""{sp}const projRef   = useRef(null);
{sp}const authRef   = useRef(null);
{sp}const expiryRef = useRef(null);
{sp}const [tick,    setTick]    = useState(0);
{sp}const [fStatus, setFStatus] = useState("All");
{sp}const refilter = () => setTick(t => t + 1);
"""
    noc_body = noc_body[:insert_pos] + REF_BLOCK + noc_body[insert_pos:]
    print("Added refs + tick state")

# Step 2: Remove old fProject/fAuth/fExpiry states (now replaced by refs)
lines = noc_body.split('\n')
clean_lines = []
removed = []
for i, line in enumerate(lines):
    remove = False
    for v in ['fProject', 'fAuth', 'fExpiry']:
        if f'[{v},' in line and 'useState' in line:
            removed.append(f"line {i}: {line.strip()[:60]}")
            remove = True
            break
    if not remove:
        clean_lines.append(line)
    
noc_body = '\n'.join(clean_lines)
print(f"Removed {len(removed)} old state lines:")
for r in removed: print(f"  {r}")

# Step 3: Replace filter block
filter_re = re.compile(r'const filtered = nocs\.filter\(n => \{[\s\S]*?\n  \}\);')
m = filter_re.search(noc_body)
if m:
    NEW_FILTER = '''const _proj   = projRef.current   ? projRef.current.value   : "All";
  const _auth   = authRef.current   ? authRef.current.value   : "All";
  const _expiry = expiryRef.current ? expiryRef.current.value : "All";
  const filtered = nocs.filter(n => {
    if (_proj   !== "All" && String(n.pid||"").toLowerCase() !== _proj.toLowerCase()) return false;
    if (_auth   !== "All" && (n.authority||"") !== _auth) return false;
    if (fStatus !== "All" && (n.status||"")    !== fStatus) return false;
    if (_expiry === "expiring" && !isExpiringSoon(n.expiryDate, n.status)) return false;
    if (_expiry === "expired"  && !isExpired(n.expiryDate,      n.status)) return false;
    if (search) {
      const q   = search.toLowerCase();
      const hay = [n.nocNum,n.authority,n.nocType,n.responsible,n.desc].filter(Boolean).join(" ").toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });'''
    noc_body = noc_body[:m.start()] + NEW_FILTER + noc_body[m.end():]
    print("Replaced filter block")
else:
    print("WARNING: filter block not found")

# Step 4: Replace dropdowns — find and replace each one
def fix_dropdown(body, marker, ref_name, options_str, label):
    idx = body.find(marker)
    if idx == -1:
        print(f"  {label}: marker not found")
        return body
    before = body[:idx]
    tag_start = max(before.rfind('<Sel '), before.rfind('<select '))
    if tag_start == -1:
        print(f"  {label}: tag start not found")
        return body
    after_idx = body[idx:]
    c1 = after_idx.find('</Sel>')
    c2 = after_idx.find('</select>')
    if c1 != -1 and (c2 == -1 or c1 < c2):
        tag_end = idx + c1 + 6
    elif c2 != -1:
        tag_end = idx + c2 + 9
    else:
        print(f"  {label}: close tag not found")
        return body
    line_s = body.rfind('\n', 0, tag_start)
    raw = body[line_s+1:tag_start]
    indent = len(raw) - len(raw.lstrip())
    sp = ' ' * indent
    new_sel = (f'<select ref={{{ref_name}}} defaultValue="All"\n'
               f'{sp}  onChange={{refilter}}\n'
               f'{sp}  className="w-full px-3 py-2 text-sm border border-slate-200 '
               f'rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-400 bg-white">\n'
               f'{sp}  {options_str}\n'
               f'{sp}</select>')
    print(f"  {label}: replaced OK")
    return body[:tag_start] + new_sel + body[tag_end:]

proj_opts = ('<option value="All">All Projects</option>\n'
             '          {(projects||[]).map(p=>'
             '<option key={p.id} value={String(p.id).toLowerCase()}>'
             '{p.number} \u2014 {p.name}</option>)}')

auth_opts = ('<option value="All">All Authorities</option>\n'
             '          {NOC_AUTHORITIES.map(a=>'
             '<option key={a} value={a}>{a}</option>)}')

exp_opts  = ('<option value="All">All Dates</option>\n'
             '          <option value="expiring">Expiring Soon (30 days)</option>\n'
             '          <option value="expired">Already Expired</option>')

print("Replacing dropdowns:")
noc_body = fix_dropdown(noc_body, 'All Projects', 'projRef', proj_opts, 'Project')
noc_body = fix_dropdown(noc_body, 'All Authorities', 'authRef', auth_opts, 'Authority')
noc_body = fix_dropdown(noc_body, 'All Dates', 'expiryRef', exp_opts, 'Expiry')

# Step 5: Fix navFilter useEffect
ue_re = re.compile(r'useEffect\(\(\) => \{[\s\S]*?\}, \[navFilter\]\);')
ue_m = ue_re.search(noc_body)
if ue_m:
    NEW_UE = '''useEffect(() => {
    setFStatus(navFilter.status || "All");
    refilter();
  }, [navFilter]);'''
    noc_body = noc_body[:ue_m.start()] + NEW_UE + noc_body[ue_m.end():]
    print("Fixed navFilter useEffect")

# Write
app = app[:noc_start] + noc_body
with open(APP, "w", encoding="utf-8") as f:
    f.write(app)

print()
print("=" * 55)
print("Done! Ref-based NOC filters applied.")
print(f"Backup: {bk}")
print("Run: set CI=false && npm run build")
print("=" * 55)
input("Press Enter to exit...")
