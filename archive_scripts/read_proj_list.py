import sys
sys.stdout.reconfigure(encoding='utf-8')
APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
out = []

# Project list table rows - look for {p.number} or number cell
out.append("=== Project list table rows L2640-2700 ===")
for i in range(2639,2710):
    out.append(f"L{i+1}: {lines[i].rstrip()[:150]}")

# usePhotos hook add function
out.append("\n=== usePhotos hook L1113-1200 ===")
for i in range(1112,1200):
    out.append(f"L{i+1}: {lines[i].rstrip()[:150]}")

# EMPTY_PHOTO_UPLOAD + Photos upload form date area
out.append("\n=== EMPTY_PHOTO_UPLOAD + upload form L4326-4420 ===")
for i in range(4325,4420):
    out.append(f"L{i+1}: {lines[i].rstrip()[:150]}")

# Project view mode buttons L2435-2445
out.append("\n=== Project view buttons L2435-2445 ===")
for i in range(2434,2446):
    out.append(f"L{i+1}: {lines[i].rstrip()[:150]}")

with open("proj_list_out.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("done")
