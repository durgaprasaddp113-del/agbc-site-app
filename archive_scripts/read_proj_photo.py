import sys
sys.stdout.reconfigure(encoding='utf-8')
APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

out = []

# 1. Project list table — project number cell (around L2074-2280)
out.append("=== Project LIST rows (number column) L2380-2460 ===")
for i in range(2379,2470):
    l = lines[i].rstrip()
    if any(k in l for k in ['number','onClick','openView','cursor','td','tr']):
        out.append(f"L{i+1}: {l[:140]}")

# 2. Project VIEW mode export area (around L2397-2580)
out.append("\n=== Project VIEW mode header/export L2395-2580 ===")
for i in range(2394,2580):
    l = lines[i].rstrip()
    if any(k in l for k in ['export','Export','PDF','Excel','Print','btn','Btn','button','Button','goList','Edit','Delete','overall']):
        out.append(f"L{i+1}: {l[:140]}")

# 3. Photos component — full signature + key logic
out.append("\n=== Photos component signature + state ===")
for i,l in enumerate(lines):
    if 'const Photos = (' in l:
        out.append(f"\nL{i+1}: {l.rstrip()}")
        for j in range(i+1, min(i+80, len(lines))):
            out.append(f"L{j+1}: {lines[j].rstrip()[:140]}")
        break

# 4. Photos upload/save logic
out.append("\n=== Photos upload + save logic ===")
for i,l in enumerate(lines):
    if any(k in l for k in ['uploadToR2','r2Storage','photo_date','photoDate','addPhoto','onAdd','file','File']):
        if 'Photos' in ''.join(lines[max(0,i-30):i+1]) or i > 1113:
            out.append(f"L{i+1}: {lines[i].rstrip()[:140]}")

with open("proj_photo_out.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("done")
