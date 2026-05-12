APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
def s(x): return x.encode('ascii',errors='replace').decode('ascii')

# Show DprAttendancePanel usage block in full
print("── DprAttendancePanel usage in form ──")
for i,l in enumerate(lines):
    if "<DprAttendancePanel" in l and ("dprId" in l or "mpAttDprId" in l):
        for j in range(i, min(i+20, len(lines))):
            print(f"L{j+1}: {s(lines[j].rstrip())}")
            if "/>" in lines[j] and j > i:
                break
        break

input("\nPress Enter...")
