APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def show(label,a,b):
    print("=== "+label+" (L"+str(a+1)+"-"+str(b+1)+") ===")
    for i in range(a,min(b,len(lines))):
        print(str(i+1)+"\t"+s(lines[i].rstrip()))
    print()
def find(t):
    for i,l in enumerate(lines):
        if t in l: return i
    return -1

# 1. useProjects hook - FULL definition
print("### useProjects FULL HOOK ###")
idx = find("function useProjects")
if idx == -1: idx = find("const useProjects")
if idx != -1:
    show("useProjects", idx, idx+40)
else:
    print("NOT FOUND - searching for setProjects...")
    for i,l in enumerate(lines):
        if "setProjects" in l and "map" in l:
            show("setProjects mapping", i, i+10)
            break

# 2. How projects are passed to each module
print("### HOW PROJECTS ARE PASSED TO MODULES ###")
for i,l in enumerate(lines):
    if "projects={" in l and ("MaterialRequests" in l or "LPOModule" in l or "NOCModule" in l):
        print("L"+str(i+1)+": "+s(l.rstrip())[:160])

# 3. MR form - how project_id is saved
print("\n### MR SAVE - HOW project_id IS STORED ###")
mr_idx = find("function useMatReqs")
if mr_idx == -1: mr_idx = find("useMatReqs")
if mr_idx != -1:
    for j in range(mr_idx, min(mr_idx+120, len(lines))):
        l = lines[j]
        if "project_id" in l or "pid" in l:
            print("L"+str(j+1)+": "+s(l.rstrip()))

# 4. MR form fields - project selector
print("\n### MR FORM - PROJECT FIELD ###")
mr_comp = find("const MaterialRequests = (")
if mr_comp != -1:
    for j in range(mr_comp, min(mr_comp+600, len(lines))):
        l = lines[j]
        if ("pid" in l or "project" in l.lower()) and ("form" in l.lower() or "Form" in l or "setForm" in l or "onChange" in l):
            print("L"+str(j+1)+": "+s(l.rstrip())[:160])

# 5. LPO form - project_id saved
print("\n### LPO SAVE - project_id ###")
lpo_idx = find("function useLPOs")
if lpo_idx != -1:
    for j in range(lpo_idx, min(lpo_idx+120, len(lines))):
        l = lines[j]
        if "project_id" in l or ("pid" in l and "project" in l.lower()):
            print("L"+str(j+1)+": "+s(l.rstrip()))

# 6. What does App() pass as projects to these modules?
print("\n### App() RENDER - projects prop ###")
app_idx = find("function App(")
if app_idx == -1: app_idx = find("export default function App")
if app_idx != -1:
    for j in range(app_idx, min(app_idx+300, len(lines))):
        l = lines[j]
        if "projects" in l and ("useProjects" in l or "projects=" in l):
            print("L"+str(j+1)+": "+s(l.rstrip())[:160])

# 7. Projects table columns used
print("\n### useProjects data mapping ###")
for i,l in enumerate(lines):
    if ("id:" in l or "number:" in l) and ("project_number" in l or "p.id" in l or "p.number" in l):
        if i < 3000:  # projects hook is likely near top
            print("L"+str(i+1)+": "+s(l.rstrip()))

# 8. Show the full MR filter to confirm _pid source
print("\n### MR FULL FILTER BLOCK ###")
mr_comp = find("const MaterialRequests = (")
if mr_comp != -1:
    for j in range(mr_comp, min(mr_comp+350, len(lines))):
        if "const filtered" in lines[j]:
            show("MR filter", j, j+15)
            break

print("=== DONE ===")
input("Press Enter...")
