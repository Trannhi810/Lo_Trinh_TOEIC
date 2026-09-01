import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('toeic_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

js_data = json.dumps(data, ensure_ascii=False)

js_code = r"""// ===================================================
// TOEIC 0→700 ROADMAP — APP.JS
// Data embedded from Lo_trinh_TOEIC_0_700_6_thang.xlsx
// ===================================================

const DATA = """ + js_data + r""";

// ===== STATE =====
let checkedDays = JSON.parse(localStorage.getItem('toeic_done') || '{}');
let currentTab = 'roadmap';

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
  buildWeekFilter();
  renderRoadmap(DATA.roadmap);
  renderGrammar(DATA.grammar);
  renderRoutine(DATA.routine);
  updateGlobalProgress();
  handleScroll();
  window.addEventListener('scroll', handleScroll);
});

// ===== TAB =====
function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + tab).classList.add('active');
  document.getElementById('tab-' + tab).classList.add('active');
}

// ===== FILTER HELPERS =====
function buildWeekFilter() {
  const weeks = [...new Set(DATA.roadmap.map(d => d.week))].sort((a,b) => a-b);
  const sel = document.getElementById('week-filter');
  weeks.forEach(w => {
    const opt = document.createElement('option');
    opt.value = w;
    opt.textContent = 'Tuần ' + w;
    sel.appendChild(opt);
  });
}

function resetFilters() {
  document.getElementById('search-input').value = '';
  document.getElementById('week-filter').value = '';
  document.getElementById('status-filter').value = '';
  filterRoadmap();
}

function filterRoadmap() {
  const q = document.getElementById('search-input').value.toLowerCase();
  const wf = document.getElementById('week-filter').value;
  const sf = document.getElementById('status-filter').value;
  const filtered = DATA.roadmap.filter(d => {
    const matchQ = !q || [d.day, d.week, d.ipa, d.grammar, d.vocab, d.listening, d.ets, d.routine]
      .join(' ').toLowerCase().includes(q);
    const matchW = !wf || String(d.week) === wf;
    const isDone = !!checkedDays[d.day];
    const matchS = !sf || (sf === 'done' && isDone) || (sf === 'pending' && !isDone);
    return matchQ && matchW && matchS;
  });
  renderRoadmap(filtered);
}

// ===== RENDER ROADMAP =====
function renderRoadmap(days) {
  const container = document.getElementById('week-groups');
  container.innerHTML = '';
  if (!days.length) {
    container.innerHTML = '<div class="no-results"><div class="no-results-icon">🔍</div><div class="no-results-text">Không tìm thấy kết quả phù hợp.</div></div>';
    return;
  }
  // Group by week
  const groups = {};
  days.forEach(d => {
    if (!groups[d.week]) groups[d.week] = [];
    groups[d.week].push(d);
  });
  Object.keys(groups).sort((a,b) => a-b).forEach(week => {
    const groupDays = groups[week];
    const doneCount = groupDays.filter(d => checkedDays[d.day]).length;
    const pct = Math.round(doneCount / groupDays.length * 100);
    const dayNums = groupDays.map(d => d.day);
    const minDay = Math.min(...dayNums), maxDay = Math.max(...dayNums);

    const section = document.createElement('div');
    section.className = 'week-group';
    section.id = 'week-' + week;

    const header = document.createElement('div');
    header.className = 'week-header';
    header.innerHTML = `
      <span class="week-label">Tuần</span>
      <span class="week-number">${week}</span>
      <span class="week-days">Ngày ${minDay}–${maxDay}</span>
      <div class="week-progress-mini"><div class="week-progress-fill" style="width:${pct}%"></div></div>
      <span class="week-count">${doneCount}/${groupDays.length}</span>
      <span class="week-toggle" id="wtoggle-${week}">▼</span>
    `;
    header.onclick = () => toggleWeek(week);

    const list = document.createElement('div');
    list.className = 'day-list';
    list.id = 'wlist-' + week;
    groupDays.forEach(d => list.appendChild(buildDayCard(d)));

    section.appendChild(header);
    section.appendChild(list);
    container.appendChild(section);
  });
}

function toggleWeek(week) {
  const list = document.getElementById('wlist-' + week);
  const tog = document.getElementById('wtoggle-' + week);
  if (list.style.display === 'none') {
    list.style.display = 'flex';
    list.style.flexDirection = 'column';
    list.style.gap = '8px';
    tog.classList.add('open');
  } else {
    list.style.display = 'none';
    tog.classList.remove('open');
  }
}

function buildDayCard(d) {
  const isDone = !!checkedDays[d.day];
  const isReview = d.review && d.review.includes('Tổng');

  const card = document.createElement('div');
  card.className = 'day-card' + (isDone ? ' is-done' : '') + (isReview ? ' is-review' : '');
  card.id = 'day-card-' + d.day;

  const books = [
    d.hackers !== '—' ? 'Hackers (' + d.hackers + ')' : '',
    d.ybm !== '—' ? 'YBM (' + d.ybm + ')' : '',
    d.ets !== '—' ? 'ETS: ' + d.ets : ''
  ].filter(Boolean).join(' | ') || '—';

  card.innerHTML = `
    <div class="day-header" onclick="toggleDay(${d.day})">
      <span class="day-num">Ngày ${d.day}</span>
      <div class="day-summary">
        <div class="day-grammar-tag">${escHtml(d.grammar || '')}</div>
        <div class="day-vocab-tag">${escHtml(d.vocab || '')}</div>
      </div>
      <div class="done-checkbox ${isDone ? 'checked' : ''}" id="cb-${d.day}" onclick="toggleDone(event,${d.day})">${isDone ? '✓' : ''}</div>
      <span class="day-expand-icon" id="exp-${d.day}">▼</span>
    </div>
    <div class="day-body" id="body-${d.day}">
      <div class="detail-grid">
        <div class="detail-item">
          <div class="detail-label label-ipa">🔊 IPA / Phát âm</div>
          <div class="detail-value">${escHtml(d.ipa || '—')}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label label-grammar">📖 Grammar</div>
          <div class="detail-value">${escHtml(d.grammar || '—')}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label label-vocab">📚 Vocabulary</div>
          <div class="detail-value">${escHtml(d.vocab || '—')}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label label-listening">🎧 Listening</div>
          <div class="detail-value">${escHtml(d.listening || '—')}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label label-books">📕 Sách luyện</div>
          <div class="detail-value">${escHtml(books)}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label label-review">🔁 Ôn tập</div>
          <div class="detail-value">${escHtml(d.review || '—')}</div>
        </div>
      </div>
      <div class="routine-chip">⏱ ${escHtml(d.routine || '')}</div>
    </div>
  `;
  return card;
}

function toggleDay(day) {
  const body = document.getElementById('body-' + day);
  const icon = document.getElementById('exp-' + day);
  body.classList.toggle('open');
  icon.classList.toggle('open');
}

function toggleDone(e, day) {
  e.stopPropagation();
  checkedDays[day] = !checkedDays[day];
  if (!checkedDays[day]) delete checkedDays[day];
  localStorage.setItem('toeic_done', JSON.stringify(checkedDays));
  const cb = document.getElementById('cb-' + day);
  if (cb) { cb.classList.toggle('checked', !!checkedDays[day]); cb.textContent = checkedDays[day] ? '✓' : ''; }
  const card = document.getElementById('day-card-' + day);
  if (card) { card.classList.toggle('is-done', !!checkedDays[day]); }
  updateGlobalProgress();
  const dayData = DATA.roadmap.find(d => d.day === day);
  if (dayData) updateWeekProgress(dayData.week);
}

function updateWeekProgress(week) {
  const weekDays = DATA.roadmap.filter(d => d.week === week);
  const done = weekDays.filter(d => checkedDays[d.day]).length;
  const pct = Math.round(done / weekDays.length * 100);
  const fill = document.querySelector('#week-' + week + ' .week-progress-fill');
  const cnt = document.querySelector('#week-' + week + ' .week-count');
  if (fill) fill.style.width = pct + '%';
  if (cnt) cnt.textContent = done + '/' + weekDays.length;
}

function updateGlobalProgress() {
  const total = DATA.roadmap.length;
  const done = Object.keys(checkedDays).length;
  const pct = Math.round(done / total * 100);
  document.getElementById('stat-done').textContent = done;
  document.getElementById('stat-percent').textContent = pct + '%';
  document.getElementById('global-progress-bar').style.width = pct + '%';
  document.getElementById('progress-label').textContent = done + ' / ' + total + ' ngày';
}

// ===== RENDER GRAMMAR =====
function renderGrammar(items) {
  const grid = document.getElementById('grammar-grid');
  grid.innerHTML = '';
  items.forEach(g => {
    const card = document.createElement('div');
    card.className = 'grammar-card';
    card.innerHTML = `
      <div class="grammar-day-badge">Ngày ${g.day}</div>
      <div class="grammar-topic">${escHtml(g.topic || '')}</div>
      <div class="grammar-content">${escHtml(g.content || '')}</div>
    `;
    grid.appendChild(card);
  });
}

// ===== RENDER ROUTINE =====
function renderRoutine(items) {
  const container = document.getElementById('routine-cards');
  container.innerHTML = '';
  const icons = ['🔊', '📖', '📚', '🎧'];
  const classes = ['skill-ipa', 'skill-grammar', 'skill-vocab', 'skill-listening'];
  const names = ['IPA / Phát âm', 'Grammar', 'Vocabulary', 'Listening + TOEIC'];
  items.forEach(r => {
    const card = document.createElement('div');
    card.className = 'routine-card';
    const skills = [r.ipa, r.grammar, r.vocab, r.listening];
    const chipsHtml = skills.map((s, i) => `
      <div class="skill-chip ${classes[i]}">
        <div class="skill-name">${icons[i]} ${names[i]}</div>
        <div class="skill-time">${escHtml(s || '—')}</div>
      </div>
    `).join('');
    card.innerHTML = `
      <div class="routine-period-badge">${escHtml(r.period)}</div>
      <div class="routine-skills">${chipsHtml}</div>
    `;
    container.appendChild(card);
  });
}

// ===== UTILS =====
function escHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function handleScroll() {
  const btn = document.getElementById('back-to-top');
  btn.classList.toggle('visible', window.scrollY > 300);
}
"""

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js_code)

print('app.js created, size:', len(js_code), 'chars')
