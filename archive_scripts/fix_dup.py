APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

# Rename the duplicate in our new code only
# Our new code is the SECOND occurrence - rename it to EMPTY_MP_FORM
content = content.replace(
    'const EMPTY_MP = () => ({ subId:"", empId:"", name:"", designation:"", defaultTeamNo:"", status:"Active", dateJoined:"", dateLeft:"", remarks:"" });\n\nconst ManpowerMaster',
    'const EMPTY_MP_FORM = () => ({ subId:"", empId:"", name:"", designation:"", defaultTeamNo:"", status:"Active", dateJoined:"", dateLeft:"", remarks:"" });\n\nconst ManpowerMaster'
)

# Update references in ManpowerMaster component
content = content.replace(
    'const [form, setForm] = useState(EMPTY_MP());\n  const [saving, setSaving] = useState(false);\n  const [search, setSearch] = useState("");\n  const [fSub, setFSub] = useState("All");\n  const [fStatus, setFStatus] = useState("Active");\n  const [confirmId, setConfirmId] = useState(null);\n  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));\n\n  const filtered',
    'const [form, setForm] = useState(EMPTY_MP_FORM());\n  const [saving, setSaving] = useState(false);\n  const [search, setSearch] = useState("");\n  const [fSub, setFSub] = useState("All");\n  const [fStatus, setFStatus] = useState("Active");\n  const [confirmId, setConfirmId] = useState(null);\n  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));\n\n  const filtered'
)
content = content.replace(
    'setForm(EMPTY_MP()); setSel(null); setMode("form"); };',
    'setForm(EMPTY_MP_FORM()); setSel(null); setMode("form"); };'
)

with open(APP,"w",encoding="utf-8") as f:
    f.write(content)
print("Fixed. Run: set CI=false && npm run build")
input("Press Enter...")
