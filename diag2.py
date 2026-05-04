import os

APP = r"src\App.js"
OUT = "diag2.txt"

with open(APP, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []

def show(label, start, count=40):
    out.append("\n=== " + label + " (line " + str(start+1) + ") ===")
    for i in range(start, min(start+count, len(lines))):
        out.append(str(i+1) + ": " + lines[i].rstrip()[:130])

# 1. useStore return object
for i,l in enumerate(lines):
    if "function useStore() {" in l:
        # Find the return statement near end of useStore
        for j in range(i+1, min(i+500, len(lines))):
            if "return {" in lines[j] and "ok:" not in lines[j]:
                show("useStore RETURN OBJECT", j, 15)
                break
        break

# 2. MaterialStore first 60 lines after props
for i,l in enumerate(lines):
    if "const MaterialStore = ({" in l:
        show("MaterialStore COMPONENT START", i, 60)
        break

# 3. LPO form section
lpo_start = 0
for i,l in enumerate(lines):
    if "const LPOModule = (" in l:
        lpo_start = i
        break

# Find form inside LPO
for i in range(lpo_start, min(lpo_start+600, len(lines))):
    if ('mode === "form"' in lines[i] or 'mode==="form"' in lines[i] or
        'return (' in lines[i] and i > lpo_start+50):
        show("LPO FORM SECTION", i, 80)
        break

result = "\n".join(out)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(result)

print(result)
print("\nSaved to diag2.txt — share its contents")
input("Press Enter...")
