APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

checks = {
    "Export button exists": "Export / Print" in content,
    "handlePrintDPR is async": "handlePrintDPR = async" in content,
    "Uses Blob download": "new Blob([html]" in content,
    "Uses a.download": "a.download=" in content and "a.target" not in content,
    "No window.open": "window.open(" not in content or content.count("window.open(") == 0,
    "showToast preparing": "Preparing report" in content,
    "Panel CSS show/hide": 'display:activeSection==="manpower"' in content,
    "attRowsRef exists": "attRowsRef" in content,
    "DprAttendancePanel exists": "const DprAttendancePanel" in content,
    "saveAttendance updates DB": "manpower_total: presentCount" in content,
    "loadData gets att counts": "dpr_attendance" in content and "cntMap" in content,
}

print("=== DEPLOYMENT VERIFICATION ===")
all_ok = True
for k,v in checks.items():
    status = "OK" if v else "MISSING"
    if not v: all_ok = False
    print(f"  [{status}] {k}")

print()
if all_ok:
    print("All checks passed - code is correct")
else:
    print("Some items missing - fixes not applied")

# Show window.open occurrences
import re
opens = [(i+1, l.strip()[:80]) for i,l in enumerate(content.split('\n')) if 'window.open(' in l]
if opens:
    print("\nwindow.open occurrences:")
    for ln, txt in opens[:5]:
        print(f"  L{ln}: {txt}")

# Show a.download
downloads = [(i+1, l.strip()[:80]) for i,l in enumerate(content.split('\n')) if 'a.download=' in l]
print("\na.download occurrences:")
for ln,txt in downloads[:3]:
    print(f"  L{ln}: {txt}")

# Show a.target
targets = [(i+1, l.strip()[:80]) for i,l in enumerate(content.split('\n')) if "a.target=" in l]
if targets:
    print("\na.target occurrences (should be 0):")
    for ln,txt in targets[:3]:
        print(f"  L{ln}: {txt}")

input("\nPress Enter...")
