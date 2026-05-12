APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def show(label,a,b):
    print("=== "+label+" ===")
    for i in range(a,min(b,len(lines))):
        print(str(i+1)+"\t"+s(lines[i].rstrip()))
    print()
def find(t):
    for i,l in enumerate(lines):
        if t in l: return i
    return -1

app = find("function App(")
if app == -1: app = find("export default function App")
if app == -1: app = find("const App = (")

print("### App() state setup (first 60 lines) ###")
show("App state", app, app+60)

print("### navFilter definition in App ###")
for i,l in enumerate(lines):
    if "navFilter" in l and i > app:
        print("L"+str(i+1)+": "+s(l.rstrip())[:160])

print("\n### navigate / setNav / onNavigate in App ###")
for i,l in enumerate(lines):
    if ("navigate" in l or "setNav" in l or "onNavigate" in l) and i > app:
        print("L"+str(i+1)+": "+s(l.rstrip())[:160])

print("\n### How MR/LPO/NOC case returns component (full line) ###")
for i,l in enumerate(lines):
    if 'case "mr"' in l or 'case "lpo"' in l or 'case "noc"' in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:200])

print("\n=== DONE ===")
input("Press Enter...")
