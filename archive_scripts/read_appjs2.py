import sys
sys.stdout.reconfigure(encoding='utf-8')

APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

out = []
out.append(f"Total lines: {len(lines)}")
out.append("\n=== Key functions/hooks ===")
keywords = ["function use","const use","function App","renderPage","case \"","const ManpowerMaster","const DprAttendance","const DailyReports","const LPOModule","const MaterialRequests","const NOCModule","const MaterialStore","const Projects","const Tasks","const Snags","const Users","const Subcontractors","const Dashboard"]
for i,l in enumerate(lines):
    for k in keywords:
        if k in l and (l.strip().startswith("const ") or l.strip().startswith("function ") or l.strip().startswith("case ")):
            safe = l.rstrip().encode('ascii',errors='replace').decode('ascii')[:100]
            out.append(f"L{i+1}: {safe}")
            break

with open("read_out2.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("Done — see read_out2.txt")
