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

noc = find("const NOCModule = (")
if noc == -1:
    print("NOCModule not found"); exit()

# Find the table headers
print("### NOC TABLE HEADERS ###")
for j in range(noc, min(noc+700, len(lines))):
    l = lines[j]
    if '<thead' in l or ('th' in l and ('NOC' in l or 'Project' in l or 'Status' in l or 'Submit' in l or 'Expiry' in l or 'Auth' in l)):
        show("NOC headers area", j, j+8)
        break

# Find the table row rendering
print("### NOC TABLE ROW CELLS ###")
for j in range(noc, min(noc+700, len(lines))):
    l = lines[j]
    if '<tbody' in l:
        show("NOC tbody rows", j, j+40)
        break

print("=== DONE ===")
input("Press Enter...")
