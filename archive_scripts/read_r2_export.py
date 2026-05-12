import sys
sys.stdout.reconfigure(encoding='utf-8')
APP = r"src\App.js"
R2  = r"src\r2Storage.js"

with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()

out = []

# 1. r2Storage.js full content
out.append("=== r2Storage.js FULL ===")
try:
    with open(R2,"r",encoding="utf-8",errors="replace") as f:
        for i,l in enumerate(f.readlines()):
            out.append(f"L{i+1}: {l.rstrip()[:160]}")
except:
    out.append("FILE NOT FOUND")

# 2. uploadToR2 usage in App.js
out.append("\n=== uploadToR2 calls in App.js ===")
for i,l in enumerate(lines):
    if 'uploadToR2' in l or 'r2Storage' in l or 'R2' in l:
        out.append(f"L{i+1}: {lines[i].rstrip()[:150]}")

# 3. Photos upload form full (L4384-4440)
out.append("\n=== Photos upload form L4384-4445 ===")
for i in range(4383,4445):
    out.append(f"L{i+1}: {lines[i].rstrip()[:150]}")

# 4. exportToPDF / exportToExcel functions
out.append("\n=== export functions definition ===")
for i,l in enumerate(lines):
    if any(k in l for k in ['const exportToPDF','const exportToExcel','function exportT','jsPDF','autoTable','XLSX.utils']):
        out.append(f"L{i+1}: {lines[i].rstrip()[:150]}")

# 5. Photos grid card display (around L4460-4520)
out.append("\n=== Photos grid/card L4460-4530 ===")
for i in range(4459,4530):
    out.append(f"L{i+1}: {lines[i].rstrip()[:150]}")

# 6. NOC upload (uses supabase storage — need to find)
out.append("\n=== NOC/Drawings file upload ===")
for i,l in enumerate(lines):
    if 'supabase.storage' in l or 'site-photos' in l or 'storage.from' in l:
        out.append(f"L{i+1}: {lines[i].rstrip()[:150]}")

with open("r2_export_out.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("done")
