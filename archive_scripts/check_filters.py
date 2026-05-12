APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')
def find(t):
    for i,l in enumerate(lines):
        if t in l: return i
    return -1

print("=== FILTER CONDITIONS ===")
for i,l in enumerate(lines):
    if ("fProject" in l and "return false" in l) or ("_fpid" in l and "return false" in l):
        print(f"L{i+1}: {s(l.rstrip())[:110]}")

print("\n=== useMatReqs pid ===")
umr = find("function useMatReqs(")
if umr != -1:
    for j in range(umr, min(umr+50,len(lines))):
        if "pid:" in lines[j]:
            print(f"L{j+1}: {s(lines[j].rstrip())[:100]}")
            break

print("\n=== MR/LPO/NOC dropdown onChange ===")
for i,l in enumerate(lines):
    if "setFProject" in l and "onChange" in l:
        print(f"L{i+1}: {s(l.rstrip())[:120]}")

print("\n=== All Projects option values ===")
for i,l in enumerate(lines):
    if "All Projects" in l and "option" in l:
        import re
        m = re.search(r'value="([^"]*)"', l)
        val = m.group(1) if m else "?"
        print(f"L{i+1} val='{val}': {s(l.rstrip())[:80]}")

input("Press Enter...")
