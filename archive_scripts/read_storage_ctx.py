import sys
sys.stdout.reconfigure(encoding='utf-8')
APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    lines = f.readlines()
out = []

# L790-815 — who uses supabase.storage at L800
out.append("=== L790-815 (L800 supabase.storage context) ===")
for i in range(789,815):
    out.append(f"L{i+1}: {lines[i].rstrip()[:160]}")

# L1015-1040 — L1027 drawings
out.append("\n=== L1015-1040 (L1027 drawings upload) ===")
for i in range(1014,1042):
    out.append(f"L{i+1}: {lines[i].rstrip()[:160]}")

# L11280-11300 — L11291 NOC
out.append("\n=== L11280-11300 (L11291 NOC upload) ===")
for i in range(11279,11302):
    out.append(f"L{i+1}: {lines[i].rstrip()[:160]}")

# exportToPDF full function L43-185
out.append("\n=== exportToPDF function L43-190 ===")
for i in range(42,191):
    out.append(f"L{i+1}: {lines[i].rstrip()[:160]}")

# Project view mode L2395-2442 (header section with sel data)
out.append("\n=== Project VIEW header L2395-2442 ===")
for i in range(2394,2443):
    out.append(f"L{i+1}: {lines[i].rstrip()[:160]}")

with open("storage_ctx_out.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("done")
