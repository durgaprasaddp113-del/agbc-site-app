APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

# Revert <details> back to <div>
old = '<details className="bg-white rounded-xl border border-slate-200 overflow-x-auto"><summary className="px-4 py-2 text-xs text-slate-400 cursor-pointer select-none">Legacy summary (tap to expand)</summary>'
new = '<div className="bg-white rounded-xl border border-slate-200 overflow-x-auto">'

if old in content:
    content = content.replace(old, new)
    print("FIX: details reverted to div")
else:
    print("Pattern not found - checking for partial...")
    if "<details" in content:
        # Line by line fix
        lines = content.split('\n')
        for i,l in enumerate(lines):
            if "<details" in l and "rounded-xl" in l:
                lines[i] = l.split('<details')[0] + '<div className="bg-white rounded-xl border border-slate-200 overflow-x-auto">'
                print(f"Fixed line {i+1}")
                break
        content = '\n'.join(lines)

with open(APP,"w",encoding="utf-8") as f:
    f.write(content)
print("Saved")
print("\nRun: set CI=false && npm run build")
input("Press Enter...")
