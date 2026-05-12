APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def find(t):
    for i,l in enumerate(lines): 
        if t in l: return i
    return -1

# Show handlePrintDPR exact current state
hp = find("const handlePrintDPR =")
print("handlePrintDPR at L"+str(hp+1 if hp!=-1 else -1))
if hp!=-1:
    depth=0
    for j in range(hp, min(hp+70,len(lines))):
        depth += lines[j].count('{') - lines[j].count('}')
        print(str(j+1)+": "+s(lines[j].rstrip())[:100])
        if depth<=0 and j>hp: break

# Show the button
print("\n── Export/Print button ──")
for i,l in enumerate(lines):
    if "handlePrintDPR(sel)" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:120])

input("Press Enter...")
