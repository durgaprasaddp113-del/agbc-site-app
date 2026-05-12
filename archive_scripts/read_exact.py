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

print("Lines:",len(lines))

# 1. EXACT useDailyReports loadData function
udr = find("function useDailyReports()")
print("\n### useDailyReports loadData ###")
if udr!=-1:
    for j in range(udr,min(udr+60,len(lines))):
        print(str(j+1)+"\t"+s(lines[j].rstrip()))
        if "return { reports" in lines[j]: break

# 2. EXACT saveAttendance function
print("\n### saveAttendance ###")
sa = find("saveAttendance = async (dprId, rows)")
if sa!=-1: show("saveAttendance",sa,sa+25)

# 3. EXACT handleSave in DailyReports
dr = find("const DailyReports = ({")
print("\n### handleSave ###")
if dr!=-1:
    for j in range(dr,min(dr+500,len(lines))):
        if "handleSave = async" in lines[j]:
            show("handleSave",j,j+45)
            break

# 4. EXACT list row manpower display
print("\n### list row mp ###")
if dr!=-1:
    for j in range(dr,min(dr+900,len(lines))):
        if ("const mp" in lines[j] or "manpowerTotal" in lines[j]) and j>dr+300:
            print(str(j+1)+"\t"+s(lines[j].rstrip())[:120])
        if "{mp}" in lines[j] or "mp}" in lines[j]:
            print(str(j+1)+"\t"+s(lines[j].rstrip())[:120])

# 5. EXACT handlePrintDPR
print("\n### handlePrintDPR ###")
hp = find("handlePrintDPR =")
if hp!=-1:
    depth=0; end=hp
    for j in range(hp,min(hp+60,len(lines))):
        depth+=lines[j].count('{') - lines[j].count('}')
        if depth<=0 and j>hp: end=j; break
    show("handlePrintDPR",hp,end+1)

print("=== DONE ===")
input("Press Enter...")
