import os

APP = r"src\App.js"
OUT = "diagnosis.txt"

with open(APP, "r", encoding="utf-8") as f:
    lines = f.readlines()

results = []
results.append("TOTAL LINES: " + str(len(lines)))

# Key checks
checks = [
    "const ManpowerMaster",
    "useManpowerMaster",
    'case "manpower-master"',
    "Module coming soon",
    "const MaterialStore",
    "approveReceipt",
    "updateReceipt",
    "onApproveReceipt",
    "function useStore",
    "LPOModule",
]
for c in checks:
    found = [(i+1, lines[i].strip()[:80]) for i,l in enumerate(lines) if c in l]
    results.append("\n[" + c + "] found " + str(len(found)) + " times:")
    for ln, txt in found[:3]:
        results.append("  line " + str(ln) + ": " + txt)

# Show renderPage switch
results.append("\n[RENDERPAGE SWITCH]")
in_switch = False
for i, line in enumerate(lines):
    if "const renderPage" in line or "switch (page)" in line or "switch(page)" in line:
        in_switch = True
    if in_switch:
        results.append(str(i+1) + ": " + line.rstrip()[:120])
        if i > 0 and "default:" in line:
            for j in range(i+1, min(i+5, len(lines))):
                results.append(str(j+1) + ": " + lines[j].rstrip()[:120])
            break
    if in_switch and i > 8400:
        break

# Show case store line
results.append("\n[CASE STORE]")
for i, line in enumerate(lines):
    if 'case "store"' in line:
        for j in range(max(0,i-1), min(len(lines),i+3)):
            results.append(str(j+1) + ": " + lines[j].rstrip()[:150])

# Show MaterialStore props
results.append("\n[MATERIALSTORE PROPS]")
for i, line in enumerate(lines):
    if "const MaterialStore" in line:
        for j in range(i, min(len(lines),i+8)):
            results.append(str(j+1) + ": " + lines[j].rstrip()[:120])
        break

output = "\n".join(results)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(output)

print(output)
print("\nSaved to: " + OUT)
print("Share the contents of diagnosis.txt")
input("Press Enter...")
