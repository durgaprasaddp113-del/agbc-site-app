# Rewrites r2Storage.js + fixes all 3 Supabase storage usages + adds comprehensive project PDF export

import shutil, re
from datetime import datetime

APP   = r"src\App.js"
R2    = r"src\r2Storage.js"
bk    = APP + ".bak_" + datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy2(APP, bk)
print(f"Backup App.js: {bk}")

# ══════════════════════════════════════════════════════════════════
# 1. REWRITE r2Storage.js COMPLETELY
# ══════════════════════════════════════════════════════════════════
R2_CODE = r'''const WORKER_URL  = process.env.REACT_APP_R2_WORKER_URL;
const AUTH_TOKEN  = process.env.REACT_APP_R2_AUTH_TOKEN;
const PUBLIC_BASE = process.env.REACT_APP_R2_PUBLIC_BASE;

// Validate image file — returns { ok, error }
export const validateImageFile = (file, maxMB = 5) => {
  const allowed = ['image/jpeg','image/jpg','image/png','image/webp','image/gif'];
  if (!allowed.includes(file.type))
    return { ok: false, error: 'Invalid file type. Only JPEG, PNG, WebP and GIF allowed.' };
  if (file.size > maxMB * 1024 * 1024)
    return { ok: false, error: `File too large. Maximum size is ${maxMB}MB.` };
  return { ok: true, error: null };
};

// Generate unique filename
export const generateFileName = (file) => {
  const ts  = Date.now();
  const rnd = Math.random().toString(36).substring(2, 8);
  const ext = file.name.split('.').pop().toLowerCase();
  return `${ts}-${rnd}.${ext}`;
};

// Upload any file to R2 — returns Promise<{ ok, url, error }>
// Supports progress callback via XHR
export const uploadToR2 = (file, folder = 'uploads', onProgress = null) => {
  return new Promise((resolve) => {
    try {
      const fileName = generateFileName(file);
      const key      = `${folder}/${fileName}`;
      const endpoint = `${WORKER_URL}/upload/${encodeURIComponent(key)}`;

      const xhr = new XMLHttpRequest();

      if (onProgress) {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable)
            onProgress(Math.round((e.loaded / e.total) * 95));
        });
      }

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          if (onProgress) onProgress(100);
          resolve({ ok: true, url: `${PUBLIC_BASE}/${key}` });
        } else {
          resolve({ ok: false, error: `Upload failed (${xhr.status}): ${xhr.statusText}` });
        }
      });

      xhr.addEventListener('error', () =>
        resolve({ ok: false, error: 'Network error during upload — check R2 Worker URL.' })
      );
      xhr.addEventListener('abort', () =>
        resolve({ ok: false, error: 'Upload was cancelled.' })
      );

      xhr.open('PUT', endpoint);
      xhr.setRequestHeader('Content-Type', file.type || 'application/octet-stream');
      xhr.setRequestHeader('X-Auth-Token', AUTH_TOKEN);
      xhr.send(file);

    } catch (err) {
      resolve({ ok: false, error: err.message });
    }
  });
};

// Delete file from R2 by full URL or key
export const deleteFromR2 = async (fileUrlOrKey) => {
  try {
    const key = fileUrlOrKey.startsWith('http')
      ? fileUrlOrKey.replace(PUBLIC_BASE + '/', '')
      : fileUrlOrKey;
    const res = await fetch(`${WORKER_URL}/delete/${encodeURIComponent(key)}`, {
      method: 'DELETE',
      headers: { 'X-Auth-Token': AUTH_TOKEN },
    });
    return res.ok;
  } catch { return false; }
};

// Human-readable file size
export const fileSizeLabel = (bytes) => {
  if (!bytes) return '0 Bytes';
  const k = 1024;
  const s = ['Bytes','KB','MB','GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + s[i];
};
'''

with open(R2, 'w', encoding='utf-8') as f:
    f.write(R2_CODE)
print("FIX 1: r2Storage.js rewritten — validateImageFile returns {ok}, uploadToR2 uses XHR + returns {ok,url} ✅")

# ══════════════════════════════════════════════════════════════════
# 2. PATCH App.js
# ══════════════════════════════════════════════════════════════════
with open(APP,"r",encoding="utf-8",errors="replace") as f:
    content = f.read()

changes = 0

# ── FIX 2: Snags uploadPhoto → R2 ──────────────────────────────
OLD_SNAG = '''  const uploadPhoto = async (file, folder) => {
    const ext = file.name.split(".").pop();
    const fileName = `${folder}/${Date.now()}_${Math.random().toString(36).slice(2)}.${ext}`;
    const { error } = await supabase.storage.from("site-photos").upload(fileName, file);
    if (error) { console.error("Photo upload:", error.message); return null; }
    const { data: { publicUrl } } = supabase.storage.from("site-photos").getPublicUrl(fileName);
    return publicUrl;
  };'''
NEW_SNAG = '''  const uploadPhoto = async (file, folder) => {
    const r2 = await uploadToR2(file, `snag-photos/${folder}`);
    if (!r2.ok) { console.error("Snag photo upload:", r2.error); return null; }
    return r2.url;
  };'''
if OLD_SNAG in content:
    content = content.replace(OLD_SNAG, NEW_SNAG, 1)
    changes += 1
    print("FIX 2: Snags uploadPhoto → R2 ✅")
else:
    print("WARN FIX 2: Snags uploadPhoto pattern not found")

# ── FIX 3: Drawings uploadFile → R2 ────────────────────────────
OLD_DWG = '''  const uploadFile = async (file) => {
    const ext = file.name.split(".").pop();
    const name = `${Date.now()}_${Math.random().toString(36).slice(2)}.${ext}`;
    const { error } = await supabase.storage.from("drawings").upload(name, file);
    if (error) { console.error("File upload:", error.message); return null; }
    const { data: { publicUrl } } = supabase.storage.from("drawings").getPublicUrl(name);
    return publicUrl;
  };'''
NEW_DWG = '''  const uploadFile = async (file) => {
    const r2 = await uploadToR2(file, "drawings");
    if (!r2.ok) { console.error("Drawing file upload:", r2.error); return null; }
    return r2.url;
  };'''
if OLD_DWG in content:
    content = content.replace(OLD_DWG, NEW_DWG, 1)
    changes += 1
    print("FIX 3: Drawings uploadFile → R2 ✅")
else:
    print("WARN FIX 3: Drawings uploadFile pattern not found")

# ── FIX 4: NOC uploadFile → R2 ─────────────────────────────────
OLD_NOC = '''  const uploadFile = async (file) => {
    const ext = file.name.split(".").pop();
    const name = `noc_${Date.now()}_${Math.random().toString(36).slice(2)}.${ext}`;
    const { error } = await supabase.storage.from("site-photos").upload(name, file);
    if (error) { console.error("Upload:", error.message); return null; }
    const { data: { publicUrl } } = supabase.storage.from("site-photos").getPublicUrl(name);
    return publicUrl;
  };'''
NEW_NOC = '''  const uploadFile = async (file) => {
    const r2 = await uploadToR2(file, "noc-files");
    if (!r2.ok) { console.error("NOC file upload:", r2.error); return null; }
    return r2.url;
  };'''
if OLD_NOC in content:
    content = content.replace(OLD_NOC, NEW_NOC, 1)
    changes += 1
    print("FIX 4: NOC uploadFile → R2 ✅")
else:
    print("WARN FIX 4: NOC uploadFile pattern not found")

# ── FIX 5: Add exportProjectReportPDF after exportToPDF ────────
EXPORT_PDF_END = '  } catch(e) { console.error("PDF export error:", e); alert("PDF export failed: " + e.message); }\n};\n\nconst exportLpoPDF'

PROJECT_REPORT_FN = '''  } catch(e) { console.error("PDF export error:", e); alert("PDF export failed: " + e.message); }
};

// ─── COMPREHENSIVE PROJECT PROGRESS REPORT ────────────────────────────────────
const exportProjectReportPDF = (sel, pgItems, overallPct) => {
  try {
    const { jsPDF } = window.jspdf;
    if (!jsPDF) { alert("PDF library not loaded. Refresh and try again."); return; }
    const doc     = new jsPDF({ orientation:"portrait", format:"a4", compress:true });
    const pageW   = doc.internal.pageSize.getWidth();
    const pageH   = doc.internal.pageSize.getHeight();
    const MARGIN  = 12;
    const usableW = pageW - MARGIN * 2;
    const now     = new Date().toLocaleString("en-GB",{dateStyle:"medium",timeStyle:"short"});
    const today   = new Date().toLocaleDateString("en-GB").replace(/\//g,"-");

    // Header constants
    const HDR_H  = 38;
    const LOGO_H = HDR_H - 8;
    const LOGO_W = Math.min(LOGO_H * 4.7, usableW * 0.55);
    const LOGO_X = MARGIN;
    const LOGO_Y = (HDR_H - LOGO_H) / 2;
    let pgCount  = 0;

    const drawHeader = () => {
      pgCount++;
      doc.setFillColor(30,41,59);   doc.rect(0,0,pageW,HDR_H,"F");
      doc.setFillColor(245,158,11); doc.rect(0,HDR_H,pageW,2.5,"F");
      try {
        doc.addImage("data:image/jpeg;base64,"+AGBC_LOGO_B64,"JPEG",LOGO_X,LOGO_Y,LOGO_W,LOGO_H);
      } catch(e) {
        doc.setTextColor(245,158,11); doc.setFontSize(14); doc.setFont("helvetica","bold");
        doc.text("AGBC",LOGO_X+2,HDR_H/2+4);
      }
      doc.setTextColor(255,255,255); doc.setFontSize(10); doc.setFont("helvetica","bold");
      doc.text("PROJECT PROGRESS REPORT",pageW-MARGIN,HDR_H/2-4,{align:"right"});
      doc.setFontSize(6.5); doc.setFont("helvetica","normal"); doc.setTextColor(160,160,160);
      doc.text(now,pageW-MARGIN,HDR_H-5,{align:"right"});
    };

    drawHeader();
    let y = HDR_H + 8;

    // ── Project title block
    doc.setFillColor(248,250,252); doc.setDrawColor(226,232,240); doc.setLineWidth(0.3);
    doc.roundedRect(MARGIN,y,usableW,22,2,2,"FD");
    doc.setTextColor(245,158,11); doc.setFontSize(8); doc.setFont("helvetica","bold");
    doc.text(sel.number||"",MARGIN+4,y+7);
    doc.setTextColor(30,41,59); doc.setFontSize(13);
    doc.text(sel.name||"",MARGIN+4,y+16);
    const SC={"Active":[16,185,129],"Completed":[59,130,246],"On Hold":[245,158,11],"Cancelled":[239,68,68]};
    const sc=SC[sel.status]||[148,163,184];
    doc.setFillColor(...sc); doc.roundedRect(pageW-MARGIN-28,y+7,25,8,2,2,"F");
    doc.setTextColor(255,255,255); doc.setFontSize(7); doc.setFont("helvetica","bold");
    doc.text(sel.status||"—",pageW-MARGIN-15.5,y+13,{align:"center"});
    y+=27;

    // ── Project info grid
    doc.setFontSize(8.5); doc.setFont("helvetica","bold"); doc.setTextColor(100,116,139);
    doc.text("PROJECT DETAILS",MARGIN,y+4);
    doc.setDrawColor(245,158,11); doc.setLineWidth(0.4);
    doc.line(MARGIN,y+5.5,MARGIN+36,y+5.5);
    y+=10;
    const INFO=[
      ["Project No.",    sel.number||"—"],
      ["Location",       sel.location||"—"],
      ["Duration",       sel.duration?sel.duration+" Months":"—"],
      ["Plot Area",      sel.plotArea?sel.plotArea+" sqft":"—"],
      ["BUA",            sel.bua?sel.bua+" sqft":"—"],
      ["Start Date",     sel.startDate||"—"],
      ["End Date",       sel.endDate||"—"],
      ["Consultant",     sel.consultant||"—"],
      ["Consultant Tel", sel.consultantContact||"—"],
      ["Status",         sel.status||"—"],
    ];
    const colW = (usableW-4)/2;
    INFO.forEach(([lbl,val],idx)=>{
      const cx=MARGIN+(idx%2)*(colW+4);
      const cy=y+Math.floor(idx/2)*11;
      doc.setFontSize(6); doc.setFont("helvetica","normal"); doc.setTextColor(148,163,184);
      doc.text(lbl,cx,cy);
      doc.setFontSize(7.5); doc.setFont("helvetica","bold"); doc.setTextColor(30,41,59);
      doc.text(String(val).substring(0,42),cx,cy+5.5);
    });
    y+=Math.ceil(INFO.length/2)*11+6;

    // ── KPI boxes
    doc.setFontSize(8.5); doc.setFont("helvetica","bold"); doc.setTextColor(100,116,139);
    doc.text("PROGRESS OVERVIEW",MARGIN,y+4);
    doc.setDrawColor(245,158,11); doc.line(MARGIN,y+5.5,MARGIN+43,y+5.5);
    y+=10;
    const comp=pgItems.filter(i=>i.status==="Completed").length;
    const inp=pgItems.filter(i=>i.status==="In Progress").length;
    const nst=pgItems.filter(i=>i.status==="Not Started").length;
    const ohd=pgItems.filter(i=>i.status==="On Hold").length;
    const KPIS=[
      {l:"Overall",     v:overallPct+"%",   c:[59,130,246]},
      {l:"Total",       v:pgItems.length,   c:[100,116,139]},
      {l:"Completed",   v:comp,             c:[16,185,129]},
      {l:"In Progress", v:inp,              c:[245,158,11]},
      {l:"Not Started", v:nst,              c:[239,68,68]},
      {l:"On Hold",     v:ohd,              c:[168,85,247]},
    ];
    const kw=(usableW-2*(KPIS.length-1))/KPIS.length;
    KPIS.forEach((k,i)=>{
      const kx=MARGIN+i*(kw+2);
      doc.setFillColor(...k.c); doc.roundedRect(kx,y,kw,18,2,2,"F");
      doc.setTextColor(255,255,255); doc.setFontSize(14); doc.setFont("helvetica","bold");
      doc.text(String(k.v),kx+kw/2,y+12,{align:"center"});
      doc.setFontSize(5.5); doc.setFont("helvetica","normal");
      doc.text(k.l,kx+kw/2,y+17,{align:"center"});
    });
    y+=23;

    // ── Overall progress bar
    doc.setFillColor(241,245,249); doc.roundedRect(MARGIN,y,usableW,8,2,2,"F");
    const fill=Math.max(0.5,(overallPct/100)*usableW);
    const barClr=overallPct>=80?[16,185,129]:overallPct>=50?[59,130,246]:overallPct>=25?[245,158,11]:[239,68,68];
    doc.setFillColor(...barClr); doc.roundedRect(MARGIN,y,fill,8,2,2,"F");
    doc.setTextColor(overallPct>45?255:30,overallPct>45?255:41,overallPct>45?255:59);
    doc.setFontSize(6); doc.setFont("helvetica","bold");
    doc.text(overallPct+"% Complete · "+comp+" of "+pgItems.length+" activities done",MARGIN+usableW/2,y+5.5,{align:"center"});
    y+=14;

    // ── Totals row for qty-based activities
    const qtyItems=pgItems.filter(i=>i.unit!=="Lumpsum"&&(Number(i.actualQty)||0)>0);
    if(qtyItems.length>0){
      const totA=qtyItems.reduce((s,i)=>s+(Number(i.actualQty)||0),0);
      const totD=qtyItems.reduce((s,i)=>s+(Number(i.workDoneQty)||0),0);
      const totB=qtyItems.reduce((s,i)=>s+(Number(i.balanceQty)||0),0);
      doc.setFillColor(254,252,232); doc.setDrawColor(253,230,138); doc.setLineWidth(0.3);
      doc.roundedRect(MARGIN,y,usableW,9,1,1,"FD");
      doc.setTextColor(92,67,7); doc.setFontSize(6.5); doc.setFont("helvetica","bold");
      doc.text(`Qty Summary (excl. Lumpsum):  Actual Total: ${totA.toLocaleString()}   Work Done: ${totD.toLocaleString()}   Balance: ${totB.toLocaleString()}`,MARGIN+3,y+6);
      y+=13;
    }

    // ── Activities section header
    doc.setFontSize(8.5); doc.setFont("helvetica","bold"); doc.setTextColor(100,116,139);
    doc.text("ACTIVITY PROGRESS DETAILS",MARGIN,y+4);
    doc.setDrawColor(245,158,11); doc.line(MARGIN,y+5.5,MARGIN+56,y+5.5);
    y+=10;

    if(pgItems.length===0){
      doc.setFontSize(8); doc.setTextColor(148,163,184); doc.setFont("helvetica","italic");
      doc.text("No activities recorded for this project.",MARGIN,y+8);
    } else {
      const heads=[[
        "#","Activity","Unit","Actual Qty","Work Done","Balance","Progress %","Status","Pln.Start","Pln.End","Remarks"
      ]];
      const rows=pgItems.map((pg,idx)=>{
        const lbl=(pg.activity==="Other (Custom)"&&pg.customActivity)?pg.customActivity:(pg.activity||pg.customActivity||"—");
        const isL=pg.unit==="Lumpsum";
        return[
          String(idx+1),
          lbl.substring(0,30),
          pg.unit||"NOS",
          isL?"L/S":String(pg.actualQty||0),
          isL?(pg.pct||0)+"%":String(pg.workDoneQty||0),
          isL?(100-(pg.pct||0))+"%":String(pg.balanceQty||0),
          (pg.pct||0)+"%",
          pg.status||"—",
          pg.plannedStart||"—",
          pg.plannedEnd||"—",
          (pg.remarks||"").substring(0,30),
        ];
      });
      doc.autoTable({
        startY:y, margin:{left:MARGIN,right:MARGIN,bottom:16},
        head:heads, body:rows, theme:"grid",
        styles:{fontSize:6.2,cellPadding:2.2,overflow:"linebreak",valign:"middle",textColor:[30,41,59],lineColor:[220,220,220],lineWidth:0.2},
        headStyles:{fillColor:[30,41,59],textColor:[255,255,255],fontStyle:"bold",fontSize:6.5,halign:"center",cellPadding:3},
        alternateRowStyles:{fillColor:[248,250,252]},
        columnStyles:{
          0:{cellWidth:7,halign:"center"},
          1:{cellWidth:36},
          2:{cellWidth:13,halign:"center"},
          3:{cellWidth:15,halign:"center"},
          4:{cellWidth:15,halign:"center"},
          5:{cellWidth:15,halign:"center"},
          6:{cellWidth:16,halign:"center"},
          7:{cellWidth:18,halign:"center"},
          8:{cellWidth:16,halign:"center"},
          9:{cellWidth:16,halign:"center"},
          10:{cellWidth:20},
        },
        didParseCell:(data)=>{
          if(data.section==="body"){
            if(data.column.index===6){
              const p=parseInt(data.cell.text[0])||0;
              data.cell.styles.textColor=p>=100?[16,185,129]:p>=60?[59,130,246]:p>=30?[245,158,11]:[239,68,68];
              data.cell.styles.fontStyle="bold";
            }
            if(data.column.index===7){
              const s=data.cell.text[0];
              data.cell.styles.textColor=s==="Completed"?[16,185,129]:s==="In Progress"?[59,130,246]:s==="On Hold"?[245,158,11]:[239,68,68];
              data.cell.styles.fontStyle="bold";
            }
          }
        },
        didDrawPage:({pageNumber})=>{
          if(pageNumber>1) drawHeader();
          const tot=doc.internal.getNumberOfPages();
          doc.setFontSize(7); doc.setTextColor(160); doc.setFont("helvetica","normal");
          doc.text(`Page ${pageNumber} / ${tot}  ·  Generated: ${now}`,pageW/2,pageH-5,{align:"center"});
        },
      });
    }

    doc.save(`Project_Report_${sel.number}_${today}.pdf`);
  } catch(e){ console.error("Project PDF error:",e); alert("Export failed: "+e.message); }
};

const exportLpoPDF'''

if EXPORT_PDF_END in content:
    content = content.replace(EXPORT_PDF_END, PROJECT_REPORT_FN, 1)
    changes += 1
    print("FIX 5: exportProjectReportPDF added ✅")
else:
    print("WARN FIX 5: exportToPDF end pattern not found")
    # Debug
    idx = content.find('} catch(e) { console.error("PDF export error:"')
    print(f"  exportToPDF catch found at char: {idx}")
    idx2 = content.find('const exportLpoPDF')
    print(f"  exportLpoPDF found at char: {idx2}")

# ── FIX 6: Replace PDF export button in project view with comprehensive report
OLD_PDF_BTN = '''            <button onClick={()=>{
              const pgRows = progressItems.filter(pg=>pg.pid===sel.id);
              const pdfData = pgRows.length>0 ? pgRows.map(pg=>({
                Activity: getActivityLabel(pg)||pg.activity,
                Unit: pg.unit||"NOS",
                Actual_Qty: pg.unit==="Lumpsum"?"L/S":String(pg.actualQty||0),
                Work_Done: pg.unit==="Lumpsum"?(pg.pct||0)+"%":String(pg.workDoneQty||0),
                Balance: pg.unit==="Lumpsum"?(100-(pg.pct||0))+"%":String(pg.balanceQty||0),
                Progress_Pct: (pg.pct||0)+"%",
                Status: pg.status,
              })) : [{Activity:"No activities recorded",Unit:"",Actual_Qty:"",Work_Done:"",Balance:"",Progress_Pct:"0%",Status:""}];
              const pdfCols = [
                {header:"Activity",key:"Activity",pdfWidth:32},
                {header:"Unit",key:"Unit",pdfWidth:12},
                {header:"Actual Qty",key:"Actual_Qty",pdfWidth:16},
                {header:"Work Done",key:"Work_Done",pdfWidth:16},
                {header:"Balance",key:"Balance",pdfWidth:16},
                {header:"Progress %",key:"Progress_Pct",pdfWidth:16},
                {header:"Status",key:"Status",pdfWidth:16},
              ];
              exportToPDF(pdfData, pdfCols, "Project_"+sel.number+"_Progress", sel.number+" — "+sel.name+" | Progress Report | Overall: "+overallPct+"%", "landscape");
            }} className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-lg border bg-red-50 text-red-700 border-red-300 hover:bg-red-100">
              📄 Export PDF
            </button>'''
NEW_PDF_BTN = '''            <button onClick={()=>exportProjectReportPDF(sel, projPgItems, overallPct)} className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-lg border bg-red-50 text-red-700 border-red-300 hover:bg-red-100">
              📄 Full Report PDF
            </button>'''

if OLD_PDF_BTN in content:
    content = content.replace(OLD_PDF_BTN, NEW_PDF_BTN, 1)
    changes += 1
    print("FIX 6: Project PDF button → exportProjectReportPDF ✅")
else:
    print("WARN FIX 6: Old PDF button pattern not found — trying partial match...")
    if 'exportToPDF(pdfData, pdfCols, "Project_"+sel.number' in content:
        # Find the full button block around this string
        idx = content.find('exportToPDF(pdfData, pdfCols, "Project_"+sel.number')
        # Find button start (go back to find onClick)
        start = content.rfind('<button onClick', 0, idx)
        # Find button end
        end_marker = '📄 Export PDF\n            </button>'
        end = content.find(end_marker, idx)
        if start > 0 and end > 0:
            end_pos = end + len(end_marker)
            old_btn = content[start:end_pos]
            content = content[:start] + NEW_PDF_BTN + content[end_pos:]
            changes += 1
            print("FIX 6 (partial match): Project PDF button replaced ✅")

# ── WRITE App.js
with open(APP,"w",encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Saved App.js. Total changes: {changes}")
print("\nRUN:")
print("  set CI=false && npm run build")
print("  git add src/App.js src/r2Storage.js && git commit -m 'fix: R2 storage, photo upload, comprehensive project PDF' && git push")
input("\nPress Enter...")
