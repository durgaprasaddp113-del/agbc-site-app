APP = r"src\App.js"
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

# Fix: remove target=_blank, add download attribute instead
# Old: a.href=url; a.target='_blank'; a.rel='noopener';
# New: a.href=url; a.download='DPR_report.html';

old = "        a.href=url; a.target='_blank'; a.rel='noopener';\n"
new = "        a.download=(rpt.reportNum||'DPR')+'_'+(rpt.date||'')+'.html';\n"

if old in content:
    content = content.replace(old, new)
    print("FIX: Changed to download instead of open new tab")
    # Also update toast message
    content = content.replace(
        "showToast('Report opened! Use Ctrl+P to print from the new tab.');",
        "showToast('Report downloaded! Open the file and press Ctrl+P to print.');"
    )
    print("FIX: Toast message updated")
else:
    print("Pattern not found - trying alternate...")
    old2 = "a.target='_blank'; a.rel='noopener';"
    if old2 in content:
        content = content.replace(
            old2,
            "a.download=(rpt.reportNum||'DPR')+'_'+(rpt.date||'')+'.html';"
        )
        print("FIX: Alt pattern replaced")
    else:
        print("NOT FOUND")

with open(APP,"w",encoding="utf-8") as f:
    f.write(content)
print("Saved")
print("RUN: set CI=false && npm run build && npx vercel --prod --force")
input("Press Enter...")
