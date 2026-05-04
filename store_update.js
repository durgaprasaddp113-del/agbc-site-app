// =============================================================================
// UPDATED useStore() + MaterialStore — Replace both in App.js
// Changes:
//   1. GRN saves immediately update stock (no Approve step)
//   2. GRN list has Edit + Delete buttons
//   3. Fully received LPOs hidden from GRN dropdown
//   4. Deleting a GRN reverses stock automatically
// =============================================================================

function useStore() {
  const [stock,    setStock]    = useState([]);
  const [receipts, setReceipts] = useState([]);
  const [issues,   setIssues]   = useState([]);
  const [loading,  setLoading]  = useState(true);

  const loadAll = useCallback(async () => {
    setLoading(true);
    const [sRes, rRes, iRes] = await Promise.all([
      supabase.from("material_stock").select("*").order("material_name"),
      supabase.from("material_receipts")
        .select("*, material_receipt_items(*)")
        .order("created_at", { ascending: false }),
      supabase.from("material_issues")
        .select("*, material_issue_items(*)")
        .order("created_at", { ascending: false }),
    ]);

    if (sRes.data) setStock(sRes.data.map(s => ({
      id:       s.id,
      code:     s.material_code      || "",
      name:     s.material_name      || "",
      category: s.category           || "",
      unit:     s.unit               || "Nos",
      pid:      s.project_id         || "",
      location: s.store_location     || "",
      opening:  Number(s.opening_stock)         || 0,
      received: Number(s.received_quantity)      || 0,
      issued:   Number(s.issued_quantity)        || 0,
      balance:  Number(s.balance_stock)          || 0,
      minLevel: Number(s.minimum_stock_level)    || 0,
      supplier: s.supplier_name      || "",
      rate:     Number(s.last_purchase_rate)     || 0,
      status:   s.status             || "Available",
      remarks:  s.remarks            || "",
    })));

    if (rRes.data) setReceipts(rRes.data.map(r => ({
      id:           r.id,
      grnNum:       r.grn_number           || "",
      grnStatus:    r.grn_status           || "Approved",
      pid:          r.project_id           || "",
      lpoId:        r.lpo_id               || "",
      lpoReference: r.lpo_reference        || "",
      supplier:     r.supplier_name        || "",
      deliveryNote: r.delivery_note_number || "",
      receivedDate: r.received_date        || "",
      receivedBy:   r.received_by          || "",
      remarks:      r.remarks              || "",
      items: (r.material_receipt_items || []).map(i => ({
        id:          i.id,
        stockId:     i.material_stock_id   || "",
        lpoItemId:   i.lpo_item_id         || "",
        name:        i.material_name       || "",
        unit:        i.unit                || "",
        orderedQty:  Number(i.ordered_quantity)  || 0,
        prevRecQty:  Number(i.prev_received_qty) || 0,
        pendingQty:  Number(i.pending_quantity)  || 0,
        qty:         Number(i.quantity_received) || 0,
        rate:        Number(i.unit_rate)         || 0,
        remarks:     i.remarks             || "",
      })),
    })));

    if (iRes.data) setIssues(iRes.data.map(i => ({
      id:        i.id,
      issueNum:  i.issue_number       || "",
      pid:       i.project_id         || "",
      issuedTo:  i.issued_to          || "",
      dept:      i.department_trade   || "",
      location:  i.location_area      || "",
      issueDate: i.issue_date         || "",
      issuedBy:  i.issued_by          || "",
      purpose:   i.purpose            || "",
      remarks:   i.remarks            || "",
      items: (i.material_issue_items || []).map(it => ({
        id:      it.id,
        stockId: it.material_stock_id  || "",
        name:    it.material_name      || "",
        unit:    it.unit               || "",
        qty:     Number(it.quantity_issued) || 0,
        remarks: it.remarks            || "",
      })),
    })));

    setLoading(false);
  }, []);

  useEffect(() => { loadAll(); }, [loadAll]);

  const computeStatus = (balance, minLevel) => {
    if (balance <= 0)        return "Out of Stock";
    if (balance <= minLevel) return "Low Stock";
    return "Available";
  };

  // ── STOCK CRUD ─────────────────────────────────────────────────────────────
  const addStock = async (f) => {
    const balance = (Number(f.opening)||0) + (Number(f.received)||0) - (Number(f.issued)||0);
    const { error } = await supabase.from("material_stock").insert([{
      material_code:       f.code,
      material_name:       f.name,
      category:            f.category,
      unit:                f.unit,
      project_id:          f.pid || null,
      store_location:      f.location,
      opening_stock:       Number(f.opening)  || 0,
      received_quantity:   Number(f.received) || 0,
      issued_quantity:     Number(f.issued)   || 0,
      balance_stock:       balance,
      minimum_stock_level: Number(f.minLevel) || 0,
      supplier_name:       f.supplier,
      last_purchase_rate:  Number(f.rate)     || 0,
      status:              computeStatus(balance, Number(f.minLevel)||0),
      remarks:             f.remarks,
    }]);
    if (error) return { ok: false, error: error.message };
    await loadAll(); return { ok: true };
  };

  const updateStock = async (id, f) => {
    const balance = (Number(f.opening)||0) + (Number(f.received)||0) - (Number(f.issued)||0);
    const { error } = await supabase.from("material_stock").update({
      material_code:       f.code,
      material_name:       f.name,
      category:            f.category,
      unit:                f.unit,
      project_id:          f.pid || null,
      store_location:      f.location,
      opening_stock:       Number(f.opening)  || 0,
      received_quantity:   Number(f.received) || 0,
      issued_quantity:     Number(f.issued)   || 0,
      balance_stock:       balance,
      minimum_stock_level: Number(f.minLevel) || 0,
      supplier_name:       f.supplier,
      last_purchase_rate:  Number(f.rate)     || 0,
      status:              f.status || computeStatus(balance, Number(f.minLevel)||0),
      remarks:             f.remarks,
    }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadAll(); return { ok: true };
  };

  const removeStock = async (id) => {
    const { error } = await supabase.from("material_stock").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadAll(); return { ok: true };
  };

  // ── GRN number generator ───────────────────────────────────────────────────
  const getNextGRN = async () => {
    const { data } = await supabase
      .from("material_receipts")
      .select("grn_number")
      .order("created_at", { ascending: false })
      .limit(1);
    const last = data?.[0]?.grn_number || "GRN-000";
    const n = parseInt(last.replace("GRN-", "")) || 0;
    return `GRN-${String(n + 1).padStart(3, "0")}`;
  };

  // ── GRN: CREATE — immediately updates stock ────────────────────────────────
  const addReceipt = async (f) => {
    const grnNum = await getNextGRN();

    // Save GRN header (Approved immediately)
    const { data: rData, error } = await supabase
      .from("material_receipts")
      .insert([{
        grn_number:           grnNum,
        grn_status:           "Approved",
        project_id:           f.pid          || null,
        lpo_id:               f.lpoId        || null,
        lpo_reference:        f.lpoReference || null,
        supplier_name:        f.supplier,
        delivery_note_number: f.deliveryNote || null,
        received_date:        f.receivedDate || null,
        received_by:          f.receivedBy   || null,
        remarks:              f.remarks      || null,
      }])
      .select()
      .single();

    if (error) return { ok: false, error: error.message };

    const validItems = (f.items || []).filter(i => Number(i.qty) > 0);

    // Save GRN items
    if (validItems.length > 0) {
      const itemRows = validItems.map(i => ({
        receipt_id:         rData.id,
        lpo_item_id:        i.lpoItemId  || null,
        material_stock_id:  i.stockId    || null,
        material_name:      i.name,
        unit:               i.unit,
        ordered_quantity:   Number(i.orderedQty)  || 0,
        prev_received_qty:  Number(i.prevRecQty)  || 0,
        pending_quantity:   Number(i.pendingQty)  || 0,
        quantity_received:  Number(i.qty),
        unit_rate:          Number(i.rate)        || 0,
        remarks:            i.remarks || "",
      }));
      await supabase.from("material_receipt_items").insert(itemRows);
    }

    // Immediately update stock for each received item
    for (const item of validItems) {
      const qty = Number(item.qty);

      if (item.stockId) {
        // Update existing stock record
        const { data: st } = await supabase
          .from("material_stock")
          .select("received_quantity, balance_stock, minimum_stock_level, last_purchase_rate")
          .eq("id", item.stockId)
          .single();

        if (st) {
          const newRec = (st.received_quantity || 0) + qty;
          const newBal = (st.balance_stock    || 0) + qty;
          await supabase.from("material_stock").update({
            received_quantity:  newRec,
            balance_stock:      newBal,
            last_purchase_rate: Number(item.rate) || st.last_purchase_rate || 0,
            status: computeStatus(newBal, st.minimum_stock_level || 0),
          }).eq("id", item.stockId);
        }
      } else if (item.name) {
        // Auto-create new stock entry
        await supabase.from("material_stock").insert([{
          material_name:       item.name,
          unit:                item.unit    || "Nos",
          project_id:          f.pid        || null,
          supplier_name:       f.supplier   || "",
          opening_stock:       0,
          received_quantity:   qty,
          issued_quantity:     0,
          balance_stock:       qty,
          minimum_stock_level: 0,
          last_purchase_rate:  Number(item.rate) || 0,
          status:              qty > 0 ? "Available" : "Out of Stock",
        }]);
      }

      // Update LPO item received quantity
      if (item.lpoItemId) {
        const { data: li } = await supabase
          .from("lpo_items")
          .select("quantity, received_quantity")
          .eq("id", item.lpoItemId)
          .maybeSingle();

        if (li) {
          const newRecv  = (Number(li.received_quantity) || 0) + qty;
          const ordered  = Number(li.quantity) || 0;
          await supabase.from("lpo_items").update({
            received_quantity: newRecv,
            delivery_status:   newRecv >= ordered ? "Fully Delivered" : "Partially Delivered",
          }).eq("id", item.lpoItemId);
        }
      }
    }

    // Auto-update LPO header delivery status
    if (f.lpoId) {
      const { data: lpoItems } = await supabase
        .from("lpo_items")
        .select("quantity, received_quantity")
        .eq("lpo_id", f.lpoId);

      if (lpoItems && lpoItems.length > 0) {
        const allFull  = lpoItems.every(i => (Number(i.received_quantity)||0) >= Number(i.quantity));
        const anyRecv  = lpoItems.some(i  => (Number(i.received_quantity)||0) > 0);
        const delStatus = allFull ? "Fully Delivered" : anyRecv ? "Partially Delivered" : "Not Delivered";
        await supabase.from("lpo").update({
          delivery_status: delStatus,
          status: allFull ? "Fully Delivered" : "Partially Delivered",
        }).eq("id", f.lpoId);
      }
    }

    await loadAll();
    return { ok: true, grnNum };
  };

  // ── GRN: UPDATE (header details only) ─────────────────────────────────────
  const updateReceipt = async (id, f) => {
    const { error } = await supabase.from("material_receipts").update({
      supplier_name:        f.supplier      || null,
      delivery_note_number: f.deliveryNote  || null,
      received_date:        f.receivedDate  || null,
      received_by:          f.receivedBy    || null,
      remarks:              f.remarks       || null,
    }).eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadAll(); return { ok: true };
  };

  // ── GRN: DELETE — reverses stock automatically ────────────────────────────
  const removeReceipt = async (id) => {
    // Load GRN with items to reverse stock
    const { data: grn } = await supabase
      .from("material_receipts")
      .select("*, material_receipt_items(*)")
      .eq("id", id)
      .single();

    if (grn) {
      for (const item of (grn.material_receipt_items || [])) {
        const qty = Number(item.quantity_received) || 0;
        if (qty <= 0) continue;

        // Reverse stock
        if (item.material_stock_id) {
          const { data: st } = await supabase
            .from("material_stock")
            .select("received_quantity, balance_stock, minimum_stock_level")
            .eq("id", item.material_stock_id)
            .single();
          if (st) {
            const newRec = Math.max(0, (st.received_quantity||0) - qty);
            const newBal = Math.max(0, (st.balance_stock   ||0) - qty);
            await supabase.from("material_stock").update({
              received_quantity: newRec,
              balance_stock:     newBal,
              status: computeStatus(newBal, st.minimum_stock_level || 0),
            }).eq("id", item.material_stock_id);
          }
        }

        // Reverse LPO item received quantity
        if (item.lpo_item_id) {
          const { data: li } = await supabase
            .from("lpo_items")
            .select("quantity, received_quantity")
            .eq("id", item.lpo_item_id)
            .maybeSingle();
          if (li) {
            const newRecv = Math.max(0, (Number(li.received_quantity)||0) - qty);
            await supabase.from("lpo_items").update({
              received_quantity: newRecv,
              delivery_status: newRecv <= 0 ? "Not Delivered"
                : newRecv >= Number(li.quantity) ? "Fully Delivered" : "Partially Delivered",
            }).eq("id", item.lpo_item_id);
          }
        }
      }

      // Reverse LPO header status
      if (grn.lpo_id) {
        const { data: lpoItems } = await supabase
          .from("lpo_items").select("quantity, received_quantity").eq("lpo_id", grn.lpo_id);
        if (lpoItems) {
          const allFull = lpoItems.every(i => (Number(i.received_quantity)||0) >= Number(i.quantity));
          const anyRecv = lpoItems.some(i  => (Number(i.received_quantity)||0) > 0);
          await supabase.from("lpo").update({
            delivery_status: allFull ? "Fully Delivered" : anyRecv ? "Partially Delivered" : "Not Delivered",
            status: allFull ? "Fully Delivered" : anyRecv ? "Partially Delivered" : "Approved",
          }).eq("id", grn.lpo_id);
        }
      }
    }

    await supabase.from("material_receipt_items").delete().eq("receipt_id", id);
    const { error } = await supabase.from("material_receipts").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadAll(); return { ok: true };
  };

  // ── ISSUES ─────────────────────────────────────────────────────────────────
  const getNextIssueNum = async () => {
    const { data } = await supabase
      .from("material_issues")
      .select("issue_number")
      .order("created_at", { ascending: false })
      .limit(1);
    const last = data?.[0]?.issue_number || "ISS-000";
    const n = parseInt(last.replace("ISS-", "")) || 0;
    return `ISS-${String(n + 1).padStart(3, "0")}`;
  };

  const addIssue = async (f) => {
    for (const it of (f.items || []).filter(i => i.stockId && Number(i.qty) > 0)) {
      const { data: st } = await supabase
        .from("material_stock")
        .select("balance_stock, material_name")
        .eq("id", it.stockId)
        .single();
      if (!st || (st.balance_stock || 0) < Number(it.qty)) {
        return { ok: false, error: `Insufficient stock for "${st?.material_name || it.name}". Available: ${st?.balance_stock || 0}` };
      }
    }

    const issueNum = await getNextIssueNum();
    const { data: iData, error } = await supabase
      .from("material_issues")
      .insert([{
        issue_number:     issueNum,
        project_id:       f.pid      || null,
        issued_to:        f.issuedTo,
        department_trade: f.dept,
        location_area:    f.location,
        issue_date:       f.issueDate || null,
        issued_by:        f.issuedBy,
        purpose:          f.purpose,
        remarks:          f.remarks,
      }])
      .select()
      .single();

    if (error) return { ok: false, error: error.message };

    for (const it of (f.items || []).filter(i => i.stockId && Number(i.qty) > 0)) {
      await supabase.from("material_issue_items").insert([{
        issue_id:          iData.id,
        material_stock_id: it.stockId,
        material_name:     it.name,
        unit:              it.unit,
        quantity_issued:   Number(it.qty),
        remarks:           it.remarks || "",
      }]);

      const { data: st } = await supabase
        .from("material_stock")
        .select("issued_quantity, balance_stock, minimum_stock_level")
        .eq("id", it.stockId)
        .single();

      if (st) {
        const newIss = (st.issued_quantity || 0) + Number(it.qty);
        const newBal = Math.max(0, (st.balance_stock || 0) - Number(it.qty));
        await supabase.from("material_stock").update({
          issued_quantity: newIss,
          balance_stock:   newBal,
          status: computeStatus(newBal, st.minimum_stock_level || 0),
        }).eq("id", it.stockId);
      }
    }

    await loadAll();
    return { ok: true, issueNum };
  };

  const removeIssue = async (id) => {
    await supabase.from("material_issue_items").delete().eq("issue_id", id);
    const { error } = await supabase.from("material_issues").delete().eq("id", id);
    if (error) return { ok: false, error: error.message };
    await loadAll(); return { ok: true };
  };

  return {
    stock, receipts, issues, loading,
    addStock, updateStock, removeStock,
    addReceipt, updateReceipt, removeReceipt,
    addIssue, removeIssue,
    reload: loadAll,
  };
}


// =============================================================================
// MaterialStore COMPONENT — Replace in App.js
// =============================================================================
const MaterialStore = ({
  stock, receipts, issues, loading,
  onAddStock, onUpdateStock, onRemoveStock,
  onAddReceipt, onUpdateReceipt, onRemoveReceipt,
  onAddIssue, onRemoveIssue,
  projects, lpos, showToast, navFilter = {},
}) => {
  const [tab,       setTab]       = useState("stock");
  const [mode,      setMode]      = useState("list");
  const [sel,       setSel]       = useState(null);
  const [form,      setForm]      = useState(EMPTY_STOCK_FORM());
  const [search,    setSearch]    = useState("");
  const [fProject,  setFProject]  = useState("All");
  const [fCat,      setFCat]      = useState("All");
  const [fStatus,   setFStatus]   = useState("All");
  const [fLowOnly,  setFLowOnly]  = useState(false);
  const [saving,    setSaving]    = useState(false);
  const [confirmId, setConfirmId] = useState(null);
  const [selLpoId,  setSelLpoId]  = useState("");
  const [lpoItems,  setLpoItems]  = useState([]);
  const [loadingLpo,setLoadingLpo]= useState(false);
  const [grnEdit,   setGrnEdit]   = useState(false);

  useEffect(() => {
    if (navFilter.status === "Low Stock") { setFLowOnly(true); setFStatus("Low Stock"); }
    else if (navFilter.status) setFStatus(navFilter.status);
    if (navFilter.projectId) setFProject(navFilter.projectId);
  }, [navFilter]);

  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }));

  const loadLpoItems = async (lpoId) => {
    if (!lpoId) { setLpoItems([]); return; }
    setLoadingLpo(true);
    const { data } = await supabase.from("lpo_items").select("*").eq("lpo_id", lpoId);
    if (data) {
      setLpoItems(
        data
          .filter(i => ((Number(i.quantity)||0) - (Number(i.received_quantity)||0)) > 0)
          .map(i => ({
            lpoItemId:  i.id,
            name:       i.item_description || "",
            unit:       i.unit || "Nos",
            orderedQty: Number(i.quantity)           || 0,
            prevRecQty: Number(i.received_quantity)  || 0,
            pendingQty: (Number(i.quantity)||0) - (Number(i.received_quantity)||0),
            rate:       Number(i.rate) || 0,
            qty: 0, stockId: "", remarks: "",
          }))
      );
    }
    setLoadingLpo(false);
  };

  const setGrnItem = (idx, k, v) =>
    setLpoItems(p => p.map((i, n) => n === idx ? { ...i, [k]: v } : i));

  // Only LPOs with pending items
  const availableLpos = lpos.filter(l => {
    if (!["Approved","Sent to Supplier","Partially Delivered"].includes(l.status)) return false;
    return l.items.some(i => ((Number(i.qty)||0) - (Number(i.deliveredQty)||0)) > 0);
  });

  const filteredStock = stock.filter(s => {
    if (fProject !== "All" && s.pid !== fProject) return false;
    if (fCat     !== "All" && s.category !== fCat) return false;
    if (fStatus  !== "All" && s.status !== fStatus) return false;
    if (fLowOnly && s.status !== "Low Stock") return false;
    if (search && !`${s.code} ${s.name} ${s.supplier}`.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const goList = () => {
    setMode("list"); setSel(null); setSelLpoId(""); setLpoItems([]);
    setGrnEdit(false); setForm(EMPTY_STOCK_FORM());
  };

  // ── Handlers ───────────────────────────────────────────────────────────────
  const handleSaveStock = async () => {
    if (!form.name.trim()) { showToast("Material name required", "error"); return; }
    setSaving(true);
    const res = sel ? await onUpdateStock(sel.id, form) : await onAddStock(form);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Failed", "error"); return; }
    showToast(sel ? "Stock updated!" : "Stock item created!"); goList();
  };

  const handleSaveGRN = async () => {
    if (!selLpoId) { showToast("Select an LPO", "error"); return; }
    if (!lpoItems.some(i => Number(i.qty) > 0)) { showToast("Enter at least one received quantity", "error"); return; }
    for (const it of lpoItems) {
      if (Number(it.qty) > Number(it.pendingQty)) {
        showToast(`"${it.name}": Received (${it.qty}) > Pending (${it.pendingQty})`, "error"); return;
      }
    }
    const lpo = lpos.find(l => l.id === selLpoId);
    setSaving(true);
    const res = await onAddReceipt({
      pid: lpo?.pid || "", lpoId: selLpoId, lpoReference: lpo?.lpoNum || "",
      supplier: form.supplier || lpo?.supplierName || "",
      deliveryNote: form.deliveryNote || "",
      receivedDate: form.receivedDate || new Date().toISOString().split("T")[0],
      receivedBy: form.receivedBy || "", remarks: form.remarks || "",
      items: lpoItems.filter(i => Number(i.qty) > 0),
    });
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Failed", "error"); return; }
    showToast(`✅ ${res.grnNum} saved — stock updated!`); goList();
  };

  const handleEditGRN = async () => {
    setSaving(true);
    const res = await onUpdateReceipt(sel.id, form);
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Failed", "error"); return; }
    showToast("GRN updated!"); goList();
  };

  const handleSaveIssue = async () => {
    if (!form.issuedTo?.trim()) { showToast("Issued To required", "error"); return; }
    const items = (form.items || []).filter(i => i.stockId && Number(i.qty) > 0);
    if (!items.length) { showToast("Add at least one item with quantity", "error"); return; }
    setSaving(true);
    const res = await onAddIssue({ ...form, items });
    setSaving(false);
    if (!res.ok) { showToast(res.error || "Failed", "error"); return; }
    showToast("Materials issued: " + res.issueNum); goList();
  };

  const handleDelete = async (type, id) => {
    setSaving(true);
    const res = type === "stock"   ? await onRemoveStock(id)
              : type === "receipt" ? await onRemoveReceipt(id)
              :                      await onRemoveIssue(id);
    setSaving(false);
    if (!res.ok) { showToast(res.error, "error"); return; }
    showToast(type === "receipt" ? "GRN deleted — stock reversed!" : "Deleted!");
    setConfirmId(null);
  };

  const addIssueItem    = () => setForm(p => ({ ...p, items: [...(p.items||[]), EMPTY_STOCK_ITEM()] }));
  const removeIssueItem = id => setForm(p => ({ ...p, items: p.items.filter(i => i.id !== id) }));
  const setIssueItem    = (id, k, v) => setForm(p => ({ ...p, items: p.items.map(i => i.id===id ? {...i,[k]:v} : i) }));
  const setIssueStock   = (id, stockId) => {
    const st = stock.find(s => s.id === stockId);
    setForm(p => ({ ...p, items: p.items.map(i => i.id===id ? {...i, stockId, name: st?.name||"", unit: st?.unit||"Nos"} : i) }));
  };

  const now2 = new Date(); now2.setDate(1); now2.setHours(0,0,0,0);
  const recThisMonth = receipts.filter(r => r.receivedDate && new Date(r.receivedDate) >= now2)
    .reduce((s,r) => s + r.items.reduce((a,i) => a + i.qty, 0), 0);
  const issThisMonth = issues.filter(i => i.issueDate && new Date(i.issueDate) >= now2)
    .reduce((s,i) => s + i.items.reduce((a,it) => a + it.qty, 0), 0);

  const TABS = [
    { id:"stock",    label:"📦 Stock Register",          count: stock.length    },
    { id:"receipts", label:"📥 Material Receipts (GRN)",  count: receipts.length },
    { id:"issues",   label:"📤 Material Issues",          count: issues.length   },
  ];

  // ── GRN NEW FORM ───────────────────────────────────────────────────────────
  if (tab === "receipts" && mode === "form" && !grnEdit) return (
    <div className="p-6 max-w-4xl">
      <BackBtn onClick={goList}/>
      <h2 className="text-xl font-bold text-slate-800 mb-4">New Material Receipt (GRN)</h2>

      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-4">
        <div className="text-xs font-bold text-blue-700 uppercase tracking-wide mb-2">Step 1 — Select LPO</div>
        <Sel value={selLpoId} onChange={e => {
          setSelLpoId(e.target.value);
          const lpo = lpos.find(l => l.id === e.target.value);
          if (lpo) setForm(p => ({ ...p, supplier: lpo.supplierName }));
          loadLpoItems(e.target.value);
        }}>
          <option value="">Select LPO with pending items...</option>
          {availableLpos.map(l => {
            const proj    = projects.find(p => p.id === l.pid);
            const pending = l.items.reduce((s,i) => s + Math.max(0,(Number(i.qty)||0)-(Number(i.deliveredQty)||0)), 0);
            return (
              <option key={l.id} value={l.id}>
                {l.lpoNum} — {l.supplierName} ({proj?.number||"—"}) · {pending} units pending
              </option>
            );
          })}
        </Sel>
        {availableLpos.length === 0 && (
          <p className="text-xs text-amber-700 mt-2">⚠️ No LPOs with pending items. All are fully received or none approved.</p>
        )}
      </div>

      {selLpoId && (() => {
        const lpo  = lpos.find(l => l.id === selLpoId);
        const proj = projects.find(p => p.id === lpo?.pid);
        return (
          <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div><div className="text-xs text-slate-400">LPO No.</div><div className="font-bold text-green-700">{lpo?.lpoNum}</div></div>
            <div><div className="text-xs text-slate-400">Supplier</div><div className="font-semibold text-slate-800">{lpo?.supplierName}</div></div>
            <div><div className="text-xs text-slate-400">Project</div><div className="font-semibold text-slate-800">{proj?.number}</div></div>
            <div><div className="text-xs text-slate-400">Status</div><Badge text={lpo?.status}/></div>
          </div>
        );
      })()}

      {selLpoId && (
        <div className="bg-white rounded-xl border border-slate-200 overflow-visible mb-4">
          <div className="px-4 py-3 bg-slate-50 border-b border-slate-200 flex items-center gap-2">
            <span className="font-semibold text-slate-700 text-sm">Step 2 — Enter Received Quantities</span>
            {loadingLpo && <span className="text-xs text-amber-600 animate-pulse">Loading...</span>}
            {!loadingLpo && lpoItems.length === 0 && <span className="text-xs text-red-600">⚠️ No pending items</span>}
          </div>
          {lpoItems.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm min-w-[800px]">
                <thead className="bg-slate-50">
                  <tr>{["#","Item","Unit","Ordered","Prev Rec","Pending","Received Now*","Rate AED","Link to Stock","Remarks"].map(h=>(
                    <th key={h} className="text-left px-3 py-2 text-xs font-bold text-slate-500 whitespace-nowrap">{h}</th>
                  ))}</tr>
                </thead>
                <tbody>
                  {lpoItems.map((it, idx) => (
                    <tr key={idx} className="border-t border-slate-100">
                      <td className="px-3 py-2 text-xs text-slate-400">{idx+1}</td>
                      <td className="px-3 py-2 font-medium text-slate-800">{it.name}</td>
                      <td className="px-3 py-2 text-xs">{it.unit}</td>
                      <td className="px-3 py-2 text-xs text-center font-bold">{it.orderedQty}</td>
                      <td className="px-3 py-2 text-xs text-center text-amber-600 font-semibold">{it.prevRecQty}</td>
                      <td className="px-3 py-2 text-xs text-center text-blue-700 font-bold">{it.pendingQty}</td>
                      <td className="px-2 py-1 w-24">
                        <Inp type="number" value={it.qty||""} placeholder="0"
                          className={it.qty > it.pendingQty ? "border-red-400" : ""}
                          onChange={e => setGrnItem(idx, "qty", Math.min(Number(e.target.value), it.pendingQty))}/>
                      </td>
                      <td className="px-3 py-2 text-xs">AED {it.rate}</td>
                      <td className="px-2 py-1 min-w-[150px]">
                        <Sel value={it.stockId} onChange={e => setGrnItem(idx, "stockId", e.target.value)} className="text-xs">
                          <option value="">Auto-create / link...</option>
                          {stock.map(s => (
                            <option key={s.id} value={s.id}>{s.code?`[${s.code}] `:""}{s.name} (bal:{s.balance})</option>
                          ))}
                        </Sel>
                      </td>
                      <td className="px-2 py-1">
                        <Inp value={it.remarks} onChange={e => setGrnItem(idx, "remarks", e.target.value)} placeholder="Notes"/>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {selLpoId && (
        <FormCard>
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Step 3 — Delivery Details</div>
          <Grid2>
            <div><Lbl t="Supplier"/><Inp value={form.supplier||""} onChange={set("supplier")}/></div>
            <div><Lbl t="Delivery Note No."/><Inp value={form.deliveryNote||""} onChange={set("deliveryNote")} placeholder="DN-XXXX"/></div>
            <div><Lbl t="Received Date"/><Inp type="date" value={form.receivedDate||""} onChange={set("receivedDate")}/></div>
            <div><Lbl t="Received By"/><Inp value={form.receivedBy||""} onChange={set("receivedBy")} placeholder="Store keeper"/></div>
          </Grid2>
          <div><Lbl t="Remarks"/><Txta value={form.remarks||""} onChange={set("remarks")} rows={2}/></div>
          <div className="bg-green-50 border border-green-200 rounded-xl p-3 text-xs text-green-800 font-semibold mt-2">
            ✅ Stock Register updates <strong>immediately</strong> when GRN is saved.
          </div>
        </FormCard>
      )}

      <div className="flex gap-3 mt-4">
        <Btn saving={saving} onClick={handleSaveGRN} label="💾 Save GRN & Update Stock"/>
        <Btn onClick={goList} label="Cancel" color="slate"/>
      </div>
    </div>
  );

  // ── GRN EDIT FORM ──────────────────────────────────────────────────────────
  if (tab === "receipts" && mode === "form" && grnEdit) return (
    <div className="p-6 max-w-2xl">
      <BackBtn onClick={goList}/>
      <h2 className="text-xl font-bold text-slate-800 mb-4">Edit GRN — {sel?.grnNum}</h2>
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-800 mb-4">
        ℹ️ Only delivery details (DN number, date, remarks) can be edited here. To change received quantities, delete this GRN and create a new one.
      </div>
      <FormCard>
        <Grid2>
          <div><Lbl t="Supplier Name"/><Inp value={form.supplier||""} onChange={set("supplier")}/></div>
          <div><Lbl t="Delivery Note No."/><Inp value={form.deliveryNote||""} onChange={set("deliveryNote")}/></div>
          <div><Lbl t="Received Date"/><Inp type="date" value={form.receivedDate||""} onChange={set("receivedDate")}/></div>
          <div><Lbl t="Received By"/><Inp value={form.receivedBy||""} onChange={set("receivedBy")}/></div>
        </Grid2>
        <div><Lbl t="Remarks"/><Txta value={form.remarks||""} onChange={set("remarks")} rows={2}/></div>
        <div className="flex gap-3 pt-2">
          <Btn saving={saving} onClick={handleEditGRN} label="Update GRN"/>
          <Btn onClick={goList} label="Cancel" color="slate"/>
        </div>
      </FormCard>
    </div>
  );

  // ── ISSUE FORM ─────────────────────────────────────────────────────────────
  if (tab === "issues" && mode === "form") return (
    <div className="p-6 max-w-3xl">
      <BackBtn onClick={goList}/>
      <h2 className="text-xl font-bold text-slate-800 mb-4">New Material Issue</h2>
      <div className="space-y-4">
        <FormCard>
          <Grid2>
            <div><Lbl t="Project"/><Sel value={form.pid||""} onChange={set("pid")}><option value="">All Projects</option>{projects.map(p=><option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}</Sel></div>
            <div><Lbl t="Issue Date"/><Inp type="date" value={form.issueDate||""} onChange={set("issueDate")}/></div>
            <div><Lbl t="Issued To" req/><Inp value={form.issuedTo||""} onChange={set("issuedTo")} placeholder="Name / Subcontractor"/></div>
            <div><Lbl t="Department"/><Sel value={form.dept||"Civil"} onChange={set("dept")}>{DEPT_LIST.map(d=><option key={d}>{d}</option>)}</Sel></div>
            <div><Lbl t="Location"/><Inp value={form.location||""} onChange={set("location")} placeholder="Floor 3, Grid A"/></div>
            <div><Lbl t="Issued By"/><Inp value={form.issuedBy||""} onChange={set("issuedBy")} placeholder="Store keeper"/></div>
          </Grid2>
          <div><Lbl t="Purpose"/><Txta value={form.purpose||""} onChange={set("purpose")} rows={2}/></div>
        </FormCard>
        <div className="bg-white rounded-xl border border-slate-200 overflow-visible">
          <div className="flex items-center justify-between px-4 py-3 bg-slate-50 border-b border-slate-100">
            <span className="font-semibold text-slate-700 text-sm">Items to Issue</span>
            <button onClick={addIssueItem} className="text-xs font-bold text-amber-600 border border-amber-300 px-2.5 py-1 rounded-lg">+ Add Item</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm min-w-[600px]">
              <thead className="bg-slate-50"><tr>{["#","Material*","Available","Qty*","Remarks",""].map(h=><th key={h} className="text-left px-3 py-2 text-xs font-bold text-slate-500">{h}</th>)}</tr></thead>
              <tbody>
                {(form.items||[]).map((it,idx)=>{
                  const st   = stock.find(s => s.id === it.stockId);
                  const over = it.qty && st && Number(it.qty) > st.balance;
                  return (
                    <tr key={it.id} className="border-t border-slate-100">
                      <td className="px-3 py-1 text-xs text-slate-400 w-8">{idx+1}</td>
                      <td className="px-2 py-1">
                        <Sel value={it.stockId} onChange={e=>setIssueStock(it.id,e.target.value)}>
                          <option value="">Select material...</option>
                          {stock.filter(s=>s.balance>0).map(s=><option key={s.id} value={s.id}>{s.code?`[${s.code}] `:""}{s.name} (bal:{s.balance} {s.unit})</option>)}
                        </Sel>
                      </td>
                      <td className="px-2 py-1 w-20">
                        {st && <span className={`text-xs font-bold ${st.balance<=0?"text-red-600":st.balance<=st.minLevel?"text-amber-600":"text-green-600"}`}>{st.balance} {st.unit}</span>}
                      </td>
                      <td className="px-2 py-1 w-24">
                        <Inp type="number" value={it.qty} onChange={e=>setIssueItem(it.id,"qty",e.target.value)} placeholder="0" className={over?"border-red-400":""}/>
                        {over && <div className="text-red-500 text-xs mt-0.5">Exceeds stock!</div>}
                      </td>
                      <td className="px-2 py-1"><Inp value={it.remarks} onChange={e=>setIssueItem(it.id,"remarks",e.target.value)} placeholder="Notes"/></td>
                      <td className="px-2 py-1 w-8"><button onClick={()=>removeIssueItem(it.id)} disabled={(form.items||[]).length===1} className="text-red-400 hover:text-red-600 text-lg disabled:opacity-30">×</button></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
        <div className="flex gap-3">
          <Btn saving={saving} onClick={handleSaveIssue} label="Issue Materials"/>
          <Btn onClick={goList} label="Cancel" color="slate"/>
        </div>
      </div>
    </div>
  );

  // ── STOCK FORM ─────────────────────────────────────────────────────────────
  if (tab === "stock" && mode === "form") return (
    <div className="p-6 max-w-2xl">
      <BackBtn onClick={goList}/>
      <h2 className="text-xl font-bold text-slate-800 mb-4">{sel?"Edit Stock Item":"New Stock Item"}</h2>
      <FormCard>
        <Grid2>
          <div><Lbl t="Material Code"/><Inp value={form.code||""} onChange={set("code")} placeholder="CEM-001"/></div>
          <div><Lbl t="Material Name" req/><Inp value={form.name||""} onChange={set("name")} placeholder="OPC Cement 50kg"/></div>
          <div><Lbl t="Category"/><Sel value={form.category||"Cement & Concrete"} onChange={set("category")}>{STOCK_CATS.map(c=><option key={c}>{c}</option>)}</Sel></div>
          <div><Lbl t="Unit"/><Sel value={form.unit||"Nos"} onChange={set("unit")}>{UNITS.map(u=><option key={u}>{u}</option>)}</Sel></div>
          <div><Lbl t="Project"/><Sel value={form.pid||""} onChange={set("pid")}><option value="">All Projects</option>{projects.map(p=><option key={p.id} value={p.id}>{p.number} — {p.name}</option>)}</Sel></div>
          <div><Lbl t="Store Location"/><Inp value={form.location||""} onChange={set("location")} placeholder="Site Store A"/></div>
          <div><Lbl t="Opening Stock"/><Inp type="number" value={form.opening||"0"} onChange={set("opening")}/></div>
          <div><Lbl t="Minimum Stock Level"/><Inp type="number" value={form.minLevel||"0"} onChange={set("minLevel")}/></div>
          <div><Lbl t="Supplier"/><Inp value={form.supplier||""} onChange={set("supplier")}/></div>
          <div><Lbl t="Rate (AED)"/><Inp type="number" value={form.rate||""} onChange={set("rate")}/></div>
        </Grid2>
        {sel && <div><Lbl t="Status"/><Sel value={form.status||"Available"} onChange={set("status")}>{STOCK_STATUS.map(s=><option key={s}>{s}</option>)}</Sel></div>}
        <div><Lbl t="Remarks"/><Txta value={form.remarks||""} onChange={set("remarks")} rows={2}/></div>
        <div className="flex gap-3 pt-2">
          <Btn saving={saving} onClick={handleSaveStock} label={sel?"Update":"Add to Stock"}/>
          <Btn onClick={goList} label="Cancel" color="slate"/>
        </div>
      </FormCard>
    </div>
  );

  // ── MAIN LIST ──────────────────────────────────────────────────────────────
  return (
    <div className="p-6">
      {confirmId && <ConfirmDialog
        message={confirmId.type === "receipt"
          ? "⚠️ Delete this GRN? Stock quantities received will be reversed automatically."
          : "Delete this record permanently?"}
        onConfirm={() => handleDelete(confirmId.type, confirmId.id)}
        onCancel={() => setConfirmId(null)}/>}

      {/* KPI */}
      <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-5 gap-2 sm:gap-3 mb-4">
        {[
          {l:"Total Materials",   v:stock.length,                                    c:"bg-blue-500"},
          {l:"Low Stock",         v:stock.filter(s=>s.status==="Low Stock").length,   c:"bg-amber-500"},
          {l:"Out of Stock",      v:stock.filter(s=>s.status==="Out of Stock").length,c:"bg-red-500"},
          {l:"Received (Month)",  v:recThisMonth,                                    c:"bg-green-500"},
          {l:"Issued (Month)",    v:issThisMonth,                                    c:"bg-indigo-500"},
        ].map(c=>(
          <div key={c.l} className={`${c.c} rounded-xl p-3 text-white`}>
            <div className="text-2xl font-bold">{c.v}</div>
            <div className="text-xs opacity-80 mt-0.5">{c.l}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-4 bg-slate-100 p-1 rounded-xl w-fit flex-wrap">
        {TABS.map(t=>(
          <button key={t.id} onClick={()=>{setTab(t.id);setMode("list");setSel(null);}}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${tab===t.id?"bg-white text-slate-800 shadow-sm":"text-slate-500 hover:text-slate-700"}`}>
            {t.label} <span className="text-xs opacity-60">({t.count})</span>
          </button>
        ))}
      </div>

      {/* ── STOCK TAB ── */}
      {tab === "stock" && (
        <>
          <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
            <div className="flex flex-wrap gap-2">
              <SearchBar value={search} onChange={e=>setSearch(e.target.value)} placeholder="Code, name, supplier..."/>
              <Sel value={fProject} onChange={e=>setFProject(e.target.value)} className="w-auto"><option value="All">All Projects</option>{projects.map(p=><option key={p.id} value={p.id}>{p.number}</option>)}</Sel>
              <Sel value={fCat}     onChange={e=>setFCat(e.target.value)}     className="w-auto"><option value="All">All Categories</option>{STOCK_CATS.map(c=><option key={c}>{c}</option>)}</Sel>
              <Sel value={fStatus}  onChange={e=>setFStatus(e.target.value)}  className="w-auto"><option value="All">All Status</option>{STOCK_STATUS.map(s=><option key={s}>{s}</option>)}</Sel>
              <label className="flex items-center gap-1.5 text-xs font-semibold text-amber-700 cursor-pointer">
                <input type="checkbox" checked={fLowOnly} onChange={e=>setFLowOnly(e.target.checked)} className="rounded"/>
                Low Stock Only
              </label>
            </div>
            <AddBtn onClick={()=>{setForm(EMPTY_STOCK_FORM());setSel(null);setMode("form");}} label="Add Material"/>
          </div>
          {loading?<Spinner/>:filteredStock.length===0?<EmptyState msg="No stock items found" onCreate={()=>{setForm(EMPTY_STOCK_FORM());setSel(null);setMode("form");}}/>:(
            <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto shadow-sm">
              <table className="w-full text-sm min-w-[1000px]">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>{["Code","Name","Category","Unit","Opening","Received","Issued","Balance","Min Lvl","Rate AED","Status","Actions"].map(h=>(
                    <th key={h} className="text-left px-3 py-3 text-xs font-bold text-slate-500 uppercase whitespace-nowrap">{h}</th>
                  ))}</tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredStock.map(s=>(
                    <tr key={s.id} className={`hover:bg-slate-50 ${s.status==="Out of Stock"?"bg-red-50/30":s.status==="Low Stock"?"bg-amber-50/30":""}`}>
                      <td className="px-3 py-2.5 font-mono text-xs text-slate-600">{s.code||"—"}</td>
                      <td className="px-3 py-2.5 font-semibold text-slate-800 max-w-[160px] truncate">{s.name}</td>
                      <td className="px-3 py-2.5 text-xs text-slate-600">{s.category}</td>
                      <td className="px-3 py-2.5 text-xs">{s.unit}</td>
                      <td className="px-3 py-2.5 text-xs text-center">{s.opening}</td>
                      <td className="px-3 py-2.5 text-xs text-center text-green-700 font-semibold">{s.received}</td>
                      <td className="px-3 py-2.5 text-xs text-center text-red-600 font-semibold">{s.issued}</td>
                      <td className="px-3 py-2.5 text-center">
                        <span className={`text-sm font-bold ${s.balance<=0?"text-red-700":s.balance<=s.minLevel?"text-amber-600":"text-slate-800"}`}>{s.balance}</span>
                      </td>
                      <td className="px-3 py-2.5 text-xs text-center text-slate-500">{s.minLevel}</td>
                      <td className="px-3 py-2.5 text-xs text-slate-600">AED {s.rate||0}</td>
                      <td className="px-3 py-2.5">
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${ST_BADGE[s.status]||ST_BADGE.Inactive}`}>{s.status}</span>
                      </td>
                      <td className="px-3 py-2.5">
                        <div className="flex gap-1 flex-wrap">
                          <ActBtn onClick={()=>{setSel(s);setForm({code:s.code,name:s.name,category:s.category,unit:s.unit,pid:s.pid,location:s.location,opening:String(s.opening),received:String(s.received),issued:String(s.issued),minLevel:String(s.minLevel),supplier:s.supplier,rate:String(s.rate),status:s.status,remarks:s.remarks});setMode("form");}} label="Edit" color="edit"/>
                          <ActBtn onClick={()=>setConfirmId({type:"stock",id:s.id})} label="Del" color="del"/>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* ── RECEIPTS TAB ── */}
      {tab === "receipts" && (
        <>
          <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
            <SearchBar value={search} onChange={e=>setSearch(e.target.value)} placeholder="GRN no, LPO, supplier..."/>
            <AddBtn onClick={()=>{setForm({supplier:"",deliveryNote:"",receivedDate:new Date().toISOString().split("T")[0],receivedBy:"",remarks:""});setSel(null);setSelLpoId("");setLpoItems([]);setGrnEdit(false);setMode("form");}} label="New GRN"/>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-3 mb-3 text-xs text-green-800 font-semibold">
            ✅ Stock updates immediately on GRN save · ⚠️ Deleting a GRN reverses stock automatically
          </div>
          {loading?<Spinner/>:receipts.length===0?<EmptyState msg="No GRNs yet" onCreate={()=>{setForm({supplier:"",deliveryNote:"",receivedDate:new Date().toISOString().split("T")[0],receivedBy:"",remarks:""});setSel(null);setSelLpoId("");setLpoItems([]);setGrnEdit(false);setMode("form");}}/>:(
            <div className="space-y-3">
              {receipts
                .filter(r=>!search||`${r.grnNum} ${r.supplier} ${r.lpoReference}`.toLowerCase().includes(search.toLowerCase()))
                .map(r=>{
                  const proj = projects.find(p=>p.id===r.pid);
                  return (
                    <div key={r.id} className="bg-white rounded-xl border border-green-200 shadow-sm p-4">
                      <div className="flex items-start justify-between gap-3 mb-3">
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-mono text-sm font-bold text-green-700">{r.grnNum}</span>
                            <span className="text-xs font-bold px-2 py-0.5 rounded-full border bg-green-100 text-green-700 border-green-200">✅ Stock Updated</span>
                            {r.lpoReference && <span className="text-xs font-bold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded-full">LPO: {r.lpoReference}</span>}
                          </div>
                          <div className="text-sm font-semibold text-slate-800 mt-1">{r.supplier}</div>
                          <div className="text-xs text-slate-500 mt-0.5">
                            {proj?.number} · DN: {r.deliveryNote||"—"} · {fmtDate(r.receivedDate)} · By: {r.receivedBy||"—"}
                          </div>
                        </div>
                        <div className="flex gap-2 shrink-0">
                          <ActBtn onClick={()=>{
                            setSel(r);
                            setForm({supplier:r.supplier,deliveryNote:r.deliveryNote,receivedDate:r.receivedDate,receivedBy:r.receivedBy,remarks:r.remarks});
                            setGrnEdit(true); setMode("form");
                          }} label="Edit" color="edit"/>
                          <ActBtn onClick={()=>setConfirmId({type:"receipt",id:r.id})} label="Del" color="del"/>
                        </div>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="w-full text-xs min-w-[500px]">
                          <thead className="bg-slate-50">
                            <tr>{["Item","Unit","Ordered","Prev Rec","Received","Rate AED"].map(h=>(
                              <th key={h} className="text-left px-3 py-1.5 font-bold text-slate-500">{h}</th>
                            ))}</tr>
                          </thead>
                          <tbody>
                            {r.items.map((it,i)=>(
                              <tr key={i} className="border-t border-slate-100">
                                <td className="px-3 py-1.5 font-medium text-slate-700">{it.name}</td>
                                <td className="px-3 py-1.5 text-slate-500">{it.unit}</td>
                                <td className="px-3 py-1.5 text-center">{it.orderedQty||"—"}</td>
                                <td className="px-3 py-1.5 text-center text-amber-600">{it.prevRecQty||"—"}</td>
                                <td className="px-3 py-1.5 text-center text-green-700 font-bold">{it.qty}</td>
                                <td className="px-3 py-1.5 text-slate-500">AED {it.rate||0}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  );
                })}
            </div>
          )}
        </>
      )}

      {/* ── ISSUES TAB ── */}
      {tab === "issues" && (
        <>
          <div className="flex items-center justify-between mb-3">
            <SearchBar value={search} onChange={e=>setSearch(e.target.value)} placeholder="Issue no, issued to..."/>
            <AddBtn onClick={()=>{setForm({...EMPTY_ISS_FORM(),items:[EMPTY_STOCK_ITEM()]});setSel(null);setMode("form");}} label="Issue Material"/>
          </div>
          {loading?<Spinner/>:issues.length===0?<EmptyState msg="No issues yet" onCreate={()=>{setForm({...EMPTY_ISS_FORM(),items:[EMPTY_STOCK_ITEM()]});setSel(null);setMode("form");}}/>:(
            <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto shadow-sm">
              <table className="w-full text-sm min-w-[800px]">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>{["Issue No.","Project","Issued To","Dept","Date","Items","Actions"].map(h=><th key={h} className="text-left px-4 py-3 text-xs font-bold text-slate-500 uppercase">{h}</th>)}</tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {issues
                    .filter(i=>!search||`${i.issueNum} ${i.issuedTo}`.toLowerCase().includes(search.toLowerCase()))
                    .map(i=>{
                      const proj = projects.find(p=>p.id===i.pid);
                      return (
                        <tr key={i.id} className="hover:bg-slate-50">
                          <td className="px-4 py-3 font-mono text-xs font-bold text-orange-700">{i.issueNum}</td>
                          <td className="px-4 py-3 text-xs font-bold">{proj?.number||"—"}</td>
                          <td className="px-4 py-3 font-medium">{i.issuedTo}</td>
                          <td className="px-4 py-3 text-xs"><span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-semibold">{i.dept}</span></td>
                          <td className="px-4 py-3 text-xs whitespace-nowrap">{fmtDate(i.issueDate)}</td>
                          <td className="px-4 py-3">
                            {i.items.map((it,idx)=>(
                              <div key={idx} className="text-xs text-slate-600"><span className="font-semibold">{it.name}</span>: {it.qty} {it.unit}</div>
                            ))}
                          </td>
                          <td className="px-4 py-3">
                            <ActBtn onClick={()=>setConfirmId({type:"issue",id:i.id})} label="Del" color="del"/>
                          </td>
                        </tr>
                      );
                    })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
};
