APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

# Fix: remove "inline-block" where "flex" is also present on same className
# L3221 and L3224 — the P/A badge spans in DprAttendanceViewPanel
old1 = 'className={`inline-block w-7 h-7 rounded-lg font-black text-sm flex items-center justify-center border-2 ${r.am==="P"?"bg-green-100 text-green-700 border-green-400":"bg-red-100 text-red-700 border-red-400"}`}'
new1 = 'className={`flex w-7 h-7 rounded-lg font-black text-sm items-center justify-center border-2 ${r.am==="P"?"bg-green-100 text-green-700 border-green-400":"bg-red-100 text-red-700 border-red-400"}`}'

old2 = 'className={`inline-block w-7 h-7 rounded-lg font-black text-sm flex items-center justify-center border-2 ${r.pm==="P"?"bg-green-100 text-green-700 border-green-400":"bg-red-100 text-red-700 border-red-400"}`}'
new2 = 'className={`flex w-7 h-7 rounded-lg font-black text-sm items-center justify-center border-2 ${r.pm==="P"?"bg-green-100 text-green-700 border-green-400":"bg-red-100 text-red-700 border-red-400"}`}'

c = 0
if old1 in content: content = content.replace(old1, new1); c+=1; print("FIX 1: AM badge inline-block removed")
if old2 in content: content = content.replace(old2, new2); c+=1; print("FIX 2: PM badge inline-block removed")
if c == 0:
    print("Trying line-by-line...")
    lines = content.split('\n')
    for i,l in enumerate(lines):
        if 'inline-block' in l and 'flex' in l and ('r.am' in l or 'r.pm' in l):
            lines[i] = l.replace('inline-block ', '', 1)
            c += 1; print(f"FIX {c}: L{i+1} fixed")
    content = '\n'.join(lines)

with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print(f"\nFixed {c} CSS conflicts")
print("These were warnings only — build would have worked anyway")
print("\nRun: set CI=false && npm run build")
input("Press Enter...")
