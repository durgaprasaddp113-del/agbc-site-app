import sys
sys.stdout.reconfigure(encoding='utf-8')
APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
out = []

# 1. EMPTY_PHOTO_UPLOAD exact line
out.append("=== EMPTY_PHOTO_UPLOAD ===")
for i,l in enumerate(lines):
    if 'EMPTY_PHOTO_UPLOAD' in l or 'todayStr' in l:
        out.append(f"L{i+1}: {l.rstrip()}")

# 2. useState uploadForm exact line
out.append("\n=== useState uploadForm ===")
for i,l in enumerate(lines):
    if 'uploadForm' in l and 'useState' in l:
        out.append(f"L{i+1}: {l.rstrip()}")

# 3. After upload reset line
out.append("\n=== upload reset line ===")
for i,l in enumerate(lines):
    if 'Photo uploaded to R2' in l:
        out.append(f"L{i+1}: {l.rstrip()}")

# 4. PDF button exact
out.append("\n=== PDF export button ===")
for i,l in enumerate(lines):
    if 'exportProjectReportPDF' in l:
        out.append(f"L{i+1}: {l.rstrip()[:150]}")

# 5. Projects component signature
out.append("\n=== Projects component signature ===")
for i,l in enumerate(lines):
    if 'const Projects = (' in l:
        out.append(f"L{i+1}: {l.rstrip()[:150]}")

# 6. pp object
out.append("\n=== pp object ===")
for i,l in enumerate(lines):
    if 'const pp = {' in l:
        out.append(f"L{i+1}: {l.rstrip()[:150]}")

# 7. projPhotos in PDF function
out.append("\n=== projPhotos in PDF ===")
for i,l in enumerate(lines):
    if 'projPhotos' in l or 'toB64' in l:
        out.append(f"L{i+1}: {l.rstrip()[:150]}")

with open("photo_exact_out.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("done")
