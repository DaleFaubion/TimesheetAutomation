document.addEventListener('DOMContentLoaded', () => {
  // Elements - Action Toolbar & Toggles
  const btnOpenManualModal = document.getElementById('btnOpenManualModal');
  const btnToggleScan = document.getElementById('btnToggleScan');
  const paperScanCard = document.getElementById('paperScanCard');
  const btnCloseScanCard = document.getElementById('btnCloseScanCard');
  const btnOpenWorkerQR = document.getElementById('btnOpenWorkerQR');
  const btnOpenCodesModal = document.getElementById('btnOpenCodesModal');
  const btnOpenFolder = document.getElementById('btnOpenFolder');
  const desktopDropzone = document.getElementById('desktopDropzone');
  const desktopFileInput = document.getElementById('desktopFileInput');
  const btnRunTestScan = document.getElementById('btnRunTestScan');

  // Stats
  const statTotalScans = document.getElementById('statTotalScans');
  const statCartCount = document.getElementById('statCartCount');
  const statActiveTabName = document.getElementById('statActiveTabName');
  const statActiveTabTotal = document.getElementById('statActiveTabTotal');

  // Cart Tabs Elements
  const cartTabsList = document.getElementById('cartTabsList');
  const currentTabTitle = document.getElementById('currentTabTitle');
  const currentTabTotalTime = document.getElementById('currentTabTotalTime');
  const quickAddCartName = document.getElementById('quickAddCartName');
  const btnQuickAddRow = document.getElementById('btnQuickAddRow');
  const cartTableBody = document.getElementById('cartTableBody');
  const cartFilterSearch = document.getElementById('cartFilterSearch');
  const btnRefreshTabs = document.getElementById('btnRefreshTabs');

  // Team & Trailers Management Elements
  const btnOpenRosterModal = document.getElementById('btnOpenRosterModal');
  const teamTrailersModal = document.getElementById('teamTrailersModal');
  const btnCloseRosterModal = document.getElementById('btnCloseRosterModal');
  const btnCloseRosterModalBottom = document.getElementById('btnCloseRosterModalBottom');
  const tabRosterWorkers = document.getElementById('tabRosterWorkers');
  const tabRosterTrailers = document.getElementById('tabRosterTrailers');
  const paneWorkers = document.getElementById('paneWorkers');
  const paneTrailers = document.getElementById('paneTrailers');
  const inputNewWorkerName = document.getElementById('inputNewWorkerName');
  const btnAddWorkerBtn = document.getElementById('btnAddWorkerBtn');
  const rosterBadgesList = document.getElementById('rosterBadgesList');
  const workerCountBadge = document.getElementById('workerCountBadge');
  const inputNewTrailerName = document.getElementById('inputNewTrailerName');
  const btnAddTrailerBtn = document.getElementById('btnAddTrailerBtn');
  const trailerBadgesList = document.getElementById('trailerBadgesList');
  const trailerCountBadge = document.getElementById('trailerCountBadge');
  const btnQuickAddTrailerTab = document.getElementById('btnQuickAddTrailerTab');

  // Google Sheets Elements
  const googleSheetsBadge = document.getElementById('googleSheetsBadge');
  const googleSheetsBadgeText = document.getElementById('googleSheetsBadgeText');
  const btnOpenGoogleSettings = document.getElementById('btnOpenGoogleSettings');
  const btnConfigureGoogleSheets = document.getElementById('btnConfigureGoogleSheets');
  const googleSheetsBanner = document.getElementById('googleSheetsBanner');
  const gsheetStatusTitle = document.getElementById('gsheetStatusTitle');
  const gsheetStatusSub = document.getElementById('gsheetStatusSub');
  const btnOpenSpreadsheetLink = document.getElementById('btnOpenSpreadsheetLink');
  const btnSyncAllSheets = document.getElementById('btnSyncAllSheets');
  const btnCheckGoogleSync = document.getElementById('btnCheckGoogleSync');

  const googleSettingsModal = document.getElementById('googleSettingsModal');
  const btnCloseGoogleModal = document.getElementById('btnCloseGoogleModal');
  const btnCancelGoogleModal = document.getElementById('btnCancelGoogleModal');
  const btnSaveGoogleSettings = document.getElementById('btnSaveGoogleSettings');
  const btnTestGoogleConnection = document.getElementById('btnTestGoogleConnection');
  const settingSheetUrl = document.getElementById('settingSheetUrl');
  const settingSheetTitle = document.getElementById('settingSheetTitle');
  const settingSyncEnabled = document.getElementById('settingSyncEnabled');
  const credsFileInput = document.getElementById('credsFileInput');
  const btnUploadCreds = document.getElementById('btnUploadCreds');
  const credsStatusText = document.getElementById('credsStatusText');
  const googleTestResultBox = document.getElementById('googleTestResultBox');

  // Scan Verification Modal
  const desktopVerifyModal = document.getElementById('desktopVerifyModal');
  const btnCloseModal = document.getElementById('btnCloseModal');
  const btnCancelModal = document.getElementById('btnCancelModal');
  const btnSaveModal = document.getElementById('btnSaveModal');
  const modalImgPreview = document.getElementById('modalImgPreview');
  const modalWorkerName = document.getElementById('modalWorkerName');
  const modalDate = document.getElementById('modalDate');
  const modalCheckboxBadge = document.getElementById('modalCheckboxBadge');
  const modalRowCountBadge = document.getElementById('modalRowCountBadge');
  const modalRowsTableBody = document.getElementById('modalRowsTableBody');
  const btnAddModalRow = document.getElementById('btnAddModalRow');
  const modalTotalCalculatedHours = document.getElementById('modalTotalCalculatedHours');
  const modalRawText = document.getElementById('modalRawText');
  const taskCodesDatalist = document.getElementById('taskCodesDatalist');

  // Manual Hand-Entry Modal Elements
  const manualEntryModal = document.getElementById('manualEntryModal');
  const btnCloseManualModal = document.getElementById('btnCloseManualModal');
  const btnCancelManualModal = document.getElementById('btnCancelManualModal');
  const btnSaveManualModal = document.getElementById('btnSaveManualModal');
  const manualWorkerName = document.getElementById('manualWorkerName');
  const manualDate = document.getElementById('manualDate');
  const manualDefaultCart = document.getElementById('manualDefaultCart');
  const manualRowsTableBody = document.getElementById('manualRowsTableBody');
  const btnAddManualRow = document.getElementById('btnAddManualRow');
  const manualTotalCalculatedHours = document.getElementById('manualTotalCalculatedHours');
  const manualWorkerChips = document.getElementById('manualWorkerChips');

  // Edit Row Modal Elements
  const editRowModal = document.getElementById('editRowModal');
  const btnCloseEditModal = document.getElementById('btnCloseEditModal');
  const btnCancelEditModal = document.getElementById('btnCancelEditModal');
  const btnSaveEditRow = document.getElementById('btnSaveEditRow');
  const editRowIndex = document.getElementById('editRowIndex');
  const editOriginalCart = document.getElementById('editOriginalCart');
  const editWorkerName = document.getElementById('editWorkerName');
  const editDate = document.getElementById('editDate');
  const editCartSelect = document.getElementById('editCartSelect');
  const editCode = document.getElementById('editCode');
  const editTaskDesc = document.getElementById('editTaskDesc');
  const editCategory = document.getElementById('editCategory');
  const editType = document.getElementById('editType');
  const editTimeIn = document.getElementById('editTimeIn');
  const editTimeOut = document.getElementById('editTimeOut');
  const editDuration = document.getElementById('editDuration');

  // Quick Add Row Modal Elements
  const quickAddRowModal = document.getElementById('quickAddRowModal');
  const btnCloseQuickAddModal = document.getElementById('btnCloseQuickAddModal');
  const btnCancelQuickAddModal = document.getElementById('btnCancelQuickAddModal');
  const btnSaveQuickAddRow = document.getElementById('btnSaveQuickAddRow');
  const quickAddModalCartTitle = document.getElementById('quickAddModalCartTitle');
  const quickAddWorkerName = document.getElementById('quickAddWorkerName');
  const quickAddWorkerChips = document.getElementById('quickAddWorkerChips');
  const quickAddDate = document.getElementById('quickAddDate');
  const quickAddCode = document.getElementById('quickAddCode');
  const quickAddTask = document.getElementById('quickAddTask');
  const quickAddCategory = document.getElementById('quickAddCategory');
  const quickAddType = document.getElementById('quickAddType');
  const quickAddTimeIn = document.getElementById('quickAddTimeIn');
  const quickAddTimeOut = document.getElementById('quickAddTimeOut');
  const quickAddDuration = document.getElementById('quickAddDuration');

  // Worker QR Modal Elements
  const workerQRModal = document.getElementById('workerQRModal');
  const btnCloseWorkerQRModal = document.getElementById('btnCloseWorkerQRModal');
  const btnCopyLinkModal = document.getElementById('btnCopyLinkModal');
  const btnPrintQRModal = document.getElementById('btnPrintQRModal');
  const qrUrlTextModal = document.getElementById('qrUrlTextModal');
  const qrImgModal = document.getElementById('qrImgModal');

  // Task Codes Modal Elements
  const taskCodesModal = document.getElementById('taskCodesModal');
  const btnCloseCodesModal = document.getElementById('btnCloseCodesModal');
  const codesFilterInput = document.getElementById('codesFilterInput');
  const codesTableBody = document.getElementById('codesTableBody');

  // Toast Container
  const toastContainer = document.getElementById('toastContainer');

  // State
  let activeCartTab = "FC127";
  let cachedCartRows = [];
  let currentDesktopImageName = "";
  let currentDesktopRawText = "";
  let codesDatabase = { mt_codes: [], rt_codes: [], cart_tabs: [], worker_roster: [] };
  let configuredCartTabs = [];
  let activeWorkers = [];

  // ==========================================
  // 1. Initial Load & Code References
  // ==========================================
  initCodes();
  loadGoogleSheetsStatus();
  loadCartSummaries();
  loadCartData(activeCartTab);

  function getTodayFormatted() {
    const now = new Date();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    const yyyy = now.getFullYear();
    return `${mm}/${dd}/${yyyy}`;
  }

  async function initCodes() {
    try {
      const res = await fetch('/api/codes');
      if (res.ok) {
        codesDatabase = await res.json();
        configuredCartTabs = codesDatabase.cart_tabs || [];
        activeWorkers = codesDatabase.worker_roster || [];
        if (!activeCartTab && configuredCartTabs.length > 0) {
          activeCartTab = configuredCartTabs[0];
        }
        populateCodesDatalist();
        renderCodesTable();
        populateCartSelects();
        renderWorkerChips(activeWorkers);
        renderRosterManager();
      }
    } catch (e) {
      console.warn("Could not load codes database", e);
    }
  }

  function populateCartSelects() {
    const tabs = (configuredCartTabs && configuredCartTabs.length > 0)
      ? configuredCartTabs
      : ["FC127", "FC121", "FC122", "FC123", "FC124", "FC125", "FC126", "FC128", "FC129", "FC130", "Shop"];
    const buildOptions = (selectedVal) => {
      return tabs.map(t => `<option value="${escapeHtml(t)}" ${t === selectedVal ? 'selected' : ''}>${escapeHtml(t)}</option>`).join('');
    };
    if (manualDefaultCart) {
      const cur = manualDefaultCart.value;
      manualDefaultCart.innerHTML = buildOptions(cur || activeCartTab);
    }
    if (editCartSelect) {
      const cur = editCartSelect.value;
      editCartSelect.innerHTML = buildOptions(cur || activeCartTab);
    }
  }

  function renderWorkerChips(workers) {
    if (!workers || workers.length === 0) return;
    const chipsHtml = workers.map(w => `<span class="worker-chip" data-name="${escapeHtml(w)}">${escapeHtml(w)}</span>`).join('');
    if (manualWorkerChips) {
      manualWorkerChips.innerHTML = chipsHtml;
      manualWorkerChips.querySelectorAll('.worker-chip').forEach(chip => {
        chip.addEventListener('click', () => {
          manualWorkerName.value = chip.getAttribute('data-name');
          manualWorkerChips.querySelectorAll('.worker-chip').forEach(c => c.classList.remove('active'));
          chip.classList.add('active');
        });
      });
    }
    if (quickAddWorkerChips) {
      quickAddWorkerChips.innerHTML = chipsHtml;
      quickAddWorkerChips.querySelectorAll('.worker-chip').forEach(chip => {
        chip.addEventListener('click', () => {
          quickAddWorkerName.value = chip.getAttribute('data-name');
          quickAddWorkerChips.querySelectorAll('.worker-chip').forEach(c => c.classList.remove('active'));
          chip.classList.add('active');
        });
      });
    }
  }

  function populateCodesDatalist() {
    if (!taskCodesDatalist) return;
    taskCodesDatalist.innerHTML = '';
    const allCodes = [...(codesDatabase.mt_codes || []), ...(codesDatabase.rt_codes || [])];
    allCodes.forEach(item => {
      const opt = document.createElement('option');
      opt.value = item.code;
      opt.label = `${item.code} (${item.type}) - ${item.category}: ${item.task}`;
      taskCodesDatalist.appendChild(opt);
    });
  }

  function renderCodesTable(query = '') {
    if (!codesTableBody) return;
    const q = (query || '').toLowerCase().trim();
    const allCodes = [...(codesDatabase.mt_codes || []), ...(codesDatabase.rt_codes || [])];
    const filtered = allCodes.filter(c => {
      if (!q) return true;
      return (c.code || '').toLowerCase().includes(q) ||
             (c.task || '').toLowerCase().includes(q) ||
             (c.category || '').toLowerCase().includes(q) ||
             (c.type || '').toLowerCase().includes(q);
    });

    if (filtered.length === 0) {
      codesTableBody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 18px; color: var(--text-tertiary);">No matching codes found.</td></tr>`;
      return;
    }

    codesTableBody.innerHTML = filtered.map(c => `
      <tr>
        <td><strong class="code-pill">${escapeHtml(c.code)}</strong></td>
        <td><span style="font-size:0.8rem; color:var(--text-secondary);">${escapeHtml(c.type)}</span></td>
        <td><strong>${escapeHtml(c.category)}</strong></td>
        <td>${escapeHtml(c.task)}</td>
      </tr>
    `).join('');
  }

  if (codesFilterInput) {
    codesFilterInput.addEventListener('input', () => renderCodesTable(codesFilterInput.value));
  }

  // ==========================================
  // 2. Toast Notifications
  // ==========================================
  function showToast(message, type = 'success') {
    if (!toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `app-toast ${type}`;
    const icon = type === 'success' ? '✓' : '⚠️';
    toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  // ==========================================
  // 3. Cart Navigation & Table Rendering
  // ==========================================
  async function loadCartSummaries() {
    try {
      const res = await fetch('/api/carts/summary');
      if (!res.ok) return;
      const data = await res.json();
      const carts = data.carts || [];

      statCartCount.textContent = carts.length;
      let totalAllEntries = 0;
      carts.forEach(c => totalAllEntries += (c.entry_count || 0));
      statTotalScans.textContent = totalAllEntries;

      renderCartTabButtons(carts);
    } catch (e) {
      console.error("Failed to load cart summaries:", e);
    }
  }

  function renderCartTabButtons(carts) {
    const standardTabNames = (configuredCartTabs && configuredCartTabs.length > 0)
      ? [...configuredCartTabs]
      : ["FC127", "FC121", "FC122", "FC123", "FC124", "FC125", "FC126", "FC128", "FC129", "FC130", "Shop"];

    carts.forEach(c => {
      if (!standardTabNames.includes(c.cart_id) && c.cart_id !== "All Audit Log") {
        standardTabNames.push(c.cart_id);
      }
    });

    const cartMap = {};
    carts.forEach(c => cartMap[c.cart_id] = c);

    let html = standardTabNames.map(name => {
      const info = cartMap[name] || { entry_count: 0 };
      const isActive = (name === activeCartTab) ? 'active' : '';
      const countBadge = info.entry_count > 0 ? ` <span style="font-size: 0.72rem; opacity: 0.85;">(${info.entry_count})</span>` : '';
      return `<button class="cart-tab-btn ${isActive}" data-cart="${escapeHtml(name)}">${escapeHtml(name)}${countBadge}</button>`;
    }).join('');

    const isAllActive = activeCartTab === '__ALL__' ? 'active' : '';
    html += `<button class="cart-tab-btn ${isAllActive}" data-cart="__ALL__">All Audit Log</button>`;

    cartTabsList.innerHTML = html;

    cartTabsList.querySelectorAll('.cart-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const cartId = e.currentTarget.getAttribute('data-cart');
        switchCartTab(cartId);
      });
    });
  }

  function switchCartTab(cartId) {
    activeCartTab = cartId;
    if (quickAddCartName) quickAddCartName.textContent = cartId;
    if (btnQuickAddRow) {
      btnQuickAddRow.style.display = cartId === '__ALL__' ? 'none' : 'inline-flex';
    }

    cartTabsList.querySelectorAll('.cart-tab-btn').forEach(btn => {
      if (btn.getAttribute('data-cart') === cartId) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    if (cartId === '__ALL__') {
      loadAuditLog();
    } else {
      loadCartData(cartId);
    }
  }

  async function loadCartData(cartId) {
    if (currentTabTitle) currentTabTitle.textContent = `Trailer Number: ${cartId}`;
    if (statActiveTabName) statActiveTabName.textContent = cartId;
    if (quickAddCartName) quickAddCartName.textContent = cartId;

    if (cartTableBody) {
      cartTableBody.innerHTML = `
        <tr>
          <td colspan="10" style="text-align: center; color: var(--text-tertiary); padding: 24px;">
            Loading entries for ${escapeHtml(cartId)}...
          </td>
        </tr>
      `;
    }

    try {
      const res = await fetch(`/api/cart/${encodeURIComponent(cartId)}`);
      const data = await res.json();
      if (!res.ok || !data || data.status !== 'success') {
        if (cartTableBody) {
          cartTableBody.innerHTML = `
            <tr><td colspan="10" style="text-align: center; padding: 20px; color: #dc2626;">Could not load data.</td></tr>
          `;
        }
        return;
      }

      const cart = data.cart || {};
      const totalTime = cart.total_time || "0:00:00";
      if (currentTabTotalTime) currentTabTotalTime.textContent = `Total Time: ${totalTime}`;
      if (statActiveTabTotal) statActiveTabTotal.textContent = `Total: ${totalTime}`;
      cachedCartRows = cart.rows || [];

      renderCartRows(cachedCartRows);
    } catch (e) {
      console.error(e);
      if (cartTableBody) {
        cartTableBody.innerHTML = `<tr><td colspan="10" style="text-align: center;">Error loading trailer entries.</td></tr>`;
      }
    }
  }

  async function loadAuditLog() {
    currentTabTitle.textContent = "Global Audit Log (All Carts)";
    statActiveTabName.textContent = "All Log";
    currentTabTotalTime.textContent = "Raw CSV Stream";
    cartTableBody.innerHTML = `<tr><td colspan="10" style="text-align: center; padding: 24px;">Loading audit log...</td></tr>`;

    try {
      const res = await fetch('/api/history');
      const data = await res.json();
      const history = data.history || [];
      if (history.length === 0) {
        cartTableBody.innerHTML = `<tr><td colspan="10" style="text-align: center; padding: 24px; color: var(--text-tertiary);">No entries logged yet.</td></tr>`;
        return;
      }

      cartTableBody.innerHTML = history.map(row => `
        <tr>
          <td style="font-weight: 600;">${escapeHtml(row['Worker Name'] || '-')}</td>
          <td>${escapeHtml(row['Task'] || row['Notes & Descriptions'] || '-')}</td>
          <td>${escapeHtml(row['Category'] || '-')}</td>
          <td>${escapeHtml(row['Build / Reconditioning'] || '-')}</td>
          <td><span class="code-pill">${escapeHtml(row['Code'] || row['Job / Task Code'] || '-')}</span></td>
          <td>${escapeHtml(row['Date'] || '-')}</td>
          <td>${escapeHtml(row['Time In'] || '-')}</td>
          <td>${escapeHtml(row['Time Out'] || '-')}</td>
          <td style="text-align: right; font-weight: 700; color: #15803d;">${escapeHtml(row['Task Total'] || row['Hours Worked'] || '-')}</td>
          <td style="text-align: right; color: var(--text-tertiary); font-size: 0.75rem;">Audit Log</td>
        </tr>
      `).join('');
    } catch (e) {
      cartTableBody.innerHTML = `<tr><td colspan="10" style="text-align: center;">Error loading log.</td></tr>`;
    }
  }

  function renderCartRows(rows) {
    if (!rows || rows.length === 0) {
      cartTableBody.innerHTML = `
        <tr>
          <td colspan="10" style="text-align: center; color: var(--text-tertiary); padding: 32px 20px;">
            <div style="font-weight: 600; margin-bottom: 6px; color: var(--brand-navy);">No task records logged for ${escapeHtml(activeCartTab)} yet.</div>
            <div style="font-size: 0.85rem; margin-bottom: 14px;">Use "Enter Timesheet (By Hand)" above to log hours directly into this sheet.</div>
            <button class="btn btn-sm btn-primary" onclick="window.openQuickAddModal()">+ Add First Entry</button>
          </td>
        </tr>
      `;
      return;
    }

    const query = (cartFilterSearch && cartFilterSearch.value ? cartFilterSearch.value : "").toLowerCase().trim();
    const filtered = rows.filter(r => {
      if (!query) return true;
      return (r.name || '').toLowerCase().includes(query) ||
             (r.task || '').toLowerCase().includes(query) ||
             (r.category || '').toLowerCase().includes(query) ||
             (r.code || '').toLowerCase().includes(query) ||
             (r.date || '').toLowerCase().includes(query);
    });

    if (filtered.length === 0) {
      cartTableBody.innerHTML = `
        <tr><td colspan="10" style="text-align: center; color: var(--text-tertiary); padding: 20px;">No matching rows found for "${escapeHtml(query)}".</td></tr>
      `;
      return;
    }

    cartTableBody.innerHTML = filtered.map(r => {
      const totalDisplay = (r.task_total && !r.task_total.startsWith('=') && r.task_total !== '0:00:00')
        ? r.task_total
        : ((r.time_in && r.time_out) ? calculateDuration(r.time_in, r.time_out) : (r.task_total || '-'));

      return `
        <tr>
          <td style="font-weight: 600; color: var(--text-primary);">${escapeHtml(r.name || '-')}</td>
          <td style="color: #0f172a;">${escapeHtml(r.task || '-')}</td>
          <td><span style="font-size: 0.8rem; background: var(--surface-muted); padding: 2px 6px; border-radius: 4px;">${escapeHtml(r.category || '-')}</span></td>
          <td style="font-size: 0.8rem; color: var(--text-secondary);">${escapeHtml(r.type || '-')}</td>
          <td><span class="code-pill">${escapeHtml(r.code || '-')}</span></td>
          <td>${escapeHtml(r.date || '-')}</td>
          <td>${escapeHtml(r.time_in || '-')}</td>
          <td>${escapeHtml(r.time_out || '-')}</td>
          <td style="text-align: right; font-weight: 700; color: #15803d;">${escapeHtml(totalDisplay)}</td>
          <td style="text-align: right;">
            <div class="action-cell">
              <button class="btn-table-action btn-edit-row" data-row-idx="${r.row_idx}" title="Edit this entry by hand">✏️ Edit</button>
              <button class="btn-table-action btn-delete-row" data-row-idx="${r.row_idx}" title="Delete this entry">🗑️</button>
            </div>
          </td>
        </tr>
      `;
    }).join('');

    // Attach row Edit & Delete listeners
    cartTableBody.querySelectorAll('.btn-edit-row').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const rowIdx = parseInt(e.currentTarget.getAttribute('data-row-idx'));
        const row = cachedCartRows.find(r => r.row_idx === rowIdx);
        if (row) openEditRowModal(row);
      });
    });

    cartTableBody.querySelectorAll('.btn-delete-row').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const rowIdx = parseInt(e.currentTarget.getAttribute('data-row-idx'));
        const row = cachedCartRows.find(r => r.row_idx === rowIdx);
        if (row) confirmDeleteRow(row);
      });
    });
  }

  if (cartFilterSearch) {
    cartFilterSearch.addEventListener('input', () => {
      if (activeCartTab !== '__ALL__') {
        renderCartRows(cachedCartRows);
      }
    });
  }

  let lastRefreshTime = 0;
  function refreshAllCartTabs(e) {
    if (e && e.preventDefault) e.preventDefault();
    const now = Date.now();
    if (now - lastRefreshTime < 500) return;
    lastRefreshTime = now;

    loadCartSummaries();
    if (activeCartTab === '__ALL__') {
      loadAuditLog();
    } else {
      loadCartData(activeCartTab);
    }
  }
  window.refreshAllCartTabs = refreshAllCartTabs;

  if (btnRefreshTabs) {
    btnRefreshTabs.addEventListener('click', refreshAllCartTabs);
  }

  // ==========================================
  // 4. Edit Row by Hand Logic
  // ==========================================
  function openEditRowModal(row) {
    editRowIndex.value = row.row_idx;
    editOriginalCart.value = activeCartTab;
    editWorkerName.value = row.name || '';
    editDate.value = row.date || getTodayFormatted();
    editCartSelect.value = activeCartTab !== '__ALL__' ? activeCartTab : 'FC127';
    editCode.value = row.code || '';
    editTaskDesc.value = row.task || '';
    editCategory.value = row.category || 'Misc.';
    editType.value = row.type || 'Build';
    editTimeIn.value = row.time_in || '08:00 AM';
    editTimeOut.value = row.time_out || '09:00 AM';
    editDuration.value = row.task_total || calculateDuration(editTimeIn.value, editTimeOut.value);

    editRowModal.classList.remove('hidden');
  }

  function closeEditModal() {
    editRowModal.classList.add('hidden');
  }

  if (btnCloseEditModal) btnCloseEditModal.addEventListener('click', closeEditModal);
  if (btnCancelEditModal) btnCancelEditModal.addEventListener('click', closeEditModal);

  function recalcEditDuration() {
    if (editDuration && editTimeIn && editTimeOut) {
      editDuration.value = calculateDuration(editTimeIn.value, editTimeOut.value);
    }
  }

  if (editTimeIn) {
    editTimeIn.addEventListener('input', recalcEditDuration);
    editTimeIn.addEventListener('change', recalcEditDuration);
  }
  if (editTimeOut) {
    editTimeOut.addEventListener('input', recalcEditDuration);
    editTimeOut.addEventListener('change', recalcEditDuration);
  }

  // Auto-fill on code change in edit modal
  if (editCode) {
    editCode.addEventListener('change', () => {
      const val = editCode.value.trim().toUpperCase();
      const allCodes = [...(codesDatabase.mt_codes || []), ...(codesDatabase.rt_codes || [])];
      const match = allCodes.find(c => c.code.toUpperCase() === val);
      if (match) {
        if (editCategory) editCategory.value = match.category;
        if (editType) editType.value = match.type;
        if (editTaskDesc && (!editTaskDesc.value.trim() || editTaskDesc.value === 'Task')) {
          editTaskDesc.value = match.task;
        }
      }
    });
  }

  if (btnSaveEditRow) {
    btnSaveEditRow.addEventListener('click', async () => {
    const rowIdx = parseInt(editRowIndex.value);
    const origCart = editOriginalCart.value;
    const worker = editWorkerName.value.trim();
    const date = editDate.value.trim();
    const cart = editCartSelect.value;
    const task = editTaskDesc.value.trim();
    const code = editCode.value.trim().toUpperCase();
    const category = editCategory.value.trim();
    const type = editType.value;
    const tin = editTimeIn.value.trim();
    const tout = editTimeOut.value.trim();
    const dur = editDuration.value.trim();

    if (!worker) { alert('Please enter an employee name.'); return; }
    if (!task) { alert('Please enter a task description.'); return; }
    if (!tin) { alert('Please enter a Start Time.'); return; }
    if (!tout) { alert('Please enter an End Time.'); return; }

    btnSaveEditRow.disabled = true;
    btnSaveEditRow.textContent = "Saving to Sheets...";

    try {
      const res = await fetch(`/api/cart/${encodeURIComponent(origCart)}/row/${rowIdx}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: worker,
          date: date,
          cart_id: cart,
          task: task,
          code: code,
          category: category,
          type: type,
          time_in: tin,
          time_out: tout,
          task_total: dur
        })
      });
      const data = await res.json();
      btnSaveEditRow.disabled = false;
      btnSaveEditRow.textContent = "Save Changes to Sheet";

      if (res.ok && data.status === 'success') {
        closeEditModal();
        showToast(`✓ Updated entry for ${worker} (${task})!`);
        loadCartSummaries();
        loadCartData(cart || activeCartTab);
      } else {
        alert(data.message || 'Error updating entry.');
      }
    } catch (e) {
      btnSaveEditRow.disabled = false;
      btnSaveEditRow.textContent = "Save Changes to Sheet";
      alert('Network error updating entry.');
    }
  });
  }

  async function confirmDeleteRow(row) {
    const msg = `Are you sure you want to delete this task entry?\n\n• Worker: ${row.name || 'Unknown'}\n• Task: ${row.task || '-'}\n• Time: ${row.time_in} - ${row.time_out}\n\nThis will remove the line from Excel and Google Sheets.`;
    if (!confirm(msg)) return;

    try {
      const res = await fetch(`/api/cart/${encodeURIComponent(activeCartTab)}/row/${row.row_idx}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        showToast(`✓ Removed task entry from ${activeCartTab}`);
        loadCartSummaries();
        loadCartData(activeCartTab);
      } else {
        alert(data.message || 'Could not delete entry.');
      }
    } catch (e) {
      alert('Network error while deleting entry.');
    }
  }

  // ==========================================
  // 5. Quick Add Single Row Modal
  // ==========================================
  let lastQuickAddOpenTime = 0;
  function openQuickAddModal(e) {
    if (e && e.preventDefault) e.preventDefault();
    const now = Date.now();
    if (now - lastQuickAddOpenTime < 300) return;
    lastQuickAddOpenTime = now;

    const targetCart = activeCartTab !== '__ALL__' ? activeCartTab : (configuredCartTabs[0] || 'FC127');
    if (quickAddModalCartTitle) quickAddModalCartTitle.textContent = targetCart;
    if (quickAddDate) quickAddDate.value = getTodayFormatted();
    if (quickAddWorkerName) quickAddWorkerName.value = '';
    if (quickAddCode) quickAddCode.value = '';
    if (quickAddTask) quickAddTask.value = '';
    if (quickAddCategory) quickAddCategory.value = 'Misc.';
    if (quickAddType) quickAddType.value = 'Build';
    if (quickAddTimeIn) quickAddTimeIn.value = '08:00 AM';
    if (quickAddTimeOut) quickAddTimeOut.value = '10:00 AM';
    if (quickAddDuration) quickAddDuration.value = '2:00:00';
    if (quickAddRowModal) quickAddRowModal.classList.remove('hidden');
  }
  window.openQuickAddModal = openQuickAddModal;

  if (btnQuickAddRow) {
    btnQuickAddRow.addEventListener('click', openQuickAddModal);
  }

  function closeQuickAddModal() {
    if (quickAddRowModal) quickAddRowModal.classList.add('hidden');
  }
  window.closeQuickAddModal = closeQuickAddModal;

  if (btnCloseQuickAddModal) btnCloseQuickAddModal.addEventListener('click', closeQuickAddModal);
  if (btnCancelQuickAddModal) btnCancelQuickAddModal.addEventListener('click', closeQuickAddModal);

  function recalcQuickAddDuration() {
    if (quickAddDuration && quickAddTimeIn && quickAddTimeOut) {
      quickAddDuration.value = calculateDuration(quickAddTimeIn.value, quickAddTimeOut.value);
    }
  }
  if (quickAddTimeIn) quickAddTimeIn.addEventListener('input', recalcQuickAddDuration);
  if (quickAddTimeOut) quickAddTimeOut.addEventListener('input', recalcQuickAddDuration);

  if (quickAddCode) {
    quickAddCode.addEventListener('change', () => {
      const val = quickAddCode.value.trim().toUpperCase();
      const allCodes = [...(codesDatabase.mt_codes || []), ...(codesDatabase.rt_codes || [])];
      const match = allCodes.find(c => c.code.toUpperCase() === val);
      if (match) {
        if (quickAddCategory) quickAddCategory.value = match.category;
        if (quickAddType) quickAddType.value = match.type;
        if (quickAddTask && !quickAddTask.value.trim()) quickAddTask.value = match.task;
      }
    });
  }

  // Worker chips for quick add
  if (quickAddWorkerChips) {
    quickAddWorkerChips.querySelectorAll('.worker-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        if (quickAddWorkerName) quickAddWorkerName.value = chip.getAttribute('data-name');
        quickAddWorkerChips.querySelectorAll('.worker-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
      });
    });
  }

  if (btnSaveQuickAddRow) {
    btnSaveQuickAddRow.addEventListener('click', async () => {
    const targetCart = activeCartTab !== '__ALL__' ? activeCartTab : 'FC127';
    const worker = quickAddWorkerName.value.trim();
    const task = quickAddTask.value.trim();
    const tin = quickAddTimeIn.value.trim();
    const tout = quickAddTimeOut.value.trim();

    if (!worker) { alert('Please enter an employee name.'); return; }
    if (!task) { alert('Please enter a task description.'); return; }
    if (!tin) { alert('Please enter a Start Time.'); return; }
    if (!tout) { alert('Please enter an End Time.'); return; }

    btnSaveQuickAddRow.disabled = true;
    btnSaveQuickAddRow.textContent = "Adding...";

    try {
      const res = await fetch(`/api/cart/${encodeURIComponent(targetCart)}/row`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          worker_name: worker,
          date: quickAddDate.value.trim(),
          task: task,
          code: quickAddCode.value.trim().toUpperCase(),
          category: quickAddCategory.value.trim(),
          type: quickAddType.value,
          time_in: tin,
          time_out: tout,
          duration: quickAddDuration.value.trim()
        })
      });
      const data = await res.json();
      btnSaveQuickAddRow.disabled = false;
      btnSaveQuickAddRow.textContent = "Add to Sheet & Sync";

      if (res.ok && data.status === 'success') {
        closeQuickAddModal();
        showToast(`✓ Added task for ${worker} to ${targetCart}!`);
        loadCartSummaries();
        loadCartData(targetCart);
      } else {
        alert(data.message || 'Could not add entry.');
      }
    } catch (e) {
      btnSaveQuickAddRow.disabled = false;
      btnSaveQuickAddRow.textContent = "Add to Sheet & Sync";
      alert('Network error adding entry.');
    }
  });
  }

  // ==========================================
  // 6. Manual Timesheet Hand-Entry Flow
  // ==========================================
  let lastManualOpenTime = 0;
  function openManualModal(e) {
    if (e && e.preventDefault) e.preventDefault();
    const now = Date.now();
    if (now - lastManualOpenTime < 300) return;
    lastManualOpenTime = now;

    if (manualDate) manualDate.value = getTodayFormatted();
    if (manualWorkerName) manualWorkerName.value = '';
    if (manualDefaultCart) {
      manualDefaultCart.value = activeCartTab !== '__ALL__' ? activeCartTab : (configuredCartTabs[0] || 'FC127');
    }
    if (manualRowsTableBody) {
      manualRowsTableBody.innerHTML = '';
      addManualRowItem({ task: '', code: 'S6', category: 'Shell', type: 'Build', time_in: '08:00 AM', time_out: '10:00 AM' });
      addManualRowItem({ task: '', code: 'F2', category: 'Frame', type: 'Build', time_in: '10:00 AM', time_out: '12:00 PM' });
      addManualRowItem({ task: '', code: 'H1', category: 'Hood', type: 'Build', time_in: '12:30 PM', time_out: '04:30 PM' });
    }
    recalcManualTotal();
    if (manualEntryModal) manualEntryModal.classList.remove('hidden');
  }
  window.openManualModal = openManualModal;

  if (btnOpenManualModal) {
    btnOpenManualModal.addEventListener('click', openManualModal);
  }

  function closeManualModal() {
    if (manualEntryModal) manualEntryModal.classList.add('hidden');
  }
  window.closeManualModal = closeManualModal;

  if (btnCloseManualModal) btnCloseManualModal.addEventListener('click', closeManualModal);
  if (btnCancelManualModal) btnCancelManualModal.addEventListener('click', closeManualModal);

  // Worker chips for manual modal
  if (manualWorkerChips) {
    manualWorkerChips.querySelectorAll('.worker-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        if (manualWorkerName) manualWorkerName.value = chip.getAttribute('data-name');
        manualWorkerChips.querySelectorAll('.worker-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
      });
    });
  }

  if (btnAddManualRow) {
    btnAddManualRow.addEventListener('click', () => {
      const allRows = manualRowsTableBody ? manualRowsTableBody.querySelectorAll('.manual-task-row') : [];
      let nextStart = "08:00 AM";
      if (allRows && allRows.length > 0) {
        const lastRow = allRows[allRows.length - 1];
        const lastToutEl = lastRow ? lastRow.querySelector('.row-timeout') : null;
        if (lastToutEl && lastToutEl.value && lastToutEl.value.trim()) {
          nextStart = lastToutEl.value.trim();
        }
      }

      addManualRowItem({
        task: '',
        code: '',
        category: 'Misc.',
        type: 'Build',
        time_in: nextStart,
        time_out: '',
        duration: '0:00:00',
        cart_id: (manualDefaultCart ? manualDefaultCart.value : '') || 'FC127'
      });
      recalcManualTotal();
    });
  }

  function addManualRowItem(r = {}) {
    const tr = document.createElement('tr');
    tr.className = 'manual-task-row';

    const defaultCart = r.cart_id || (manualDefaultCart ? manualDefaultCart.value : '') || 'FC127';
    const defaultType = r.type || 'Build';
    const initialDur = (r.time_in && r.time_out) ? calculateDuration(r.time_in, r.time_out) : (r.duration || '0:00:00');
    const initialDate = r.date || (manualDate ? manualDate.value : '') || getTodayFormatted();

    tr.innerHTML = `
      <td><input type="text" class="row-input-compact row-task" value="${escapeHtml(r.task || '')}" placeholder="Task description"></td>
      <td><input type="text" list="taskCodesDatalist" class="row-input-compact row-code" value="${escapeHtml(r.code || '')}" placeholder="e.g. S6" style="text-transform: uppercase;"></td>
      <td><input type="text" class="row-input-compact row-category" value="${escapeHtml(r.category || 'Misc.')}"></td>
      <td>
        <select class="row-input-compact row-type">
          <option value="Build" ${defaultType === 'Build' ? 'selected' : ''}>Build</option>
          <option value="Reconditioning" ${defaultType === 'Reconditioning' ? 'selected' : ''}>Reconditioning</option>
        </select>
      </td>
      <td><input type="text" class="row-input-compact row-date" value="${escapeHtml(initialDate)}" placeholder="MM/DD/YYYY"></td>
      <td><input type="text" class="row-input-compact row-timein" value="${escapeHtml(r.time_in || '08:00 AM')}" placeholder="e.g. 8:00 AM"></td>
      <td><input type="text" class="row-input-compact row-timeout" value="${escapeHtml(r.time_out || '')}" placeholder="e.g. 12:00 PM"></td>
      <td><input type="text" class="row-input-compact row-duration" value="${escapeHtml(initialDur)}" readonly style="font-weight: 700; color: #047857; background: #f0fdf4; cursor: default;"></td>
      <td><input type="text" class="row-input-compact row-cart" value="${escapeHtml(defaultCart)}" style="font-weight: 600;"></td>
      <td style="text-align: center;"><button type="button" class="btn-remove-row" title="Delete Row">&times;</button></td>
    `;

    const codeInput = tr.querySelector('.row-code');
    if (codeInput) {
      codeInput.addEventListener('change', () => {
        const val = codeInput.value.trim().toUpperCase();
        const allCodes = [...(codesDatabase.mt_codes || []), ...(codesDatabase.rt_codes || [])];
        const match = allCodes.find(c => c.code.toUpperCase() === val);
        if (match) {
          const cat = tr.querySelector('.row-category');
          if (cat) cat.value = match.category;
          const typ = tr.querySelector('.row-type');
          if (typ) typ.value = match.type;
          const taskInput = tr.querySelector('.row-task');
          if (taskInput && (!taskInput.value.trim() || taskInput.value === 'Task')) {
            taskInput.value = match.task;
          }
        }
      });
    }

    const timeInInput = tr.querySelector('.row-timein');
    const timeOutInput = tr.querySelector('.row-timeout');
    const durationInput = tr.querySelector('.row-duration');

    function updateRowDuration() {
      const allRows = manualRowsTableBody ? Array.from(manualRowsTableBody.querySelectorAll('.manual-task-row')) : [];
      const thisIdx = allRows.indexOf(tr);
      if (thisIdx > 0 && timeInInput && timeInInput.value.trim()) {
        const prevRow = allRows[thisIdx - 1];
        const prevTout = prevRow ? prevRow.querySelector('.row-timeout') : null;
        if (prevTout && !prevTout.value.trim()) {
          prevTout.value = timeInInput.value.trim();
          const prevTin = prevRow.querySelector('.row-timein');
          const prevDur = prevRow.querySelector('.row-duration');
          if (prevTin && prevDur) {
            prevDur.value = calculateDuration(prevTin.value, prevTout.value);
          }
        }
      }

      if (durationInput && timeInInput && timeOutInput) {
        durationInput.value = calculateDuration(timeInInput.value, timeOutInput.value);
      }
      recalcManualTotal();
    }

    if (timeInInput) {
      timeInInput.addEventListener('input', updateRowDuration);
      timeInInput.addEventListener('change', updateRowDuration);
    }
    if (timeOutInput) {
      timeOutInput.addEventListener('input', updateRowDuration);
      timeOutInput.addEventListener('change', updateRowDuration);
    }

    const removeBtn = tr.querySelector('.btn-remove-row');
    if (removeBtn) {
      removeBtn.addEventListener('click', () => {
        tr.remove();
        recalcManualTotal();
      });
    }

    if (manualRowsTableBody) {
      manualRowsTableBody.appendChild(tr);
    }
  }

  function recalcManualTotal() {
    let totalMinutes = 0;
    const durInputs = manualRowsTableBody ? manualRowsTableBody.querySelectorAll('.row-duration') : [];
    durInputs.forEach(input => {
      const parts = input.value.split(':');
      if (parts.length >= 2) {
        const hrs = parseInt(parts[0]) || 0;
        const mins = parseInt(parts[1]) || 0;
        totalMinutes += (hrs * 60) + mins;
      }
    });

    const h = Math.floor(totalMinutes / 60);
    const m = totalMinutes % 60;
    if (manualTotalCalculatedHours) {
      manualTotalCalculatedHours.textContent = `${h}:${String(m).padStart(2, '0')}:00`;
    }
  }

  if (btnSaveManualModal) {
    btnSaveManualModal.addEventListener('click', async () => {
      const rows = [];
      const trs = manualRowsTableBody ? manualRowsTableBody.querySelectorAll('.manual-task-row') : [];
      const worker = manualWorkerName ? manualWorkerName.value.trim() : '';
      if (!worker) {
        alert('Please enter or select a Worker Name.');
        if (manualWorkerName && typeof manualWorkerName.focus === 'function') {
          manualWorkerName.focus();
        }
        return;
      }
      const dateVal = (manualDate && manualDate.value.trim()) || getTodayFormatted();
      let hasValidationError = false;
      let errorMsg = '';

      trs.forEach((tr, idx) => {
        const taskEl = tr.querySelector('.row-task');
        const codeEl = tr.querySelector('.row-code');
        const catEl = tr.querySelector('.row-category');
        const typeEl = tr.querySelector('.row-type');
        const tinEl = tr.querySelector('.row-timein');
        const toutEl = tr.querySelector('.row-timeout');
        const durEl = tr.querySelector('.row-duration');
        const cartEl = tr.querySelector('.row-cart');
        const dateEl = tr.querySelector('.row-date');

        const taskVal = taskEl ? taskEl.value.trim() : '';
        const codeVal = codeEl ? codeEl.value.trim().toUpperCase() : '';
        const catVal = catEl ? catEl.value.trim() : 'Misc.';
        const typeVal = typeEl ? typeEl.value : 'Build';
        const tinVal = tinEl ? tinEl.value.trim() : '';
        const toutVal = toutEl ? toutEl.value.trim() : '';
        const durVal = durEl ? durEl.value.trim() : '0:00:00';
        const cartVal = (cartEl && cartEl.value.trim()) || (manualDefaultCart ? manualDefaultCart.value : '') || 'FC127';
        const rowDateVal = (dateEl && dateEl.value.trim()) || dateVal;

        if (!taskVal && !tinVal && !toutVal) return;

        if (!tinVal) {
          hasValidationError = true;
          errorMsg = `Task row #${idx + 1} is missing a Start Time.`;
          if (tinEl && typeof tinEl.focus === 'function') tinEl.focus();
          return;
        }
        if (!toutVal) {
          hasValidationError = true;
          errorMsg = `Task row #${idx + 1} is missing an End Time.`;
          if (toutEl && typeof toutEl.focus === 'function') toutEl.focus();
          return;
        }

        rows.push({
          task: taskVal || 'General Work',
          code: codeVal,
          category: catVal || 'Misc.',
          type: typeVal,
          time_in: tinVal,
          time_out: toutVal,
          duration: durVal || '0:00:00',
          cart_id: cartVal,
          date: rowDateVal
        });
      });

      if (hasValidationError) {
        alert(`Validation Warning:\n${errorMsg}`);
        return;
      }

      if (rows.length === 0) {
        alert('Please enter at least one task row before saving.');
        return;
      }

      const payload = {
        source: "Manager Hand Input",
        worker_name: worker,
        date: dateVal,
        rows: rows
      };

      btnSaveManualModal.disabled = true;
      btnSaveManualModal.textContent = "Saving to Google Sheets & Excel...";

      try {
        const res = await fetch('/api/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const result = await res.json();
        btnSaveManualModal.disabled = false;
        btnSaveManualModal.textContent = "Save & Sync to Google Sheets & Excel";

        if (res.ok && result.status === 'success') {
          closeManualModal();
          const tabsUpdated = (result.tabs_updated || []).join(', ');
          showToast(`✓ Saved ${result.rows_saved} entries to tabs: [${tabsUpdated}]!`);
          loadCartSummaries();
          loadCartData(activeCartTab !== '__ALL__' ? activeCartTab : 'FC127');
          loadGoogleSheetsStatus();
        } else {
          alert(result.message || 'Error saving timesheet.');
        }
      } catch (e) {
        btnSaveManualModal.disabled = false;
        btnSaveManualModal.textContent = "Save & Sync to Google Sheets & Excel";
        alert('Failed to submit timesheet.');
      }
    });
  }

  // ==========================================
  // 7. Modals: QR Code & Task Codes
  // ==========================================
  function openWorkerQR() {
    if (workerQRModal) workerQRModal.classList.remove('hidden');
  }
  window.openWorkerQR = openWorkerQR;

  function closeWorkerQRModal() {
    if (workerQRModal) workerQRModal.classList.add('hidden');
  }
  window.closeWorkerQRModal = closeWorkerQRModal;

  if (btnOpenWorkerQR) btnOpenWorkerQR.addEventListener('click', openWorkerQR);
  if (btnCloseWorkerQRModal) btnCloseWorkerQRModal.addEventListener('click', closeWorkerQRModal);

  function fallbackCopyText(text) {
    if (document.body && typeof document.body.appendChild === 'function') {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      if (typeof ta.focus === 'function') ta.focus();
      if (typeof ta.select === 'function') ta.select();
      try {
        if (typeof document.execCommand === 'function') document.execCommand('copy');
        if (btnCopyLinkModal) {
          btnCopyLinkModal.textContent = "Copied!";
          setTimeout(() => { if (btnCopyLinkModal) btnCopyLinkModal.textContent = "Copy Link"; }, 2000);
        }
      } catch (e) {
        prompt("Copy this URL:", text);
      }
      if (typeof document.body.removeChild === 'function') {
        document.body.removeChild(ta);
      }
    } else {
      prompt("Copy this URL:", text);
    }
  }

  if (btnCopyLinkModal) {
    btnCopyLinkModal.addEventListener('click', () => {
      const url = qrUrlTextModal ? qrUrlTextModal.textContent.trim() : (window.location.origin + '/m');
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(() => {
          btnCopyLinkModal.textContent = "Copied!";
          setTimeout(() => { if (btnCopyLinkModal) btnCopyLinkModal.textContent = "Copy Link"; }, 2000);
        }).catch(() => fallbackCopyText(url));
      } else {
        fallbackCopyText(url);
      }
    });
  }

  if (btnPrintQRModal) {
    btnPrintQRModal.addEventListener('click', () => {
      const qrSrc = qrImgModal ? qrImgModal.src : '';
      const qrUrl = qrUrlTextModal ? qrUrlTextModal.textContent : '';
      const win = window.open('', '_blank');
      if (!win) {
        alert('Popup blocker prevented opening print window. Please allow popups.');
        return;
      }
      win.document.write(`
        <html>
          <head><title>Print QR - AFCR Timesheet</title></head>
          <body style="text-align: center; font-family: sans-serif; padding: 40px;">
            <h2>AFFORDABLE FOOD CART RENTALS</h2>
            <h3>Daily Worker Timesheet Mobile Scanner</h3>
            <img src="${qrSrc}" style="width: 320px; height: 320px; margin: 20px 0;">
            <p style="font-size: 1.1rem; font-weight: bold;">${qrUrl}</p>
            <p>Scan with your smartphone camera while connected to company Wi-Fi.</p>
          </body>
        </html>
      `);
      win.document.close();
      win.focus();
      setTimeout(() => win.print(), 300);
    });
  }

  function openCodesModal() {
    renderCodesTable();
    if (taskCodesModal) taskCodesModal.classList.remove('hidden');
  }
  window.openCodesModal = openCodesModal;

  function closeCodesModal() {
    if (taskCodesModal) taskCodesModal.classList.add('hidden');
  }
  window.closeCodesModal = closeCodesModal;

  if (btnOpenCodesModal) btnOpenCodesModal.addEventListener('click', openCodesModal);
  if (btnCloseCodesModal) btnCloseCodesModal.addEventListener('click', closeCodesModal);

  // ==========================================
  // 8. Collapsible Scan Paper Card & OCR
  // ==========================================
  let lastToggleScanTime = 0;
  function toggleScanCard(e) {
    if (e && e.preventDefault) e.preventDefault();
    const now = Date.now();
    if (now - lastToggleScanTime < 300) return;
    lastToggleScanTime = now;

    if (!paperScanCard) return;
    paperScanCard.classList.toggle('hidden');
    if (!paperScanCard.classList.contains('hidden')) {
      paperScanCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
  window.toggleScanCard = toggleScanCard;

  function closeScanCard(e) {
    if (e && e.preventDefault) e.preventDefault();
    if (paperScanCard) paperScanCard.classList.add('hidden');
  }
  window.closeScanCard = closeScanCard;

  if (btnToggleScan) btnToggleScan.addEventListener('click', toggleScanCard);

  if (btnCloseScanCard) {
    btnCloseScanCard.addEventListener('click', closeScanCard);
  }

  if (desktopDropzone && desktopFileInput) {
    desktopDropzone.addEventListener('click', () => {
      if (desktopDropzone.querySelector('.ocr-loading-card')) return;
      desktopFileInput.click();
    });
  }

  if (desktopDropzone) {
    ['dragenter', 'dragover'].forEach(name => {
      desktopDropzone.addEventListener(name, (e) => {
        e.preventDefault();
        desktopDropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(name => {
      desktopDropzone.addEventListener(name, (e) => {
        e.preventDefault();
        desktopDropzone.classList.remove('dragover');
      });
    });

    desktopDropzone.addEventListener('drop', (e) => {
      if (e.dataTransfer && e.dataTransfer.files.length > 0) {
        handleDesktopUpload(e.dataTransfer.files[0]);
      }
    });
  }

  if (desktopFileInput) {
    desktopFileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleDesktopUpload(e.target.files[0]);
      }
    });
  }

  let modalPageUrls = [];
  let modalCurrentPageIndex = 0;

  let ocrProgressTimer = null;
  let ocrProgressPollTimer = null;

  function formatTimeDisplay(secs) {
    secs = Math.max(0, Math.round(secs));
    if (secs < 60) return `${secs}s`;
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return s > 0 ? `${m}m ${s}s` : `${m}m`;
  }

  async function getPdfPageCount(file) {
    try {
      const slice = file.slice(0, Math.min(file.size, 2097152));
      const text = await slice.text();
      const countMatch = text.match(/\/Count\s+(\d+)/);
      if (countMatch && countMatch[1]) {
        const c = parseInt(countMatch[1], 10);
        if (c > 0 && c < 500) return c;
      }
      const pageMatches = text.match(/\/Type\s*\/Page\b/g);
      if (pageMatches && pageMatches.length > 0) {
        return pageMatches.length;
      }
    } catch (e) {
      console.warn('Page count check notice:', e);
    }
    return Math.max(1, Math.round(file.size / 180000));
  }

  function startOCRProgress(options = {}) {
    const title = options.title || 'Analyzing Document with Neural OCR...';
    const totalPages = options.totalPages || 1;
    // Calibrated benchmark: ~8s per page with optimized handwriting OCR (~52s for 7 pages)
    const estimatedSecs = options.estimatedSecs || (totalPages > 1 ? Math.max(12, Math.round(totalPages * 8)) : 12);
    const startTime = Date.now();
    let currentServerPercent = 6;
    let currentRemaining = estimatedSecs;

    const stepsHtml = totalPages > 1 ? `
      <div class="ocr-step-item active" id="ocrStep1">
        <span class="ocr-step-dot"></span> 1. PDF Feeder Stack Conversion (${totalPages} Pages)
      </div>
      <div class="ocr-step-item" id="ocrStep2">
        <span class="ocr-step-dot"></span> 2. Neural OCR Across All ${totalPages} Pages (~8s/page)
      </div>
      <div class="ocr-step-item" id="ocrStep3">
        <span class="ocr-step-dot"></span> 3. Worker, Task Codes & Trailer Alignment
      </div>
      <div class="ocr-step-item" id="ocrStep4">
        <span class="ocr-step-dot"></span> 4. Break Deductions & Totals Audit
      </div>
    ` : `
      <div class="ocr-step-item active" id="ocrStep1">
        <span class="ocr-step-dot"></span> 1. Page Segmentation & Rendering
      </div>
      <div class="ocr-step-item" id="ocrStep2">
        <span class="ocr-step-dot"></span> 2. Worker, Cart & Date Alignment
      </div>
      <div class="ocr-step-item" id="ocrStep3">
        <span class="ocr-step-dot"></span> 3. Digit Box & Handwriting OCR
      </div>
      <div class="ocr-step-item" id="ocrStep4">
        <span class="ocr-step-dot"></span> 4. Break / Lunch Checkboxes & Totals
      </div>
    `;

    desktopDropzone.innerHTML = `
      <div class="ocr-loading-card">
        <div class="ocr-loading-header">
          <div class="ocr-spinner"></div>
          <div style="flex: 1;">
            <div class="ocr-loading-title">${title}</div>
            <div class="ocr-loading-phase" id="ocrPhaseText">Phase 1/4: Uploading & converting document...</div>
          </div>
        </div>

        <div class="ocr-progress-track">
          <div class="ocr-progress-fill" id="ocrProgressFill" style="width: 6%;"></div>
        </div>

        <div class="ocr-loading-meta">
          <div class="ocr-time-badge ocr-time-est">
            <span>⏳</span> Est. Remaining: <strong id="ocrSecsRemaining">~${formatTimeDisplay(estimatedSecs)}</strong>
          </div>
          <div class="ocr-time-badge ocr-time-elapsed">
            <span>⏱</span> Elapsed: <strong id="ocrSecsElapsed">0s</strong>
          </div>
          <div class="ocr-pct-badge" id="ocrPctBadge">6%</div>
        </div>

        <div class="ocr-live-steps">
          ${stepsHtml}
        </div>
      </div>
    `;

    if (ocrProgressTimer) clearInterval(ocrProgressTimer);
    if (ocrProgressPollTimer) clearInterval(ocrProgressPollTimer);

    ocrProgressTimer = setInterval(() => {
      const elapsed = (Date.now() - startTime) / 1000;
      const fill = document.getElementById('ocrProgressFill');
      const pctBadge = document.getElementById('ocrPctBadge');
      const remEl = document.getElementById('ocrSecsRemaining');
      const elapEl = document.getElementById('ocrSecsElapsed');
      const step1 = document.getElementById('ocrStep1');
      const step2 = document.getElementById('ocrStep2');
      const step3 = document.getElementById('ocrStep3');
      const step4 = document.getElementById('ocrStep4');

      if (!fill) return;

      // Realistic smooth curve that scales accurately with estimatedSecs
      const timeRatio = Math.min(1.0, elapsed / Math.max(1, estimatedSecs));
      let timePct = Math.round(6 + (88 * (1 - Math.exp(-2.5 * timeRatio))));

      let displayPct = Math.max(timePct, currentServerPercent);
      displayPct = Math.min(96, Math.max(6, displayPct));

      fill.style.width = `${displayPct}%`;
      if (pctBadge) pctBadge.textContent = `${displayPct}%`;
      if (remEl) remEl.textContent = `~${formatTimeDisplay(currentRemaining)}`;
      if (elapEl) elapEl.textContent = formatTimeDisplay(elapsed);

      // Countdown remaining time smoothly
      if (currentRemaining > 3) {
        currentRemaining = Math.max(3, Math.round(estimatedSecs - elapsed));
      }

      if (displayPct >= 15 && step1 && !step1.classList.contains('completed')) {
        step1.classList.remove('active');
        step1.classList.add('completed');
        if (step2) step2.classList.add('active');
      }
      if (displayPct >= 50 && step2 && !step2.classList.contains('completed')) {
        step2.classList.remove('active');
        step2.classList.add('completed');
        if (step3) step3.classList.add('active');
      }
      if (displayPct >= 80 && step3 && !step3.classList.contains('completed')) {
        step3.classList.remove('active');
        step3.classList.add('completed');
        if (step4) step4.classList.add('active');
      }
    }, 250);

    // Live backend page progress polling every 1200ms
    ocrProgressPollTimer = setInterval(async () => {
      try {
        const res = await fetch('/api/scan/progress');
        if (res.ok) {
          const prog = await res.json();
          if (prog && prog.active) {
            const phaseText = document.getElementById('ocrPhaseText');
            if (phaseText && prog.message) {
              phaseText.textContent = prog.message;
            }
            if (prog.percent > 0) {
              currentServerPercent = prog.percent;
            }
            if (prog.total_pages && prog.total_pages > 1 && prog.current_page > 0) {
              const elapsed = (Date.now() - startTime) / 1000;
              const avgPerPage = elapsed / Math.max(0.7, prog.current_page - 0.2);
              const pagesLeft = prog.total_pages - prog.current_page + 0.2;
              currentRemaining = Math.max(3, Math.round(avgPerPage * pagesLeft));
            }
          }
        }
      } catch (err) {}
    }, 1200);
  }

  function stopOCRProgress() {
    if (ocrProgressTimer) {
      clearInterval(ocrProgressTimer);
      ocrProgressTimer = null;
    }
    if (ocrProgressPollTimer) {
      clearInterval(ocrProgressPollTimer);
      ocrProgressPollTimer = null;
    }
    const fill = document.getElementById('ocrProgressFill');
    const pctBadge = document.getElementById('ocrPctBadge');
    const phaseText = document.getElementById('ocrPhaseText');
    const remEl = document.getElementById('ocrSecsRemaining');
    if (fill) fill.style.width = '100%';
    if (pctBadge) pctBadge.textContent = '100%';
    if (remEl) remEl.textContent = '0s';
    if (phaseText) phaseText.textContent = 'Complete! Loading verification window...';
  }

  if (btnRunTestScan) {
    btnRunTestScan.addEventListener('click', async () => {
      startOCRProgress({
        title: 'Running OCR on Israel Timesheet (Daily FC127)...',
        estimatedSecs: 10,
        totalPages: 1
      });

      try {
        const res = await fetch('/api/test-scan', { method: 'POST' });
        const data = await res.json();
        stopOCRProgress();
        setTimeout(() => {
          resetDropzone();
          displayVerificationModal(data);
        }, 350);
      } catch (e) {
        stopOCRProgress();
        resetDropzone();
        alert('Error running sample scan.');
      }
    });
  }

  const btnRunTestScanMT = document.getElementById('btnRunTestScanMT');
  if (btnRunTestScanMT) {
    btnRunTestScanMT.addEventListener('click', async () => {
      startOCRProgress({
        title: 'Scanning Sample MT Build Form (Frame Page 1)...',
        estimatedSecs: 12,
        totalPages: 1
      });

      try {
        const res = await fetch('/api/test-scan-mt', { method: 'POST' });
        const data = await res.json();
        stopOCRProgress();
        setTimeout(() => {
          resetDropzone();
          displayVerificationModal(data);
        }, 350);
      } catch (e) {
        stopOCRProgress();
        resetDropzone();
        alert('Error running MT sample scan.');
      }
    });
  }

  const btnInitCartMT = document.getElementById('btnInitCartMT');
  if (btnInitCartMT) {
    btnInitCartMT.addEventListener('click', async () => {
      if (!confirm(`Format and initialize ${activeCartTab} spreadsheet with all 96 standard MT manufacturing build codes organized by category?`)) {
        return;
      }
      try {
        const res = await fetch(`/api/cart/${activeCartTab}/init-mt`, { method: 'POST' });
        const d = await res.json();
        if (d.status === 'success') {
          showToast(`Formatted ${activeCartTab} with ${d.total_codes} MT build codes!`, 'success');
          loadCartData(activeCartTab);
        } else {
          alert(d.message || 'Failed to initialize cart.');
        }
      } catch (e) {
        alert('Error initializing cart with MT codes.');
      }
    });
  }

  const btnModalPrevPage = document.getElementById('btnModalPrevPage');
  const btnModalNextPage = document.getElementById('btnModalNextPage');
  if (btnModalPrevPage && btnModalNextPage) {
    btnModalPrevPage.addEventListener('click', () => {
      if (modalPageUrls.length > 1 && modalCurrentPageIndex > 0) {
        modalCurrentPageIndex--;
        updateModalPageDisplay();
      }
    });
    btnModalNextPage.addEventListener('click', () => {
      if (modalPageUrls.length > 1 && modalCurrentPageIndex < modalPageUrls.length - 1) {
        modalCurrentPageIndex++;
        updateModalPageDisplay();
      }
    });
  }

  function updateModalPageDisplay() {
    if (modalPageUrls.length > 0) {
      modalImgPreview.src = modalPageUrls[modalCurrentPageIndex];
    }
    const pager = document.getElementById('modalPageControls');
    const indicator = document.getElementById('modalPageIndicator');
    if (pager && indicator) {
      if (modalPageUrls.length > 1) {
        pager.style.display = 'flex';
        indicator.textContent = `Page ${modalCurrentPageIndex + 1} of ${modalPageUrls.length}`;
      } else {
        pager.style.display = 'none';
      }
    }
  }

  async function handleDesktopUpload(file) {
    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    let pageCount = 1;
    let estSecs = 12;

    if (isPdf) {
      pageCount = await getPdfPageCount(file);
      // Calibrated fast benchmark: ~8s per page (~52s for 7 pages)
      estSecs = Math.max(12, Math.round(pageCount * 8));
    } else if (file.size > 2500000) {
      estSecs = 15;
    }

    startOCRProgress({
      title: `Analyzing ${file.name}${pageCount > 1 ? ` (${pageCount} Pages)` : ''}...`,
      estimatedSecs: estSecs,
      totalPages: pageCount
    });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/scan', { method: 'POST', body: formData });
      const data = await res.json();
      stopOCRProgress();

      setTimeout(() => {
        resetDropzone();
        if (!res.ok || data.status !== 'success') {
          alert(data.message || 'Scanning failed.');
          return;
        }
        displayVerificationModal(data);
      }, 350);
    } catch (e) {
      stopOCRProgress();
      resetDropzone();
      alert('Could not connect to OCR service.');
    }
  }

  function resetDropzone() {
    if (!desktopDropzone) return;
    desktopDropzone.innerHTML = `
      <div class="dropzone-icon">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      </div>
      <div class="dropzone-text">Click or drag scanned timesheet document here</div>
      <div class="dropzone-sub">Supports multi-page PDF feeder stacks, PNG, JPG scanned pages. Automatically recognizes workers, tasks, hours & cart tabs!</div>
    `;
    if (desktopFileInput) desktopFileInput.value = '';
  }

  // ==========================================
  // 9. OCR Verification Modal
  // ==========================================
  function displayVerificationModal(data) {
    currentDesktopImageName = data.image_name || "";
    currentDesktopRawText = data.raw_text || "";
    modalPageUrls = data.page_urls || [data.image_url || ""];
    modalCurrentPageIndex = 0;
    updateModalPageDisplay();

    modalWorkerName.value = data.worker_name || "";
    modalDate.value = data.date || getTodayFormatted();
    modalRawText.textContent = data.raw_text || "(No raw OCR text)";

    const chkCount = data.checkbox_count || 0;
    modalCheckboxBadge.textContent = `${chkCount} Checkboxes Detected`;

    const rows = data.rows || [];
    const pageLabel = (data.total_pages && data.total_pages > 1) ? ` (${data.total_pages} Scanned Pages)` : '';
    modalRowCountBadge.textContent = `${rows.length} Tasks Extracted${pageLabel}`;

    renderModalRows(rows);
    recalcModalTotal();
    desktopVerifyModal.classList.remove('hidden');
  }

  function renderModalRows(rows) {
    modalRowsTableBody.innerHTML = '';
    rows.forEach(r => addModalRowToTable(r));
  }

  function addModalRowToTable(r = {}) {
    const tr = document.createElement('tr');
    tr.className = 'modal-task-row';

    const defaultCart = r.cart_id || (activeCartTab !== '__ALL__' ? activeCartTab : "FC127");
    const defaultType = r.type || "Build";
    const initialDuration = (r.time_in && r.time_out) ? calculateDuration(r.time_in, r.time_out) : (r.duration || '0:00:00');

    tr.innerHTML = `
      <td><input type="text" class="row-input-compact row-task" value="${escapeHtml(r.task || '')}" placeholder="Task description"></td>
      <td><input type="text" list="taskCodesDatalist" class="row-input-compact row-code" value="${escapeHtml(r.code || '')}" placeholder="e.g. S6" style="text-transform: uppercase;"></td>
      <td><input type="text" class="row-input-compact row-category" value="${escapeHtml(r.category || 'Misc.')}"></td>
      <td>
        <select class="row-input-compact row-type">
          <option value="Build" ${defaultType === 'Build' ? 'selected' : ''}>Build</option>
          <option value="Reconditioning" ${defaultType === 'Reconditioning' ? 'selected' : ''}>Reconditioning</option>
        </select>
      </td>
      <td><input type="text" class="row-input-compact row-timein" value="${escapeHtml(r.time_in || '08:00 AM')}" placeholder="e.g. 8:00 AM"></td>
      <td><input type="text" class="row-input-compact row-timeout" value="${escapeHtml(r.time_out || '12:00 PM')}" placeholder="e.g. 10:45 AM"></td>
      <td><input type="text" class="row-input-compact row-duration" value="${escapeHtml(initialDuration)}" readonly style="font-weight: 700; color: #047857; background-color: #f0fdf4; cursor: default;"></td>
      <td><input type="text" class="row-input-compact row-cart" value="${escapeHtml(defaultCart)}" style="font-weight: 600;"></td>
      <td style="text-align: center;"><button type="button" class="btn-remove-row" title="Delete Row">&times;</button></td>
    `;

    const codeInput = tr.querySelector('.row-code');
    if (codeInput) {
      codeInput.addEventListener('change', () => {
        const val = codeInput.value.trim().toUpperCase();
        const allCodes = [...(codesDatabase.mt_codes || []), ...(codesDatabase.rt_codes || [])];
        const match = allCodes.find(c => c.code.toUpperCase() === val);
        if (match) {
          const catEl = tr.querySelector('.row-category');
          if (catEl) catEl.value = match.category;
          const typeEl = tr.querySelector('.row-type');
          if (typeEl) typeEl.value = match.type;
          const taskInput = tr.querySelector('.row-task');
          if (taskInput && (!taskInput.value.trim() || taskInput.value === 'Task')) {
            taskInput.value = match.task;
          }
        }
      });
    }

    const timeInInput = tr.querySelector('.row-timein');
    const timeOutInput = tr.querySelector('.row-timeout');
    const durationInput = tr.querySelector('.row-duration');

    function updateRowDuration() {
      const allRows = modalRowsTableBody ? Array.from(modalRowsTableBody.querySelectorAll('.modal-task-row')) : [];
      const thisIdx = allRows.indexOf(tr);
      if (thisIdx > 0 && timeInInput && timeInInput.value.trim()) {
        const prevRow = allRows[thisIdx - 1];
        const prevTimeOut = prevRow ? prevRow.querySelector('.row-timeout') : null;
        if (prevTimeOut && !prevTimeOut.value.trim()) {
          prevTimeOut.value = timeInInput.value.trim();
          const prevTimeIn = prevRow.querySelector('.row-timein');
          const prevDur = prevRow.querySelector('.row-duration');
          if (prevTimeIn && prevDur) {
            prevDur.value = calculateDuration(prevTimeIn.value, prevTimeOut.value);
          }
        }
      }

      if (durationInput && timeInInput && timeOutInput) {
        durationInput.value = calculateDuration(timeInInput.value, timeOutInput.value);
      }
      recalcModalTotal();
    }

    if (timeInInput) {
      timeInInput.addEventListener('input', updateRowDuration);
      timeInInput.addEventListener('change', updateRowDuration);
    }
    if (timeOutInput) {
      timeOutInput.addEventListener('input', updateRowDuration);
      timeOutInput.addEventListener('change', updateRowDuration);
    }

    const removeBtn = tr.querySelector('.btn-remove-row');
    if (removeBtn) {
      removeBtn.addEventListener('click', () => {
        tr.remove();
        recalcModalTotal();
      });
    }

    if (modalRowsTableBody) {
      modalRowsTableBody.appendChild(tr);
    }
  }

  if (btnAddModalRow) {
    btnAddModalRow.addEventListener('click', () => {
      const allRows = modalRowsTableBody ? modalRowsTableBody.querySelectorAll('.modal-task-row') : [];
      let nextStart = "08:00 AM";
      if (allRows && allRows.length > 0) {
        const lastRow = allRows[allRows.length - 1];
        const lastTout = lastRow ? lastRow.querySelector('.row-timeout') : null;
        if (lastTout && lastTout.value && lastTout.value.trim()) {
          nextStart = lastTout.value.trim();
        }
      }

      addModalRowToTable({
        task: "",
        code: "",
        category: "Misc.",
        type: "Build",
        time_in: nextStart,
        time_out: "",
        duration: "0:00:00",
        cart_id: activeCartTab !== '__ALL__' ? activeCartTab : "FC127"
      });
      recalcModalTotal();
    });
  }

  function recalcModalTotal() {
    let totalMinutes = 0;
    const durInputs = modalRowsTableBody ? modalRowsTableBody.querySelectorAll('.row-duration') : [];
    durInputs.forEach(input => {
      const parts = input.value.split(':');
      if (parts.length >= 2) {
        const hrs = parseInt(parts[0]) || 0;
        const mins = parseInt(parts[1]) || 0;
        totalMinutes += (hrs * 60) + mins;
      }
    });

    const h = Math.floor(totalMinutes / 60);
    const m = totalMinutes % 60;
    if (modalTotalCalculatedHours) {
      modalTotalCalculatedHours.textContent = `${h}:${String(m).padStart(2, '0')}:00`;
    }
  }

  function closeModal() {
    if (desktopVerifyModal) desktopVerifyModal.classList.add('hidden');
  }

  if (btnCloseModal) btnCloseModal.addEventListener('click', closeModal);
  if (btnCancelModal) btnCancelModal.addEventListener('click', closeModal);

  if (btnSaveModal) {
    btnSaveModal.addEventListener('click', async () => {
      const rows = [];
      const trs = modalRowsTableBody ? modalRowsTableBody.querySelectorAll('.modal-task-row') : [];
      let hasValidationError = false;
      let errorMsg = "";

      trs.forEach((tr, idx) => {
        const taskEl = tr.querySelector('.row-task');
        const codeEl = tr.querySelector('.row-code');
        const catEl = tr.querySelector('.row-category');
        const typeEl = tr.querySelector('.row-type');
        const tinEl = tr.querySelector('.row-timein');
        const toutEl = tr.querySelector('.row-timeout');
        const durEl = tr.querySelector('.row-duration');
        const cartEl = tr.querySelector('.row-cart');

        const taskVal = taskEl ? taskEl.value.trim() : "";
        const codeVal = codeEl ? codeEl.value.trim().toUpperCase() : "";
        const catVal = catEl ? catEl.value.trim() : "Misc.";
        const typeVal = typeEl ? typeEl.value : "Build";
        const tinVal = tinEl ? tinEl.value.trim() : "";
        const toutVal = toutEl ? toutEl.value.trim() : "";
        const durVal = durEl ? durEl.value.trim() : "0:00:00";
        const cartVal = (cartEl && cartEl.value.trim()) || "FC127";

        if (!tinVal) {
          hasValidationError = true;
          errorMsg = `Row #${idx + 1} is missing a Start Time.`;
          if (tinEl && typeof tinEl.focus === 'function') tinEl.focus();
          return;
        }

        if (!toutVal) {
          hasValidationError = true;
          errorMsg = `Row #${idx + 1} is missing an End Time.`;
          if (toutEl && typeof toutEl.focus === 'function') toutEl.focus();
          return;
        }

        rows.push({
          task: taskVal || "General Work",
          code: codeVal,
          category: catVal || "Misc.",
        type: typeVal,
        time_in: tinVal,
        time_out: toutVal,
        duration: durVal || "0:00:00",
        cart_id: cartVal
      });
    });

    if (hasValidationError) {
      alert(`Validation Warning:\n${errorMsg}`);
      return;
    }

    if (rows.length === 0) {
      alert('Please add at least one task row.');
      return;
    }

    const workerNameVal = modalWorkerName.value.trim();
    if (!workerNameVal) {
      alert('Please enter or confirm the Worker Name.');
      modalWorkerName.focus();
      return;
    }

    const payload = {
      source: "Office Scanner",
      worker_name: workerNameVal,
      date: modalDate.value.trim() || getTodayFormatted(),
      rows: rows,
      image_name: currentDesktopImageName,
      raw_text: currentDesktopRawText
    };

    btnSaveModal.disabled = true;
    btnSaveModal.textContent = "Saving to Google Sheets & Excel...";

    try {
      const res = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await res.json();
      btnSaveModal.disabled = false;
      btnSaveModal.textContent = "Save & Sync to Google Sheets & Excel";

      if (res.ok && result.status === 'success') {
        closeModal();
        loadCartSummaries();
        loadCartData(activeCartTab !== '__ALL__' ? activeCartTab : "FC127");
        loadGoogleSheetsStatus();
        const tabsUpdated = (result.tabs_updated || []).join(', ');
        showToast(`✓ Successfully saved ${result.rows_saved} entries to [${tabsUpdated}]!`);
      } else {
        alert(result.message || 'Error saving timesheet.');
      }
    } catch (e) {
      btnSaveModal.disabled = false;
      btnSaveModal.textContent = "Save & Sync to Google Sheets & Excel";
      alert('Failed to submit timesheet.');
    }
  });
  }

  // ==========================================
  // 10. Google Sheets Integration Logic
  // ==========================================
  async function loadGoogleSheetsStatus() {
    try {
      const res = await fetch('/api/google-sheets/status');
      if (!res.ok) return;
      const data = await res.json();
      const dot = googleSheetsBadge ? googleSheetsBadge.querySelector('.sync-dot') : null;

      if (data.connected) {
        if (dot) dot.className = 'sync-dot connected';
        if (googleSheetsBadgeText) googleSheetsBadgeText.textContent = `Google Sheet: ${data.title || 'Connected'}`;
        if (gsheetStatusTitle) gsheetStatusTitle.textContent = `Google Sheet Connected: "${data.title}"`;
        if (gsheetStatusSub) gsheetStatusSub.textContent = `Live syncing to ${data.worksheets ? data.worksheets.length : '10+'} trailer tabs on Google Drive.`;
        if (googleSheetsBanner) googleSheetsBanner.classList.remove('warning');

        if (data.url && btnOpenSpreadsheetLink) {
          btnOpenSpreadsheetLink.href = data.url;
          btnOpenSpreadsheetLink.classList.remove('hidden');
        }
        if (btnSyncAllSheets) btnSyncAllSheets.classList.remove('hidden');
      } else {
        if (dot) dot.className = 'sync-dot warning';
        if (googleSheetsBadgeText) googleSheetsBadgeText.textContent = `Google Sheet: Setup Required`;
        if (gsheetStatusTitle) gsheetStatusTitle.textContent = "Google Sheets: Credentials Needed";
        if (gsheetStatusSub) gsheetStatusSub.textContent = data.error || "Click 'Configure' to connect your shared Google Sheet.";
        if (googleSheetsBanner) googleSheetsBanner.classList.add('warning');
        if (btnOpenSpreadsheetLink) btnOpenSpreadsheetLink.classList.add('hidden');
        if (btnSyncAllSheets) btnSyncAllSheets.classList.add('hidden');
      }

      if (data.settings) {
        if (settingSheetUrl) settingSheetUrl.value = data.settings.google_sheet_id_or_url || '';
        if (settingSheetTitle) settingSheetTitle.value = data.settings.google_sheet_title || 'FC TIMES_ FC121-130';
        if (settingSyncEnabled) settingSyncEnabled.checked = data.settings.google_sheets_enabled !== false;
        if (credsStatusText) {
          credsStatusText.textContent = data.settings.has_credentials ? "✓ Key file installed (google_credentials.json)" : "Missing key file";
          credsStatusText.style.color = data.settings.has_credentials ? "#15803d" : "#b45309";
        }
      }
    } catch (e) {
      console.warn("Could not check Google Sheets status:", e);
    }
  }

  function openGoogleSettings() {
    if (googleSettingsModal) googleSettingsModal.classList.remove('hidden');
    if (googleTestResultBox) googleTestResultBox.style.display = 'none';
  }
  window.openGoogleSettings = openGoogleSettings;
  window.openGoogleSettingsModal = openGoogleSettings;

  function closeGoogleSettings() {
    if (googleSettingsModal) googleSettingsModal.classList.add('hidden');
  }
  window.closeGoogleSettings = closeGoogleSettings;

  if (btnOpenGoogleSettings) btnOpenGoogleSettings.addEventListener('click', openGoogleSettings);
  if (btnConfigureGoogleSheets) btnConfigureGoogleSheets.addEventListener('click', openGoogleSettings);
  if (btnCheckGoogleSync) btnCheckGoogleSync.addEventListener('click', openGoogleSettings);

  if (btnCloseGoogleModal) btnCloseGoogleModal.addEventListener('click', closeGoogleSettings);
  if (btnCancelGoogleModal) btnCancelGoogleModal.addEventListener('click', closeGoogleSettings);

  if (btnSaveGoogleSettings) {
    btnSaveGoogleSettings.addEventListener('click', async () => {
      const payload = {
        google_sheet_id_or_url: settingSheetUrl ? settingSheetUrl.value.trim() : '',
        google_sheet_title: settingSheetTitle ? settingSheetTitle.value.trim() : 'FC TIMES_ FC121-130',
        google_sheets_enabled: settingSyncEnabled ? settingSyncEnabled.checked : true
      };

      try {
        const res = await fetch('/api/google-sheets/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          closeGoogleSettings();
          loadGoogleSheetsStatus();
          showToast('Google Sheets settings saved.');
        }
      } catch (e) {
        alert('Failed to save settings.');
      }
    });
  }

  if (btnTestGoogleConnection) {
    btnTestGoogleConnection.addEventListener('click', async () => {
      if (!googleTestResultBox) return;
      googleTestResultBox.style.display = 'block';
      googleTestResultBox.style.background = '#f1f5f9';
      googleTestResultBox.style.color = '#334155';
      googleTestResultBox.textContent = "Connecting to Google Cloud & reading spreadsheet...";

      try {
        if (settingSheetUrl && settingSheetUrl.value.trim()) {
          await fetch('/api/google-sheets/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              google_sheet_id_or_url: settingSheetUrl.value.trim(),
              google_sheets_enabled: settingSyncEnabled ? settingSyncEnabled.checked : true
            })
          });
        }

        const res = await fetch('/api/google-sheets/status');
        const data = await res.json();
        if (data.connected) {
          googleTestResultBox.style.background = '#f0fdf4';
          googleTestResultBox.style.color = '#15803d';
          googleTestResultBox.innerHTML = `
            <strong>✓ Connected Successfully!</strong><br>
            Title: ${escapeHtml(data.title)}<br>
            Tabs found: ${(data.worksheets || []).slice(0, 10).join(', ')}${(data.worksheets || []).length > 10 ? '...' : ''}
          `;
        } else {
          googleTestResultBox.style.background = '#fef2f2';
          googleTestResultBox.style.color = '#b91c1c';
          googleTestResultBox.innerHTML = `
            <strong>Connection Failed</strong><br>
            ${escapeHtml(data.error || 'Unknown error')}
          `;
        }
      } catch (e) {
        googleTestResultBox.style.background = '#fef2f2';
        googleTestResultBox.style.color = '#b91c1c';
        googleTestResultBox.textContent = `Error: ${e.message}`;
      }
    });
  }

  if (btnUploadCreds && credsFileInput) {
    btnUploadCreds.addEventListener('click', () => credsFileInput.click());
  }

  if (credsFileInput) {
    credsFileInput.addEventListener('change', async (e) => {
      const file = e.target.files ? e.target.files[0] : null;
      if (!file) return;

      const fd = new FormData();
      fd.append('file', file);
      if (credsStatusText) credsStatusText.textContent = "Uploading key...";

      try {
        const res = await fetch('/api/google-sheets/upload-credentials', {
          method: 'POST',
          body: fd
        });
        const data = await res.json();
        if (res.ok && data.status === 'success') {
          if (credsStatusText) {
            credsStatusText.textContent = "✓ Key uploaded successfully!";
            credsStatusText.style.color = "#15803d";
          }
          loadGoogleSheetsStatus();
        } else {
          alert(data.message || 'Upload failed.');
        }
      } catch (e) {
        alert('Upload error.');
      }
    });
  }

  // ==========================================
  // 11. Scans Folder & Utilities
  // ==========================================
  let isOpeningFolder = false;
  async function triggerScansFolder(e) {
    if (e && e.preventDefault) e.preventDefault();
    if (isOpeningFolder) return;
    isOpeningFolder = true;
    try {
      const res = await fetch('/api/open-folder', { method: 'POST' });
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        showToast('📂 Opened AFCR_Scans folder on Desktop', 'info');
      } else {
        alert('Could not open folder: ' + (data.message || 'Unknown error'));
      }
    } catch (e) {
      alert('Could not trigger desktop folder open.');
    } finally {
      setTimeout(() => { isOpeningFolder = false; }, 600);
    }
  }
  window.triggerScansFolder = triggerScansFolder;

  if (btnOpenFolder) {
    btnOpenFolder.addEventListener('click', triggerScansFolder);
  }

  function calculateDuration(tInStr, tOutStr) {
    function parseToMinutes(s) {
      if (!s) return null;
      s = s.toLowerCase().replace(/\s+/g, '');
      const isPm = s.includes('pm') || (s.includes('p') && !s.includes('am'));
      const isAm = s.includes('am');
      const clean = s.replace(/[^0-9:]/g, '');
      let hrs = 0, mins = 0;
      if (clean.includes(':')) {
        const p = clean.split(':');
        hrs = parseInt(p[0]) || 0;
        mins = parseInt(p[1]) || 0;
      } else if (clean.length >= 3) {
        hrs = parseInt(clean.slice(0, -2)) || 0;
        mins = parseInt(clean.slice(-2)) || 0;
      } else {
        hrs = parseInt(clean) || 0;
      }
      if (!isPm && !isAm) {
        if (hrs === 12 || (hrs >= 1 && hrs <= 5)) hrs += 12;
      } else {
        if (isPm && hrs < 12) hrs += 12;
        if (isAm && hrs === 12) hrs = 0;
      }
      return (hrs * 60) + mins;
    }

    const inMin = parseToMinutes(tInStr);
    const outMin = parseToMinutes(tOutStr);
    if (inMin === null || outMin === null) return "0:00:00";

    let diff = outMin - inMin;
    if (diff <= 0 && outMin < 720) {
      diff = (outMin + 720) - inMin;
    }
    if (diff < 0) diff += 1440;

    const hrs = Math.floor(diff / 60);
    const mins = diff % 60;
    return `${hrs}:${String(mins).padStart(2, '0')}:00`;
  }

  if (btnSyncAllSheets) {
    btnSyncAllSheets.addEventListener('click', async () => {
      if (!confirm('Sync all 11 Food Cart trailer tabs into your Google Sheet? This will make sure Google Sheets has all tabs and rows.')) return;
      btnSyncAllSheets.disabled = true;
      btnSyncAllSheets.innerHTML = '⏳ Syncing 11 tabs...';
      try {
        const res = await fetch('/api/google-sheets/sync-all', { method: 'POST' });
        const d = await res.json();
        if (d.status === 'success') {
          showToast(`✓ Successfully synced ${d.count} cart tabs to Google Sheets!`, 'success');
          loadGoogleSheetsStatus();
        } else {
          alert('Sync alert: ' + (d.errors || []).join('\n'));
        }
      } catch (e) {
        alert('Failed to sync all tabs: ' + e.message);
      } finally {
        btnSyncAllSheets.disabled = false;
        btnSyncAllSheets.innerHTML = '🔄 Push All Tabs to Sheet';
      }
    });
  }

  // ==========================================
  // Power-User Keyboard Shortcuts
  // ==========================================
  document.addEventListener('keydown', (e) => {
    // 1. Esc closes any active modal
    if (e.key === 'Escape') {
      const modals = [manualEntryModal, quickAddRowModal, editRowModal, desktopVerifyModal, googleSettingsModal, workerQRModal, taskCodesModal];
      modals.forEach(m => {
        if (m && !m.classList.contains('hidden')) {
          m.classList.add('hidden');
        }
      });
      return;
    }

    // 2. Ctrl+Enter or Cmd+Enter submits the open modal
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      if (manualEntryModal && !manualEntryModal.classList.contains('hidden')) {
        e.preventDefault();
        btnSaveManualModal.click();
        return;
      }
      if (quickAddRowModal && !quickAddRowModal.classList.contains('hidden')) {
        e.preventDefault();
        btnSaveQuickAddRow.click();
        return;
      }
      if (editRowModal && !editRowModal.classList.contains('hidden')) {
        e.preventDefault();
        btnSaveEditRow.click();
        return;
      }
      if (desktopVerifyModal && !desktopVerifyModal.classList.contains('hidden')) {
        e.preventDefault();
        btnSaveModal.click();
        return;
      }
    }

    // 3. Alt+N opens "Enter Timesheet (By Hand)"
    if (e.altKey && (e.key === 'n' || e.key === 'N')) {
      e.preventDefault();
      if (btnOpenManualModal) btnOpenManualModal.click();
      return;
    }

    // 4. "/" focuses the trailer rows search bar when not typing
    if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
      e.preventDefault();
      if (cartFilterSearch) {
        cartFilterSearch.focus();
        cartFilterSearch.select();
      }
      return;
    }
  });

  // ==========================================
  // 12. Team Roster & Trailer Tabs Management
  // ==========================================
  function openRosterModal() {
    renderRosterManager();
    if (teamTrailersModal) teamTrailersModal.classList.remove('hidden');
  }
  window.openRosterModal = openRosterModal;

  function closeRosterModal() {
    if (teamTrailersModal) teamTrailersModal.classList.add('hidden');
  }
  window.closeRosterModal = closeRosterModal;

  if (btnOpenRosterModal) {
    btnOpenRosterModal.addEventListener('click', openRosterModal);
  }

  if (btnCloseRosterModal) btnCloseRosterModal.addEventListener('click', closeRosterModal);
  if (btnCloseRosterModalBottom) btnCloseRosterModalBottom.addEventListener('click', closeRosterModal);

  if (tabRosterWorkers && tabRosterTrailers) {
    tabRosterWorkers.addEventListener('click', () => {
      tabRosterWorkers.classList.add('gs-wizard-tab-active');
      tabRosterWorkers.style.fontWeight = '700';
      tabRosterWorkers.style.color = 'var(--brand-navy)';
      tabRosterTrailers.classList.remove('gs-wizard-tab-active');
      tabRosterTrailers.style.fontWeight = '600';
      tabRosterTrailers.style.color = 'var(--text-secondary)';
      if (paneWorkers) paneWorkers.style.display = '';
      if (paneTrailers) paneTrailers.style.display = 'none';
    });

    tabRosterTrailers.addEventListener('click', () => {
      tabRosterTrailers.classList.add('gs-wizard-tab-active');
      tabRosterTrailers.style.fontWeight = '700';
      tabRosterTrailers.style.color = 'var(--brand-navy)';
      tabRosterWorkers.classList.remove('gs-wizard-tab-active');
      tabRosterWorkers.style.fontWeight = '600';
      tabRosterWorkers.style.color = 'var(--text-secondary)';
      if (paneTrailers) paneTrailers.style.display = '';
      if (paneWorkers) paneWorkers.style.display = 'none';
    });
  }

  function renderRosterManager() {
    const workers = activeWorkers || [];
    const trailers = configuredCartTabs || [];
    if (workerCountBadge) workerCountBadge.textContent = workers.length;
    if (trailerCountBadge) trailerCountBadge.textContent = trailers.length;

    if (rosterBadgesList) {
      rosterBadgesList.innerHTML = workers.map(w => {
        return `<span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: white; border: 1px solid var(--border); border-radius: 20px; font-size: 0.82rem; font-weight: 600; color: var(--brand-navy);">
          ${escapeHtml(w)}
          <button type="button" data-del-worker="${escapeHtml(w)}" style="background: none; border: none; cursor: pointer; color: #ef4444; font-weight: 700; padding: 0 2px;">&times;</button>
        </span>`;
      }).join('');

      rosterBadgesList.querySelectorAll('[data-del-worker]').forEach(btn => {
        btn.addEventListener('click', async (e) => {
          const name = e.currentTarget.getAttribute('data-del-worker');
          if (confirm(`Remove "${name}" from worker roster?`)) {
            await deleteWorkerFromRoster(name);
          }
        });
      });
    }

    if (trailerBadgesList) {
      trailerBadgesList.innerHTML = trailers.map(t => {
        return `<span style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: white; border: 1px solid var(--border); border-radius: 20px; font-size: 0.82rem; font-weight: 600; color: var(--brand-navy);">
          ${escapeHtml(t)}
          <button type="button" data-del-trailer="${escapeHtml(t)}" style="background: none; border: none; cursor: pointer; color: #ef4444; font-weight: 700; padding: 0 2px;" title="Remove trailer">&times;</button>
        </span>`;
      }).join('');

      trailerBadgesList.querySelectorAll('[data-del-trailer]').forEach(btn => {
        btn.addEventListener('click', async (e) => {
          const tab = e.currentTarget.getAttribute('data-del-trailer');
          if (confirm(`Remove "${tab}" from trailer tabs?`)) {
            await deleteTrailerTab(tab);
          }
        });
      });
    }
  }

  if (btnAddWorkerBtn && inputNewWorkerName) {
    btnAddWorkerBtn.addEventListener('click', async () => {
      const name = inputNewWorkerName.value.trim();
      if (!name) return;
      try {
        const res = await fetch('/api/workers', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name })
        });
        const data = await res.json();
        if (res.ok && data.status === 'success') {
          activeWorkers = data.workers || [];
          inputNewWorkerName.value = '';
          renderWorkerChips(activeWorkers);
          renderRosterManager();
          showToast(`✓ Added ${name} to team roster!`);
        } else {
          alert(data.message || 'Could not add worker');
        }
      } catch (err) {
        alert('Network error adding worker');
      }
    });
    inputNewWorkerName.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        btnAddWorkerBtn.click();
      }
    });
  }

  async function deleteWorkerFromRoster(name) {
    try {
      const res = await fetch('/api/workers', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        activeWorkers = data.workers || [];
        renderWorkerChips(activeWorkers);
        renderRosterManager();
        showToast(`✓ Removed ${name} from roster`);
      } else {
        alert(data.message || 'Could not remove worker');
      }
    } catch (err) {
      alert('Network error removing worker');
    }
  }

  async function createTrailerTab(rawName) {
    const cart_id = String(rawName || '').trim();
    if (!cart_id) return;
    try {
      const res = await fetch('/api/carts/tabs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cart_id })
      });
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        configuredCartTabs = data.cart_tabs || [];
        populateCartSelects();
        renderRosterManager();
        loadCartSummaries();
        switchCartTab(data.cart_id);
        showToast(`✓ Created trailer tab ${data.cart_id}!`);
      } else {
        alert(data.message || 'Could not create trailer tab');
      }
    } catch (err) {
      alert('Network error creating trailer tab');
    }
  }

  if (btnAddTrailerBtn && inputNewTrailerName) {
    btnAddTrailerBtn.addEventListener('click', async () => {
      const name = inputNewTrailerName.value.trim();
      if (!name) return;
      await createTrailerTab(name);
      inputNewTrailerName.value = '';
    });
    inputNewTrailerName.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        btnAddTrailerBtn.click();
      }
    });
  }

  let isPromptingTrailerTab = false;
  async function quickAddTrailerTabPrompt(e) {
    if (e && e.preventDefault) e.preventDefault();
    if (isPromptingTrailerTab) return;
    isPromptingTrailerTab = true;
    try {
      const promptName = prompt('Enter new Food Cart / Trailer number (e.g. FC131):');
      if (promptName && promptName.trim()) {
        await createTrailerTab(promptName.trim());
      }
    } finally {
      setTimeout(() => { isPromptingTrailerTab = false; }, 400);
    }
  }
  window.quickAddTrailerTabPrompt = quickAddTrailerTabPrompt;

  if (btnQuickAddTrailerTab) {
    btnQuickAddTrailerTab.addEventListener('click', quickAddTrailerTabPrompt);
  }

  async function deleteTrailerTab(tabName) {
    try {
      const res = await fetch('/api/carts/tabs', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cart_id: tabName })
      });
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        configuredCartTabs = data.cart_tabs || [];
        populateCartSelects();
        renderRosterManager();
        loadCartSummaries();
        if (activeCartTab === tabName) {
          switchCartTab(configuredCartTabs[0] || 'FC127');
        }
        showToast(`✓ Removed trailer tab ${tabName}`);
      } else {
        alert(data.message || 'Could not remove trailer tab');
      }
    } catch (err) {
      alert('Network error removing trailer tab');
    }
  }

  // ==========================================
  // 13. Feedback & Daily Notes for Dale
  // ==========================================
  const feedbackModal = document.getElementById('feedbackModal');
  const btnOpenFeedbackModal = document.getElementById('btnOpenFeedbackModal');
  const btnCloseFeedbackModal = document.getElementById('btnCloseFeedbackModal');
  const btnCancelFeedbackModal = document.getElementById('btnCancelFeedbackModal');
  const btnSaveFeedbackOnly = document.getElementById('btnSaveFeedbackOnly');
  const btnSendFeedbackEmail = document.getElementById('btnSendFeedbackEmail');
  const feedbackSender = document.getElementById('feedbackSender');
  const feedbackSubject = document.getElementById('feedbackSubject');
  const feedbackMessage = document.getElementById('feedbackMessage');

  let lastFeedbackOpenTime = 0;
  function openFeedbackModal(e) {
    if (e && e.preventDefault) e.preventDefault();
    const now = Date.now();
    if (now - lastFeedbackOpenTime < 300) return;
    lastFeedbackOpenTime = now;

    if (feedbackModal) {
      feedbackModal.classList.remove('hidden');
      if (feedbackMessage) feedbackMessage.focus();
    }
  }
  window.openFeedbackModal = openFeedbackModal;

  function closeFeedbackModal() {
    if (feedbackModal) feedbackModal.classList.add('hidden');
  }
  window.closeFeedbackModal = closeFeedbackModal;

  if (btnOpenFeedbackModal) btnOpenFeedbackModal.addEventListener('click', openFeedbackModal);
  if (btnCloseFeedbackModal) btnCloseFeedbackModal.addEventListener('click', closeFeedbackModal);
  if (btnCancelFeedbackModal) btnCancelFeedbackModal.addEventListener('click', closeFeedbackModal);

  async function submitFeedback(sendEmail) {
    const author = (feedbackSender ? feedbackSender.value : 'Elijah').trim() || 'Elijah';
    const subject = (feedbackSubject ? feedbackSubject.value : 'AFCR Timesheet Notes').trim() || 'AFCR Timesheet Notes';
    const message = (feedbackMessage ? feedbackMessage.value : '').trim();

    if (!message) {
      alert('Please enter your notes or feedback before sending.');
      if (feedbackMessage) feedbackMessage.focus();
      return;
    }

    const fullMessage = `Subject: ${subject}\n\n${message}`;

    // 1. Always save a copy to the server logs
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ author, message: fullMessage })
      });
    } catch (err) {
      console.warn('Feedback server save warning:', err);
    }

    // 2. If email requested, open email client to dalefaubion@gmail.com
    if (sendEmail) {
      const emailTo = 'dalefaubion@gmail.com';
      const emailSubject = encodeURIComponent(`[AFCR Notes] ${subject} (from ${author})`);
      const emailBody = encodeURIComponent(
        `Hi Dale,\n\nHere are timesheet / cart notes from ${author}:\n\n` +
        `----------------------------------------\n` +
        `${message}\n` +
        `----------------------------------------\n\n` +
        `Sent from AFCR Timesheet Portal (${new Date().toLocaleString()})`
      );

      const mailtoUrl = `mailto:${emailTo}?subject=${emailSubject}&body=${emailBody}`;
      
      // Try opening mailto link
      window.location.href = mailtoUrl;

      showToast(`✉️ Email opened for Dale! (and note saved locally)`);
    } else {
      showToast(`💾 Note saved to server for Dale!`);
    }

    if (feedbackMessage) feedbackMessage.value = '';
    closeFeedbackModal();
  }

  if (btnSaveFeedbackOnly) {
    btnSaveFeedbackOnly.addEventListener('click', () => submitFeedback(false));
  }
  if (btnSendFeedbackEmail) {
    btnSendFeedbackEmail.addEventListener('click', () => submitFeedback(true));
  }

  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
});

