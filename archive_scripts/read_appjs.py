APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
print(f"Total lines: {len(lines)}")
print("\n=== TOP 50 lines ===")
for i,l in enumerate(lines[:50]):
    print(f"L{i+1}: {l.rstrip()[:120]}")

print("\n=== Key components/functions ===")
keywords = [
    "function use","const use","= ({","const App ",
    "function App","renderPage","case \"",
    "ManpowerMaster","DprAttendancePanel","useManpowerMaster",
    "loadFromMaster","useLPOs","useMatReqs","useNOCs",
    "DailyReports","LPOModule","MaterialRequests","NOCModule"
]
for i,l in enumerate(lines):
    for k in keywords:
        if k in l and (l.strip().startswith("const ") or l.strip().startswith("function ") or l.strip().startswith("case ")):
            print(f"L{i+1}: {l.rstrip()[:100]}")
            break
input("Press Enter...")
