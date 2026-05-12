APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def find(t):
    for i,l in enumerate(lines):
        if t in l: return i
    return -1

dr = find("const DailyReports = ({")

# Get exact line numbers we need
results = {}

# printData state line
for i,l in enumerate(lines):
    if "const [printData" in l and "useState" in l:
        results['printData'] = i
        break

# printRptId state line  
for i,l in enumerate(lines):
    if "const [printRptId" in l and "useState" in l:
        results['printRptId'] = i
        break

# Manpower label line
if dr != -1:
    for j in range(dr,min(dr+900,len(lines))):
        if "manpower" in lines[j] and "label:" in lines[j] and "Manpower" in lines[j]:
            results['mp_label'] = j
            break

# handlePrintDPR
hp = find("const handlePrintDPR =")
results['print_fn'] = hp

# useEffect with printRptId
for i,l in enumerate(lines):
    if "useEffect" in l and "printRptId" in l:
        results['print_ue'] = i
        break

# DprAttendancePanel usage
for i,l in enumerate(lines):
    if "DprAttendancePanel" in l and "display" in l and "activeSection" in l:
        results['panel'] = i
        break

# Print modal (setPrintData null button)
for i,l in enumerate(lines):
    if "setPrintData(null)" in l:
        results['modal'] = i
        break

print("=== KEY LINE NUMBERS ===")
for k,v in results.items():
    print(k+": L"+str(v+1 if v is not None else 'NOT FOUND'))
    if v is not None:
        print("  "+s(lines[v].rstrip())[:100])

# Show lines around printRptId state
pd = results.get('printRptId')
if pd is not None:
    print("\n=== Lines "+str(pd)+"-"+str(pd+10)+" ===")
    for j in range(pd, min(pd+10,len(lines))):
        print(str(j+1)+"\t"+s(lines[j].rstrip())[:100])

# Show manpower label full
ml = results.get('mp_label')
if ml is not None:
    print("\n=== Manpower label L"+str(ml+1)+" ===")
    print(s(lines[ml].rstrip()))

# Show handlePrintDPR full
pf = results.get('print_fn')
if pf is not None:
    print("\n=== handlePrintDPR ===")
    depth=0; end=pf
    for j in range(pf,min(pf+20,len(lines))):
        depth+=lines[j].count('{') - lines[j].count('}')
        print(str(j+1)+"\t"+s(lines[j].rstrip())[:100])
        if depth<=0 and j>pf: break

input("Press Enter...")
