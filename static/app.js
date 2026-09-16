/**
 * QuantRebalance | Frontend Engine & Dashboard Application Logic
 */

let state = {
  holdings: [],
  metrics: {},
  strategies: {},
  rebalancePlan: null,
  activeView: 'view-holdings',
  activeCategory: 'all',
  searchQuery: '',
  sortOrder: 'val-desc',
  rebalanceParams: {
    strategy_key: 'core_satellite',
    rebalance_mode: 'smart_inflow',
    fresh_capital: 0,
    tolerance_band: 3.0
  },
  charts: {
    allocation: null,
    drift: null,
    deepdive: null
  }
};

// Currency & number formatting helpers
function formatINR(val, decimals = 0) {
  if (val === null || val === undefined || isNaN(val)) return '₹0';
  const num = Number(val);
  const fixed = num.toLocaleString('en-IN', {
    maximumFractionDigits: decimals,
    minimumFractionDigits: decimals
  });
  return '₹' + fixed;
}

function formatPct(val, withPlus = false) {
  if (val === null || val === undefined || isNaN(val)) return '0.0%';
  const num = Number(val);
  const prefix = (withPlus && num > 0) ? '+' : '';
  return prefix + num.toFixed(2) + '%';
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  fetchPortfolioData();
});

// Setup DOM Event Listeners
function setupEventListeners() {
  // Navigation Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetView = btn.dataset.view;
      switchView(targetView);
    });
  });

  // Category Filter Chips
  document.querySelectorAll('.category-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.category-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      state.activeCategory = chip.dataset.category;
      renderHoldingsTable();
    });
  });

  // Search Input
  const searchInput = document.getElementById('holding-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value.toLowerCase().trim();
      renderHoldingsTable();
    });
  }

  // Sort Select
  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      state.sortOrder = e.target.value;
      renderHoldingsTable();
    });
  }

  // Refresh Market Data Button
  const btnRefresh = document.getElementById('btn-refresh-data');
  if (btnRefresh) {
    btnRefresh.addEventListener('click', () => {
      btnRefresh.classList.add('spinning');
      fetchPortfolioData(true);
    });
  }

  // Strategy Selector Cards
  document.querySelectorAll('.strategy-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.strategy-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      state.rebalanceParams.strategy_key = card.dataset.strategy;
      runRebalanceSimulation();
    });
  });

  // Mode Toggle
  const btnModeSmart = document.getElementById('btn-mode-smart');
  const btnModeFull = document.getElementById('btn-mode-full');
  if (btnModeSmart && btnModeFull) {
    btnModeSmart.addEventListener('click', () => {
      btnModeSmart.classList.add('active');
      btnModeFull.classList.remove('active');
      state.rebalanceParams.rebalance_mode = 'smart_inflow';
      runRebalanceSimulation();
    });
    btnModeFull.addEventListener('click', () => {
      btnModeFull.classList.add('active');
      btnModeSmart.classList.remove('active');
      state.rebalanceParams.rebalance_mode = 'full_rebalance';
      runRebalanceSimulation();
    });
  }

  // Fresh Capital Slider
  const sliderCapital = document.getElementById('slider-fresh-capital');
  const lblCapital = document.getElementById('lbl-fresh-capital');
  if (sliderCapital && lblCapital) {
    sliderCapital.addEventListener('input', (e) => {
      const val = Number(e.target.value);
      state.rebalanceParams.fresh_capital = val;
      lblCapital.textContent = formatINR(val);
    });
    sliderCapital.addEventListener('change', () => {
      runRebalanceSimulation();
    });
  }

  // Tolerance Slider
  const sliderTol = document.getElementById('slider-tolerance');
  const lblTol = document.getElementById('lbl-tolerance');
  if (sliderTol && lblTol) {
    sliderTol.addEventListener('input', (e) => {
      const val = Number(e.target.value);
      state.rebalanceParams.tolerance_band = val;
      lblTol.textContent = `±${val.toFixed(1)}%`;
    });
    sliderTol.addEventListener('change', () => {
      runRebalanceSimulation();
    });
  }

  // Rebalance Button
  const btnRebal = document.getElementById('btn-calculate-rebalance');
  if (btnRebal) {
    btnRebal.addEventListener('click', () => runRebalanceSimulation());
  }

  // Copy Orders Button
  const btnCopyOrders = document.getElementById('btn-copy-orders');
  if (btnCopyOrders) {
    btnCopyOrders.addEventListener('click', copyOrdersToClipboard);
  }

  // Export Orders CSV Button
  const btnExportCSV = document.getElementById('btn-export-orders-csv');
  if (btnExportCSV) {
    btnExportCSV.addEventListener('click', exportOrdersToCSV);
  }

  // Upload Modal triggers
  const btnOpenUpload = document.getElementById('btn-open-upload-modal');
  const uploadModal = document.getElementById('upload-modal');
  const uploadClose = document.getElementById('upload-modal-close-btn');
  if (btnOpenUpload && uploadModal) {
    btnOpenUpload.addEventListener('click', () => uploadModal.classList.add('open'));
    uploadClose.addEventListener('click', () => uploadModal.classList.remove('open'));
  }

  // Deep Dive Modal close
  const deepModal = document.getElementById('deepdive-modal');
  const deepClose = document.getElementById('modal-close-btn');
  if (deepModal && deepClose) {
    deepClose.addEventListener('click', () => deepModal.classList.remove('open'));
  }

  // Dropzone handling
  const dropzone = document.getElementById('csv-dropzone');
  const fileInput = document.getElementById('csv-file-input');
  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        uploadCSVFile(e.dataTransfer.files[0]);
      }
    });
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        uploadCSVFile(e.target.files[0]);
      }
    });
  }

  // Sample Load Button
  const btnLoadSample = document.getElementById('btn-load-sample');
  if (btnLoadSample) {
    btnLoadSample.addEventListener('click', () => {
      fetchPortfolioData(true);
      if (uploadModal) uploadModal.classList.remove('open');
      showToast('Sample 22-holding portfolio loaded & synchronized!', 'success');
    });
  }
}

// Switch View Tabs
function switchView(viewId) {
  state.activeView = viewId;
  document.querySelectorAll('.tab-btn').forEach(btn => {
    const isMatch = btn.dataset.view === viewId;
    btn.classList.toggle('active', isMatch);
    btn.setAttribute('aria-selected', isMatch ? 'true' : 'false');
  });

  document.querySelectorAll('.view-content').forEach(view => {
    view.classList.toggle('active', view.id === viewId);
  });

  if (viewId === 'view-allocation') {
    renderAllocationCharts();
  }
}

// Fetch Portfolio Data from Backend API
async function fetchPortfolioData(forceRefresh = false) {
  try {
    const btnRefresh = document.getElementById('btn-refresh-data');
    const url = `/api/portfolio${forceRefresh ? '?refresh=true' : ''}`;
    const res = await fetch(url);
    const data = await res.json();

    if (btnRefresh) btnRefresh.classList.remove('spinning');

    if (!data.success) {
      showToast(data.error || 'Failed to fetch portfolio', 'error');
      return;
    }

    state.holdings = data.holdings || [];
    state.metrics = data.metrics || {};
    state.strategies = data.strategies || {};

    if (data.last_synced) {
      const syncEl = document.getElementById('last-sync-time');
      if (syncEl) syncEl.innerHTML = `<span>Synced: ${data.last_synced}</span>`;
    }

    updateKPICards();
    renderHoldingsTable();
    runRebalanceSimulation();

    if (forceRefresh) {
      showToast('Real-time prices and analyst data updated!', 'success');
    }
  } catch (err) {
    console.error('Error fetching portfolio:', err);
    showToast('Failed to connect to backend server', 'error');
    const btnRefresh = document.getElementById('btn-refresh-data');
    if (btnRefresh) btnRefresh.classList.remove('spinning');
  }
}

// Update Top KPI Cards
function updateKPICards() {
  const m = state.metrics;
  if (!m) return;

  const totalValEl = document.getElementById('kpi-total-val');
  const dayPnlEl = document.getElementById('kpi-day-pnl');
  const dayBadgeEl = document.getElementById('kpi-day-badge');
  const pnlValEl = document.getElementById('kpi-pnl-val');
  const pnlPctEl = document.getElementById('kpi-pnl-pct');
  const investedValEl = document.getElementById('kpi-invested-val');
  const bufferValEl = document.getElementById('kpi-buffer-val');
  const bufferBadgeEl = document.getElementById('kpi-buffer-badge');
  const scoreValEl = document.getElementById('kpi-score-val');
  const countBadge = document.getElementById('holdings-count-badge');

  if (totalValEl) totalValEl.textContent = formatINR(m.total_current_value);
  if (dayPnlEl) dayPnlEl.textContent = `${formatINR(m.day_pnl, 0)} today`;
  if (dayBadgeEl) {
    dayBadgeEl.textContent = formatPct(m.day_pnl_pct, true) + ' Today';
    dayBadgeEl.className = `kpi-badge ${m.day_pnl >= 0 ? 'badge-success' : 'badge-danger'}`;
  }

  if (pnlValEl) {
    pnlValEl.textContent = `${m.total_pnl >= 0 ? '+' : ''}${formatINR(m.total_pnl)}`;
    pnlValEl.className = `kpi-main-number ${m.total_pnl >= 0 ? 'text-success' : 'text-danger'}`;
  }
  if (pnlPctEl) {
    pnlPctEl.textContent = formatPct(m.total_pnl_pct, true) + ' Net';
    pnlPctEl.className = `kpi-badge ${m.total_pnl_pct >= 0 ? 'badge-success' : 'badge-danger'}`;
  }
  if (investedValEl) investedValEl.textContent = formatINR(m.total_invested);

  // Arbitrage Buffer
  const arbData = (m.class_breakdown || {})['Arbitrage / Cash'] || {};
  const arbVal = arbData.value || 0;
  const arbPct = arbData.weight_pct || 0;
  if (bufferValEl) bufferValEl.textContent = formatINR(arbVal);
  if (bufferBadgeEl) bufferBadgeEl.textContent = `${arbPct}% Buffer`;

  // Average Conviction Score
  const scores = state.holdings
    .map(h => (h.analysis || {}).composite_score)
    .filter(s => typeof s === 'number');
  const avgScore = scores.length > 0 ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : '70.0';
  if (scoreValEl) scoreValEl.innerHTML = `${avgScore} <span class="score-den">/ 100</span>`;

  if (countBadge) countBadge.textContent = state.holdings.length;
}

// Render Holdings Table
function renderHoldingsTable() {
  const tbody = document.getElementById('holdings-table-body');
  if (!tbody) return;

  // Filter
  let list = state.holdings.filter(h => {
    // Category filter
    if (state.activeCategory !== 'all') {
      if (h.asset_class !== state.activeCategory) return false;
    }
    // Search filter
    if (state.searchQuery) {
      const q = state.searchQuery;
      const matchInst = (h.instrument || '').toLowerCase().includes(q);
      const matchSub = (h.sub_class || '').toLowerCase().includes(q);
      const matchCat = (h.asset_class || '').toLowerCase().includes(q);
      const matchTick = (h.ticker || '').toLowerCase().includes(q);
      if (!matchInst && !matchSub && !matchCat && !matchTick) return false;
    }
    return true;
  });

  // Sort
  list.sort((a, b) => {
    switch (state.sortOrder) {
      case 'val-desc': return (b.current_value || 0) - (a.current_value || 0);
      case 'val-asc': return (a.current_value || 0) - (b.current_value || 0);
      case 'pnl-desc': return (b.net_chg || 0) - (a.net_chg || 0);
      case 'pnl-asc': return (a.net_chg || 0) - (b.net_chg || 0);
      case 'score-desc': return ((b.analysis || {}).composite_score || 0) - ((a.analysis || {}).composite_score || 0);
      case 'day-desc': return (b.day_chg || 0) - (a.day_chg || 0);
      case 'name-asc': return a.instrument.localeCompare(b.instrument);
      default: return 0;
    }
  });

  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="11" class="text-center text-muted" style="padding: 2.5rem;">No matching holdings found.</td></tr>`;
    return;
  }

  tbody.innerHTML = list.map(h => {
    const analysis = h.analysis || {};
    const tech = h.technical || {};
    const fund = h.fundamental || {};
    const score = analysis.composite_score || 50;

    let recBadgeClass = 'badge-neutral';
    if (analysis.recommendation === 'STRONG BUY') recBadgeClass = 'badge-success';
    else if (analysis.recommendation === 'ACCUMULATE') recBadgeClass = 'badge-info';
    else if (analysis.recommendation === 'TRIM / REBALANCE') recBadgeClass = 'badge-danger';
    else if (analysis.recommendation === 'HOLD') recBadgeClass = 'badge-neutral';

    let scoreColor = 'text-info';
    if (score >= 75) scoreColor = 'text-success';
    else if (score >= 60) scoreColor = 'text-gold';
    else if (score <= 40) scoreColor = 'text-danger';

    const pnlClass = h.pnl >= 0 ? 'text-success' : 'text-danger';
    const dayPnlClass = h.day_chg >= 0 ? 'text-success' : 'text-danger';

    return `
      <tr>
        <td>
          <div class="instrument-cell">
            <span class="inst-name">${h.instrument}</span>
            <span class="inst-sub">${h.sub_class || h.asset_class}</span>
          </div>
        </td>
        <td class="text-right mono-num">${Number(h.quantity).toLocaleString('en-IN', { maximumFractionDigits: 3 })}</td>
        <td class="text-right mono-num">₹${Number(h.avg_cost).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
        <td class="text-right mono-num">
          <strong>₹${Number(h.live_price || h.ltp).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong>
          <div class="inst-sub ${dayPnlClass}">${formatPct(h.day_chg, true)}</div>
        </td>
        <td class="text-right mono-num"><strong>${formatINR(h.current_value)}</strong></td>
        <td class="text-right mono-num">
          <span class="${pnlClass}"><strong>${h.pnl >= 0 ? '+' : ''}${formatINR(h.pnl)}</strong></span>
          <div class="inst-sub ${pnlClass}">(${formatPct(h.net_chg, true)})</div>
        </td>
        <td class="text-center">
          <span style="font-size: 0.78rem; font-weight: 600;">${tech.trend || 'Consolidating'}</span>
          ${tech.rsi14 ? `<div class="inst-sub">RSI: <strong>${tech.rsi14}</strong></div>` : ''}
        </td>
        <td class="text-center">
          ${analysis.target_1 ? `<div>T1: <strong>₹${Number(analysis.target_1).toLocaleString('en-IN')}</strong></div>` : '-'}
          ${analysis.upside_pct ? `<div class="inst-sub text-success">+${analysis.upside_pct}% Upside</div>` : ''}
        </td>
        <td class="text-center">
          <span class="mono-num ${scoreColor}" style="font-weight: 700; font-size: 0.95rem;">${score}</span>
        </td>
        <td class="text-center">
          <span class="badge ${recBadgeClass}">${analysis.recommendation || 'HOLD'}</span>
        </td>
        <td class="text-center">
          <button class="btn btn-secondary btn-sm" onclick="openDeepDive('${h.instrument}')">
            <span>Analyze</span>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

// Run Rebalance Simulation
async function runRebalanceSimulation() {
  try {
    const res = await fetch('/api/rebalance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state.rebalanceParams)
    });
    const data = await res.json();
    if (!data.success) {
      showToast(data.error || 'Simulation failed', 'error');
      return;
    }

    state.rebalancePlan = data.plan;
    renderDriftMatrix();
    renderOrdersSheet();
    if (state.activeView === 'view-allocation') {
      renderAllocationCharts();
    }
  } catch (err) {
    console.error('Simulation error:', err);
  }
}

// Render Asset Class Drift Table
function renderDriftMatrix() {
  const tbody = document.getElementById('drift-table-body');
  if (!tbody || !state.rebalancePlan) return;

  const driftData = state.rebalancePlan.class_drift || {};
  tbody.innerHTML = Object.entries(driftData).map(([className, d]) => {
    const driftSign = d.drift_pct > 0 ? '+' : '';
    const driftColor = d.drift_pct > 0 ? 'text-danger' : (d.drift_pct < 0 ? 'text-success' : 'text-muted');

    let statusBadge = 'badge-neutral';
    if (d.status === 'Within Tolerance') statusBadge = 'badge-success';
    else if (d.status === 'Underweight') statusBadge = 'badge-info';
    else if (d.status === 'Overweight') statusBadge = 'badge-danger';

    return `
      <tr>
        <td><strong>${className}</strong></td>
        <td class="text-right mono-num">${formatINR(d.current_value)}</td>
        <td class="text-right mono-num">${d.current_weight_pct.toFixed(2)}%</td>
        <td class="text-right mono-num" style="color: var(--accent-cyan);"><strong>${d.target_weight_pct.toFixed(2)}%</strong></td>
        <td class="text-right mono-num">${formatINR(d.target_value)}</td>
        <td class="text-right mono-num ${driftColor}">
          <strong>${driftSign}${d.drift_pct.toFixed(2)}%</strong>
          <div class="inst-sub">(${driftSign}${formatINR(d.drift_value)})</div>
        </td>
        <td class="text-center">
          <span class="badge ${statusBadge}">${d.status}</span>
        </td>
        <td class="text-center">
          <strong>${d.action}</strong>
        </td>
      </tr>
    `;
  }).join('');
}

// Render Execution Order Sheet
function renderOrdersSheet() {
  const tbody = document.getElementById('orders-table-body');
  const kpiContainer = document.getElementById('orders-kpis-container');
  const subTitle = document.getElementById('orders-summary-subtitle');
  if (!tbody || !state.rebalancePlan) return;

  const plan = state.rebalancePlan;
  const orders = plan.orders || [];
  const sum = plan.summary || {};

  if (subTitle) {
    subTitle.textContent = `Strategy: ${plan.strategy_name} | Mode: ${plan.rebalance_mode === 'smart_inflow' ? 'Smart Cash Deployment' : 'Full Strategic Realignment'} | Drift Tolerance: ±${plan.tolerance_band}%`;
  }

  // Summary Cards
  if (kpiContainer) {
    kpiContainer.innerHTML = `
      <div class="order-kpi-subcard">
        <span class="lbl">TOTAL REBALANCE POOL</span>
        <span class="val text-info">${formatINR(plan.total_rebalance_pool)}</span>
      </div>
      <div class="order-kpi-subcard">
        <span class="lbl">CASH BUFFER DEPLOYMENT</span>
        <span class="val text-gold">${formatINR(sum.deploy_cash_value)}</span>
      </div>
      <div class="order-kpi-subcard">
        <span class="lbl">TARGET ALLOCATION BUYS</span>
        <span class="val text-success">${formatINR(sum.total_buy_value)} (${sum.num_buys} Orders)</span>
      </div>
      <div class="order-kpi-subcard">
        <span class="lbl">STRATEGIC SELLS / HARVEST</span>
        <span class="val text-danger">${formatINR(sum.total_sell_value)} (${sum.num_sells} Orders)</span>
      </div>
    `;
  }

  // Order Rows
  tbody.innerHTML = orders.map(o => {
    let actionBadge = 'badge-neutral';
    if (o.action === 'BUY') actionBadge = 'badge-success';
    else if (o.action === 'DEPLOY CASH') actionBadge = 'badge-gold';
    else if (o.action === 'SELL') actionBadge = 'badge-danger';

    let priorityBadge = 'badge-neutral';
    if (o.priority === 'HIGH') priorityBadge = 'badge-success';
    else if (o.priority === 'MEDIUM') priorityBadge = 'badge-info';

    return `
      <tr>
        <td>
          <span class="badge ${actionBadge}">${o.action}</span>
        </td>
        <td>
          <strong>${o.instrument}</strong>
          <div class="inst-sub">${o.asset_class}</div>
        </td>
        <td>${o.asset_class}</td>
        <td class="text-right mono-num">₹${Number(o.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
        <td class="text-right mono-num">
          <strong>${o.order_quantity > 0 ? Number(o.order_quantity).toLocaleString('en-IN', { maximumFractionDigits: 3 }) : '-'}</strong>
        </td>
        <td class="text-right mono-num">
          <strong>${o.order_amount > 0 ? formatINR(o.order_amount) : '-'}</strong>
        </td>
        <td class="text-center">
          <span class="badge ${priorityBadge}">${o.priority}</span>
        </td>
        <td class="text-right mono-num">${o.target_1 ? '₹' + Number(o.target_1).toLocaleString('en-IN') : '-'}</td>
        <td class="text-right mono-num text-danger">${o.stop_loss ? '₹' + Number(o.stop_loss).toLocaleString('en-IN') : '-'}</td>
        <td class="text-center mono-num" style="font-weight: 700;">${o.composite_score}</td>
      </tr>
    `;
  }).join('');
}

// Copy Zerodha Basket JSON to Clipboard
function copyOrdersToClipboard() {
  if (!state.rebalancePlan || !state.rebalancePlan.basket_orders) {
    showToast('No orders generated yet', 'error');
    return;
  }
  const basket = state.rebalancePlan.basket_orders;
  navigator.clipboard.writeText(JSON.stringify(basket, null, 2))
    .then(() => {
      showToast(`Copied ${basket.length} Zerodha Kite basket orders to clipboard!`, 'success');
    })
    .catch(() => {
      showToast('Failed to copy to clipboard', 'error');
    });
}

// Export Orders to CSV File
function exportOrdersToCSV() {
  if (!state.rebalancePlan || !state.rebalancePlan.orders) {
    showToast('No orders to export', 'error');
    return;
  }
  const orders = state.rebalancePlan.orders;
  const headers = ['Action', 'Instrument', 'Asset Class', 'Price', 'Order Qty', 'Order Amount', 'Priority', 'Target 1', 'Stop Loss', 'Score'];
  
  const rows = orders.map(o => [
    o.action,
    `"${o.instrument}"`,
    `"${o.asset_class}"`,
    o.price,
    o.order_quantity,
    o.order_amount,
    o.priority,
    o.target_1 || '',
    o.stop_loss || '',
    o.composite_score
  ]);

  const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `QuantRebalance_Orders_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  showToast('Exported execution trade sheet CSV!', 'success');
}

// Upload CSV File
async function uploadCSVFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  showToast(`Uploading and analyzing ${file.name}...`, 'info');
  try {
    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (!data.success) {
      showToast(data.error || 'Upload failed', 'error');
      return;
    }

    state.holdings = data.holdings || [];
    state.metrics = data.metrics || {};
    updateKPICards();
    renderHoldingsTable();
    runRebalanceSimulation();

    const uploadModal = document.getElementById('upload-modal');
    if (uploadModal) uploadModal.classList.remove('open');

    showToast(`Successfully analyzed ${state.holdings.length} holdings from ${file.name}!`, 'success');
  } catch (err) {
    console.error('Upload error:', err);
    showToast('Error uploading file', 'error');
  }
}

// Deep Dive Modal & Chart
async function openDeepDive(symbol) {
  try {
    const res = await fetch(`/api/deepdive/${encodeURIComponent(symbol)}`);
    const data = await res.json();
    if (!data.success) {
      showToast(data.error || 'Failed to load details', 'error');
      return;
    }

    const h = data.holding || {};
    const tech = data.technical || {};
    const fund = data.fundamental || {};
    const analysis = data.analysis || {};

    document.getElementById('modal-asset-name').textContent = h.instrument;
    document.getElementById('modal-asset-category').textContent = h.sub_class || h.asset_class;
    
    const recEl = document.getElementById('modal-asset-rec');
    recEl.textContent = analysis.recommendation || 'HOLD';
    recEl.className = `badge ${analysis.recommendation === 'STRONG BUY' ? 'badge-success' : 'badge-info'}`;

    document.getElementById('modal-price').textContent = formatINR(h.live_price || h.ltp, 2);
    document.getElementById('modal-score').textContent = `${analysis.composite_score || 50} / 100`;
    document.getElementById('modal-t1').textContent = analysis.target_1 ? formatINR(analysis.target_1, 2) : '-';
    document.getElementById('modal-t2').textContent = analysis.target_2 ? formatINR(analysis.target_2, 2) : '-';
    document.getElementById('modal-sl').textContent = analysis.stop_loss ? formatINR(analysis.stop_loss, 2) : '-';

    // Technical Metrics
    document.getElementById('m-rsi').textContent = tech.rsi14 ? `${tech.rsi14} ${tech.rsi14 < 30 ? '(Oversold)' : (tech.rsi14 > 70 ? '(Overbought)' : '(Neutral)')}` : 'N/A';
    document.getElementById('m-sma20').textContent = tech.sma20 ? formatINR(tech.sma20, 2) : 'N/A';
    document.getElementById('m-sma50').textContent = tech.sma50 ? formatINR(tech.sma50, 2) : 'N/A';
    document.getElementById('m-sma200').textContent = tech.sma200 ? formatINR(tech.sma200, 2) : 'N/A';
    document.getElementById('m-52w').textContent = (tech.w52_low && tech.w52_high) ? `${formatINR(tech.w52_low, 0)} - ${formatINR(tech.w52_high, 0)}` : 'N/A';
    document.getElementById('m-trend').textContent = tech.trend || 'Consolidating';

    // Fundamental Metrics
    document.getElementById('m-pe').textContent = fund.pe ? fund.pe : 'N/A';
    document.getElementById('m-fwd-pe').textContent = fund.forward_pe ? fund.forward_pe : 'N/A';
    document.getElementById('m-mcap').textContent = fund.market_cap_fmt ? fund.market_cap_fmt : 'N/A';
    document.getElementById('m-margin').textContent = fund.profit_margins_pct ? `${fund.profit_margins_pct}%` : 'N/A';
    document.getElementById('m-debt').textContent = fund.debt_to_equity ? fund.debt_to_equity : 'N/A';
    document.getElementById('m-analysts').textContent = fund.num_analysts ? `${fund.num_analysts} Analysts (${fund.recommendation_key || 'Covered'})` : 'Standard Coverage';

    document.getElementById('modal-rationale-text').textContent = analysis.reason || 'Asset is stabilizing within expected technical boundaries.';

    // Render Price Chart
    if (tech.history_closes && tech.history_closes.length > 0) {
      renderDeepdiveChart(tech.history_closes, tech.current_price, tech.support, tech.resistance);
    }

    const modal = document.getElementById('deepdive-modal');
    if (modal) modal.classList.add('open');
  } catch (err) {
    console.error('Deepdive error:', err);
    showToast('Failed to load asset deepdive', 'error');
  }
}

// Deep Dive 60-Day Price Movement Line Chart
function renderDeepdiveChart(closes, currentPrice, support, resistance) {
  const canvas = document.getElementById('deepdive-history-chart');
  if (!canvas) return;

  if (state.charts.deepdive) {
    state.charts.deepdive.destroy();
  }

  const ctx = canvas.getContext('2d');
  const labels = closes.map((_, i) => `D-${closes.length - i}`);

  // Create gradient
  const gradient = ctx.createLinearGradient(0, 0, 0, 240);
  gradient.addColorStop(0, 'rgba(0, 210, 255, 0.35)');
  gradient.addColorStop(1, 'rgba(0, 210, 255, 0.0)');

  state.charts.deepdive = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Close Price',
          data: closes,
          borderColor: '#00d2ff',
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 4,
          fill: true,
          backgroundColor: gradient,
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: (ctx) => ` Price: ₹${ctx.parsed.y.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
          }
        }
      },
      scales: {
        x: { display: false },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: {
            color: '#64748b',
            font: { family: 'JetBrains Mono', size: 11 },
            callback: (v) => '₹' + v.toLocaleString('en-IN')
          }
        }
      }
    }
  });
}

// Allocation Donut Chart & Drift Bar Chart
function renderAllocationCharts() {
  if (!state.rebalancePlan) return;
  const driftData = state.rebalancePlan.class_drift || {};

  const labels = Object.keys(driftData);
  const currentWeights = labels.map(k => driftData[k].current_weight_pct);
  const targetWeights = labels.map(k => driftData[k].target_weight_pct);
  const drifts = labels.map(k => driftData[k].drift_pct);

  // 1. Allocation Donut Chart
  const donutCanvas = document.getElementById('allocation-donut-chart');
  if (donutCanvas) {
    if (state.charts.allocation) state.charts.allocation.destroy();

    const ctx = donutCanvas.getContext('2d');
    state.charts.allocation = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Current Weight %',
            data: currentWeights,
            backgroundColor: [
              '#00d2ff',
              '#3b82f6',
              '#10b981',
              '#f59e0b',
              '#8b5cf6'
            ],
            borderWidth: 1,
            borderColor: '#0a0d14'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: {
              color: '#94a3b8',
              font: { family: 'Inter', size: 12 },
              padding: 15
            }
          },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Current: ${ctx.parsed}% (Target: ${targetWeights[ctx.dataIndex]}%)`
            }
          }
        },
        cutout: '70%'
      }
    });
  }

  // 2. Drift Bar Chart
  const barCanvas = document.getElementById('drift-bar-chart');
  if (barCanvas) {
    if (state.charts.drift) state.charts.drift.destroy();

    const ctx = barCanvas.getContext('2d');
    const barColors = drifts.map(d => d > 0 ? '#f43f5e' : '#10b981');

    state.charts.drift = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Allocation Drift %',
            data: drifts,
            backgroundColor: barColors,
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Drift: ${ctx.parsed.y > 0 ? '+' : ''}${ctx.parsed.y}%`
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: {
              color: '#64748b',
              font: { family: 'JetBrains Mono', size: 11 },
              callback: (v) => `${v > 0 ? '+' : ''}${v}%`
            }
          }
        }
      }
    });
  }
}
