import sys
sys.stdout.reconfigure(encoding='utf-8')

APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

# Find pct around the map section (char 116000 onwards)
region = content[115800:116600]
lines = region.split('\n')
print("=== Lines around progress map ===")
for i,l in enumerate(lines):
    if 'pct' in l or 'progress_percentage' in l or 'activity' in l or 'unit' in l:
        print(f"  {i:3}: {repr(l)}")

with open("pct_out.txt","w",encoding="utf-8") as f:
    f.write(repr(region))
print("\nFull region saved to pct_out.txt")
