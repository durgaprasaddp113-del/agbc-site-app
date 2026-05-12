APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

checks = {
    "DprAttendancePanel exists": "const DprAttendancePanel" in content,
    "useManpowerMaster exists": "function useManpowerMaster" in content,
    "attRowsRef exists": "attRowsRef" in content,
    "loadData gets att counts": "cntMap" in content,
    "Panel CSS show/hide": 'display:activeSection==="manpower"' in content,
    "saveAttendance updates DB": "manpower_total: presentCount" in content,
    "handlePrintDPR exists": "handlePrintDPR" in content,
    "showPrint state": "showPrint" in content,
    "printData state": "printData" in content,
}

print("=== CURRENT STATE ===")
for k,v in checks.items():
    print(("  [YES] " if v else "  [NO]  ") + k)

print("\nLines:", content.count('\n'))
input("\nPress Enter...")
