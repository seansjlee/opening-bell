/* Opening Bell — Dashboard */

const API = {
  latest: '/api/briefing/latest',
  byDate: (d) => `/api/briefing/${d}`,
  list: '/api/briefings',
};

// ── Helpers ────────────────────────────────────────────────────────────────

function formatDate(isoDate) {
  if (!isoDate) return '';
  const [y, m, d] = isoDate.split('-').map(Number);
  return new Date(y, m - 1, d).toLocaleDateString('en-GB', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  });
}

function formatDateTime(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('en-GB', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', timeZoneName: 'short',
  });
}

function formatPrice(price, symbol) {
  if (price == null) return '—';
  const isForex = symbol && symbol.includes('=X');
  return isForex ? price.toFixed(4) : price.toLocaleString('en-US', { maximumFractionDigits: 2 });
}

function formatChange(pct) {
  if (pct == null) return '—';
  const sign = pct >= 0 ? '+' : '';
  return `${sign}${pct.toFixed(2)}%`;
}

// ── Render ──────────────────────────────────────────────────────────────────

function renderMarketSnapshot(items) {
  const grid = document.getElementById('market-snapshot');
  grid.innerHTML = items.map(item => `
    <div class="market-item ${item.direction}">
      <div class="market-name">${item.name}</div>
      <div class="market-price">${formatPrice(item.price, item.symbol)}</div>
      <div class="market-change ${item.direction}">${formatChange(item.change_pct)}</div>
      <div class="market-category">${item.category}</div>
    </div>
  `).join('');
}

function renderStories(stories) {
  const list = document.getElementById('top-stories');
  list.innerHTML = stories.map((s, i) => `
    <div class="story-item">
      <div class="story-header" onclick="toggleStory(${i})" role="button" aria-expanded="false" aria-controls="story-body-${i}">
        <div>
          <div class="story-headline">${escapeHtml(s.headline)}</div>
          <div class="story-source">${escapeHtml(s.source || '')}</div>
        </div>
        <span class="story-toggle" id="story-toggle-${i}">▾</span>
      </div>
      <div class="story-body" id="story-body-${i}">
        <p class="story-summary">${escapeHtml(s.summary || '')}</p>
        <p class="story-why"><strong>Why it matters:</strong> ${escapeHtml(s.why_it_matters || '')}</p>
      </div>
    </div>
  `).join('');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function toggleStory(i) {
  const body = document.getElementById(`story-body-${i}`);
  const toggle = document.getElementById(`story-toggle-${i}`);
  const isOpen = body.classList.toggle('open');
  toggle.classList.toggle('open', isOpen);
  body.closest('.story-header').setAttribute('aria-expanded', isOpen);
}

function renderBriefing(data) {
  document.getElementById('briefing-date').textContent = formatDate(data.date);
  document.getElementById('generated-at').textContent =
    `Generated ${formatDateTime(data.generated_at)}`;
  document.getElementById('key-takeaway').textContent = data.key_takeaway || '';
  document.getElementById('macro-pulse').textContent = data.macro_pulse || '';
  document.getElementById('sector-spotlight').textContent = data.sector_spotlight || '';

  if (data.market_snapshot?.length) renderMarketSnapshot(data.market_snapshot);
  if (data.top_stories?.length) renderStories(data.top_stories);

  document.getElementById('footer-date').textContent = `Briefing for ${data.date}`;

  show('content');
}

// ── State management ────────────────────────────────────────────────────────

function show(id) {
  ['loading', 'error', 'content'].forEach(s => {
    document.getElementById(s).classList.toggle('hidden', s !== id);
  });
}

async function loadBriefing(date = null) {
  show('loading');
  try {
    const url = date ? API.byDate(date) : API.latest;
    const res = await fetch(url);
    if (!res.ok) throw new Error(res.statusText);
    const data = await res.json();
    renderBriefing(data);
  } catch {
    show('error');
  }
}

async function populateDatePicker() {
  try {
    const res = await fetch(API.list);
    if (!res.ok) return;
    const dates = await res.json();
    const picker = document.getElementById('date-picker');
    picker.innerHTML = dates.map((d, i) =>
      `<option value="${d}">${i === 0 ? `Today — ${d}` : d}</option>`
    ).join('');
    picker.addEventListener('change', () => loadBriefing(picker.value));
  } catch {
    // No dates available yet — hide the picker
    document.getElementById('date-picker').style.display = 'none';
  }
}

// ── Theme ───────────────────────────────────────────────────────────────────

function initTheme() {
  const saved = localStorage.getItem('ob-theme') || 'dark';
  applyTheme(saved);
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  document.getElementById('theme-icon').textContent = theme === 'dark' ? '☀️' : '🌙';
  localStorage.setItem('ob-theme', theme);
}

document.getElementById('theme-toggle').addEventListener('click', () => {
  const current = document.documentElement.getAttribute('data-theme');
  applyTheme(current === 'dark' ? 'light' : 'dark');
});

// ── Init ────────────────────────────────────────────────────────────────────

initTheme();
populateDatePicker();
loadBriefing();
