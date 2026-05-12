import sys
sys.stdout.reconfigure(encoding='utf-8')

APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

sections = {
    "Dashboard component (L1732-1800)": (1731, 1800),
    "getOverall function": None,
    "overallPct usage": None,
    "progress_percentage in DB update": None,
    "Projects card progress bar": (2074, 2180),
    "renderPage dashboard case": (11800, 11830),
}

print("=== Dashboard component props + progress display ===")
for i in range(1731, 1800):
    l = lines[i].rstrip()
    if any(k in l for k in ['progress','overall','pct','Overall','Progress','getOverall']):
        print(f"L{i+1}: {l}")

print("\n=== getOverall function ===")
for i,l in enumerate(lines):
    if 'getOverall' in l or 'overallPct' in l:
        print(f"L{i+1}: {l.rstrip()[:120]}")

print("\n=== progress_percentage DB save (update) ===")
for i,l in enumerate(lines):
    if 'progress_percentage' in l:
        print(f"L{i+1}: {l.rstrip()[:120]}")

print("\n=== Project card progress bar (L2074-2200) ===")
for i in range(2073, 2250):
    l = lines[i].rstrip()
    if any(k in l for k in ['progress','overall','pct','Overall','Progress','%']):
        print(f"L{i+1}: {l[:120]}")

print("\n=== renderPage dashboard props ===")
for i in range(11799, 11830):
    print(f"L{i+1}: {lines[i].rstrip()[:150]}")
