import sys
sys.stdout.reconfigure(encoding='utf-8')
APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

out = []

out.append("=== getOverall function L2295-2340 ===")
for i in range(2294,2340):
    out.append(f"L{i+1}: {lines[i].rstrip()[:130]}")

out.append("\n=== Dashboard signature + overallPct usage L1732-1860 ===")
for i in range(1731,1860):
    l = lines[i].rstrip()
    if any(k in l for k in ['overallPct','progressItems','getOverall','const Dashboard','progress']):
        out.append(f"L{i+1}: {l[:130]}")

out.append("\n=== renderPage switch ===")
for i,l in enumerate(lines):
    if 'case "dashboard"' in l or ('const renderPage' in l):
        out.append(f"L{i+1}: {lines[i].rstrip()[:150]}")

out.append("\n=== useProjectProgress in App ===")
for i,l in enumerate(lines):
    if 'progressItems' in l and ('useProjectProgress' in l or 'const {' in l):
        out.append(f"L{i+1}: {lines[i].rstrip()[:150]}")

with open("dash2_out.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("done")
