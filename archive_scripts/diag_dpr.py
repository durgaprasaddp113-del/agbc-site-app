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

# 1. ManpowerMaster component - first 10 lines
print("### ManpowerMaster component start ###")
mp = find("const ManpowerMaster = (")
if mp != -1: show("ManpowerMaster start", mp, mp+10)
else: print("NOT FOUND")

# 2. DailyReports component - full signature + manpower section
print("### DailyReports component start ###")
dr = find("const DailyReports = (")
if dr != -1: show("DailyReports start", dr, dr+20)

# 3. DPR manpower section - search for manpower keyword
print("### DPR manpower keywords ###")
if dr != -1:
    for j in range(dr, min(dr+800, len(lines))):
        l = lines[j].lower()
        if "manpower" in l or "labour" in l or "workforce" in l:
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:160])

# 4. useDailyReports hook
print("\n### useDailyReports hook ###")
udr = find("function useDailyReports")
if udr != -1: show("useDailyReports", udr, udr+50)

# 5. App() useManpowerMaster if exists
print("### App() useManpowerMaster ###")
app = find("export default function App")
if app != -1:
    for j in range(app, min(app+100, len(lines))):
        if "ManpowerMaster" in lines[j] or "manpower" in lines[j].lower():
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:160])

# 6. Existing ManpowerMaster case
print("\n### ManpowerMaster case ###")
for i,l in enumerate(lines):
    if "manpower-master" in l or "ManpowerMaster" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:160])

# 7. useNOCs hook end (to know where to insert new hook)
print("\n### useNOCs hook end ###")
noc_h = find("function useNOCs")
if noc_h != -1:
    # Find return statement of this hook
    for j in range(noc_h, min(noc_h+200, len(lines))):
        if "return {" in lines[j] and j > noc_h+10:
            show("useNOCs return", j, j+10)
            break

print("\n=== DONE ===")
input("Press Enter...")
