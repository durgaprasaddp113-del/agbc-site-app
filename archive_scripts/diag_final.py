APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def show(l,a,b):
    print("=== "+l+" ===")
    for i in range(a,min(b,len(lines))):
        print(str(i+1)+"\t"+s(lines[i].rstrip()))
    print()
def find(t):
    for i,l in enumerate(lines):
        if t in l: return i
    return -1

print("Lines:", len(lines))

# 1. handlePrintDPR full
hp = find("handlePrintDPR = ")
if hp != -1:
    end = hp
    d = 0
    for j in range(hp, min(hp+15,len(lines))):
        d += lines[j].count('{') - lines[j].count('}')
        if d<=0 and j>hp: end=j; break
    show("handlePrintDPR", hp, end+1)

# 2. printRptId state
print("### printRptId ###")
for i,l in enumerate(lines):
    if "printRptId" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:120])

# 3. printData useEffect
print("\n### printData/printRptId useEffect ###")
for i,l in enumerate(lines):
    if "useEffect" in l and ("printData" in l or "printRptId" in l):
        print("L"+str(i+1)+": "+s(l.rstrip())[:120])

# 4. handleSave goList line
print("\n### goList in handleSave ###")
dr = find("const DailyReports = ({")
if dr != -1:
    for j in range(dr, min(dr+400,len(lines))):
        if "goList" in lines[j] and "showToast" in lines[j]:
            print("L"+str(j+1)+": "+s(lines[j].rstrip())[:120])

# 5. useDailyReports return
print("\n### useDailyReports return ###")
udr = find("function useDailyReports()")
if udr != -1:
    for j in range(udr, min(udr+150,len(lines))):
        if "return {" in lines[j] and j > udr+5:
            show("useDailyReports return", j, j+3)
            break

# 6. manpower_total in list row
print("### List row manpower ###")
if dr != -1:
    for j in range(dr, min(dr+800,len(lines))):
        if "workers" in lines[j] and ("manpower" in lines[j].lower() or "mp" in lines[j]):
            if "<td" in lines[j] or "span" in lines[j]:
                print("L"+str(j+1)+": "+s(lines[j].rstrip())[:120])

print("\n=== DONE ===")
input("Press Enter...")
