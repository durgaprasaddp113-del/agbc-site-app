import shutil
from datetime import datetime

APP = r"src\App.js"
bk = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)

with open(APP, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

def s(x): return x.encode('ascii', errors='replace').decode('ascii')

# Find the orphaned old hook code
# Look for getActiveBySubcontractor and the old return statement outside a hook
start = -1
end   = -1
for i, l in enumerate(lines):
    # Find where orphaned old hook code starts (after the new hook ends)
    if 'getActiveBySubcontractor' in l and start == -1:
        # Scan backwards to find the function start (const getActive...)
        for j in range(i, max(i-10, 0), -1):
            if lines[j].strip().startswith('const getActive') or lines[j].strip().startswith('const load') or 'useCallback' in lines[j]:
                start = j
                break
        if start == -1:
            start = i  # fallback: start at the getActive line itself

for i, l in enumerate(lines):
    if start != -1 and i >= start:
        stripped = l.strip()
        # The old hook ends with }  followed by blank line and a comment
        if (stripped == '}' or stripped == '};') and i > start + 1:
            # Check if next non-blank line is a comment or new component
            for k in range(i+1, min(i+5, len(lines))):
                nxt = lines[k].strip()
                if nxt:
                    if nxt.startswith('//') or nxt.startswith('const ') or nxt.startswith('function '):
                        end = i
                    break
            if end != -1:
                break

print(f"Orphaned block: L{start+1} → L{end+1}")
print("Orphaned content preview:")
for i in range(start, min(end+1, len(lines))):
    print(f"  L{i+1}: {s(lines[i].rstrip())[:80]}")

if start != -1 and end != -1 and start < end:
    del lines[start:end+1]
    print(f"\nREMOVED {end-start+1} orphaned lines")
    with open(APP, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("File saved.")
else:
    # Fallback: search for exact orphaned patterns and remove them
    print("\nFallback: searching for exact orphaned patterns...")
    content = "".join(lines)
    
    # Remove orphaned getActiveBySubcontractor + old return block
    patterns_to_remove = []
    new_lines = []
    skip = False
    skip_end_marker = ""
    
    for i, l in enumerate(lines):
        # Skip lines that are part of orphaned old hook
        if 'getActiveBySubcontractor' in l and 'const getActive' in l:
            skip = True
        if skip:
            stripped = l.strip()
            if (stripped == '}' or stripped == '};') and i > 0:
                skip = False  # stop after closing brace
                continue  # skip the closing brace too
            continue
        # Also remove old return with getActiveBySubcontractor
        if 'return {' in l and 'getActiveBySubcontractor' in l:
            continue
        # Remove the closing brace after that return
        new_lines.append(l)
    
    with open(APP, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"Fallback: removed orphaned lines. New total: {len(new_lines)}")

print()
print("Now run:")
print("  set CI=false && npm run build")
input("Press Enter...")
