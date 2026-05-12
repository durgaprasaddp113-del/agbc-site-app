APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# Find the actual handlePrintDPR function definition
print("── All handlePrintDPR occurrences ──")
for i,l in enumerate(lines):
    if "handlePrintDPR" in l:
        print("L"+str(i+1)+": "+s(l.rstrip())[:120])

input("Press Enter...")
