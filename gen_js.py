import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('toeic_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

js_data = json.dumps(data, ensure_ascii=False)

js_code = r"""// ===================================================
// TOEIC 0→700 ROADMAP — APP.JS
// Sub-task checkboxes: must complete all before marking day done
// ===================================================

const DATA = """ + js_data + r""";

// Sub-tasks definition per day
const SUB_TASKS = ['ipa', 'grammar', 'vocab', 'listening', 'books', 'review'];
const SUB_TASK_LABELS = {
  ipa:       { icon: '🔊', label: 'IPA / Phát âm',  cls: 'label-ipa' },
  grammar:   { icon: '📖', label: 'Grammar',         cls: 'label-grammar' },
  vocab:     { icon: '📚', label: 'Vocabulary',      cls: 'label-vocab' },
  listening: { icon: '🎧', label: 'Listening',       cls: 'label-listening' },
  books:     { icon: '📕', label: 'Sách luyện',      cls: 'label-books' },
  review:    { icon: '🔁', label: 'Ôn tập',          cls: 'label-review' },
};

// ===== STATE =====
// checkedDays[day] = true  → toàn bộ ngày đã hoàn thành
// subChecked[day][task] = true → từng sub-task của ngày đó
let checkedDays = JSON.parse(localStorage.getItem('toeic_done') || '{}');
let subChecked  = JSON.parse(localStorage.getItem('toeic_sub')  || '{}');

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

// ===== BUILD DAY CARD =====
function buildDayCard(d) {
  const isDone = !!checkedDays[d.day];
  const isReview = d.review && d.review.includes('Tổng');
  const sub = subChecked[d.day] || {};

  // count valid sub-tasks (skip '—' content)
  const books = [
    d.hackers !== '—' ? 'Hackers (' + d.hackers + ')' : '',
    d.ybm !== '—' ? 'YBM (' + d.ybm + ')' : '',
    d.ets !== '—' ? 'ETS: ' + d.ets : ''
  ].filter(Boolean).join(' | ') || '—';

  const subValues = {
    ipa: d.ipa || '—',
    grammar: d.grammar || '—',
    vocab: d.vocab || '—',
    listening: d.listening || '—',
    books: books,
    review: d.review || '—',
  };

  // count sub tasks that have real content (not '—')
  const totalSubs = SUB_TASKS.filter(k => subValues[k] !== '—').length;
  const doneSubs  = SUB_TASKS.filter(k => subValues[k] !== '—' && sub[k]).length;
  const allSubsDone = totalSubs > 0 && doneSubs === totalSubs;

  const card = document.createElement('div');
  card.className = 'day-card' + (isDone ? ' is-done' : '') + (isReview ? ' is-review' : '');
  card.id = 'day-card-' + d.day;

  // sub-progress bar text
  const subPct = totalSubs > 0 ? Math.round(doneSubs/totalSubs*100) : 0;

  card.innerHTML = `
    <div class="day-header" onclick="toggleDay(${d.day})">
      <span class="day-num">Ngày ${d.day}</span>
      <div class="day-summary">
        <div class="day-grammar-tag">${escHtml(d.grammar || '')}</div>
        <div class="day-vocab-tag">${escHtml(d.vocab || '')}</div>
      </div>
      <div class="day-sub-progress" id="subprog-${d.day}">
        <div class="day-sub-bar-track"><div class="day-sub-bar-fill" style="width:${subPct}%"></div></div>
        <span class="day-sub-count">${doneSubs}/${totalSubs}</span>
      </div>
      <div class="done-checkbox ${isDone ? 'checked' : ''} ${!allSubsDone && !isDone ? 'locked' : ''}"
           id="cb-${d.day}"
           onclick="toggleDone(event,${d.day})"
           title="${!allSubsDone && !isDone ? 'Hoàn thành tất cả nhiệm vụ con trước!' : (isDone ? 'Bỏ đánh dấu' : 'Đánh dấu hoàn thành')}">
        ${isDone ? '✓' : (allSubsDone ? '✓' : '')}
      </div>
      <span class="day-expand-icon" id="exp-${d.day}">▼</span>
    </div>
    <div class="day-body" id="body-${d.day}">
      <div class="detail-grid">
        ${SUB_TASKS.map(key => {
          const val = subValues[key];
          const info = SUB_TASK_LABELS[key];
          const hasContent = val !== '—';
          const checked = hasContent && !!sub[key];
          return `
          <div class="detail-item ${checked ? 'sub-done' : ''}" id="detail-${d.day}-${key}">
            <div class="detail-item-top">
              <div class="detail-label ${info.cls}">${info.icon} ${info.label}</div>
              ${hasContent ? `
              <button class="sub-checkbox ${checked ? 'checked' : ''}"
                      id="scb-${d.day}-${key}"
                      onclick="toggleSub(event,${d.day},'${key}')"
                      title="${checked ? 'Bỏ hoàn thành' : 'Đánh dấu xong'}">
                ${checked ? '✓' : ''}
              </button>` : ''}
            </div>
            <div class="detail-value">${escHtml(val)}</div>
          </div>`;
        }).join('')}
      </div>
      <div class="routine-chip">⏱ ${escHtml(d.routine || '')}</div>
      <div class="day-complete-row" id="complete-row-${d.day}">
        <span class="complete-hint" id="hint-${d.day}">
          ${allSubsDone
            ? (isDone ? '✅ Ngày này đã hoàn thành!' : '🎉 Tất cả xong! Hãy đánh dấu ngày hoàn thành →')
            : `⏳ Còn ${totalSubs - doneSubs} nhiệm vụ chưa hoàn thành`}
        </span>
        <button class="btn-complete-day ${isDone ? 'done' : ''} ${!allSubsDone && !isDone ? 'locked' : ''}"
                id="btn-complete-${d.day}"
                onclick="toggleDone(event,${d.day})"
                ${!allSubsDone && !isDone ? 'disabled' : ''}>
          ${isDone ? '✅ Đã hoàn thành' : '☐ Đánh dấu hoàn thành ngày'}
        </button>
      </div>
    </div>
  `;
  return card;
}

// ===== TOGGLE DAY EXPAND =====
function toggleDay(day) {
  const body = document.getElementById('body-' + day);
  const icon = document.getElementById('exp-' + day);
  // auto-open on first click
  if (!body.classList.contains('open')) {
    body.classList.add('open');
    icon.classList.add('open');
  } else {
    body.classList.remove('open');
    icon.classList.remove('open');
  }
}

// ===== TOGGLE SUB-TASK =====
function toggleSub(e, day, key) {
  e.stopPropagation();
  if (!subChecked[day]) subChecked[day] = {};
  subChecked[day][key] = !subChecked[day][key];
  if (!subChecked[day][key]) delete subChecked[day][key];
  if (Object.keys(subChecked[day]).length === 0) delete subChecked[day];
  localStorage.setItem('toeic_sub', JSON.stringify(subChecked));

  // update UI for this sub item
  const scb = document.getElementById('scb-' + day + '-' + key);
  const detailItem = document.getElementById('detail-' + day + '-' + key);
  const isChecked = !!(subChecked[day] && subChecked[day][key]);
  if (scb) { scb.classList.toggle('checked', isChecked); scb.textContent = isChecked ? '✓' : ''; }
  if (detailItem) { detailItem.classList.toggle('sub-done', isChecked); }

  // recalculate sub progress for this day
  refreshDaySubProgress(day);
}

function refreshDaySubProgress(day) {
  const d = DATA.roadmap.find(x => x.day === day);
  if (!d) return;

  const books = [
    d.hackers !== '—' ? 'Hackers (' + d.hackers + ')' : '',
    d.ybm !== '—' ? 'YBM (' + d.ybm + ')' : '',
    d.ets !== '—' ? 'ETS: ' + d.ets : ''
  ].filter(Boolean).join(' | ') || '—';

  const subValues = {
    ipa: d.ipa || '—', grammar: d.grammar || '—',
    vocab: d.vocab || '—', listening: d.listening || '—',
    books, review: d.review || '—',
  };

  const sub = subChecked[day] || {};
  const totalSubs = SUB_TASKS.filter(k => subValues[k] !== '—').length;
  const doneSubs  = SUB_TASKS.filter(k => subValues[k] !== '—' && sub[k]).length;
  const allSubsDone = totalSubs > 0 && doneSubs === totalSubs;
  const isDone = !!checkedDays[day];
  const subPct = totalSubs > 0 ? Math.round(doneSubs/totalSubs*100) : 0;

  // sub progress bar in header
  const fill = document.querySelector('#subprog-' + day + ' .day-sub-bar-fill');
  const cnt  = document.querySelector('#subprog-' + day + ' .day-sub-count');
  if (fill) fill.style.width = subPct + '%';
  if (cnt)  cnt.textContent = doneSubs + '/' + totalSubs;

  // main checkbox
  const cb = document.getElementById('cb-' + day);
  if (cb) {
    cb.classList.toggle('locked', !allSubsDone && !isDone);
    cb.title = !allSubsDone && !isDone
      ? 'Hoàn thành tất cả nhiệm vụ con trước!'
      : (isDone ? 'Bỏ đánh dấu' : 'Đánh dấu hoàn thành');
    if (!isDone) cb.textContent = allSubsDone ? '✓' : '';
    if (!isDone && !allSubsDone) cb.classList.remove('checked');
    else if (!isDone && allSubsDone) cb.classList.add('ready');
  }

  // complete button + hint
  const btn = document.getElementById('btn-complete-' + day);
  const hint = document.getElementById('hint-' + day);
  if (btn) {
    btn.disabled = !allSubsDone && !isDone;
    btn.classList.toggle('locked', !allSubsDone && !isDone);
  }
  if (hint) {
    if (isDone) hint.textContent = '✅ Ngày này đã hoàn thành!';
    else if (allSubsDone) hint.textContent = '🎉 Tất cả xong! Hãy đánh dấu ngày hoàn thành →';
    else hint.textContent = '⏳ Còn ' + (totalSubs - doneSubs) + ' nhiệm vụ chưa hoàn thành';
  }
}

// ===== TOGGLE DAY DONE =====
function toggleDone(e, day) {
  e.stopPropagation();
  // check if allowed
  const d = DATA.roadmap.find(x => x.day === day);
  if (!d) return;

  const books = [
    d.hackers !== '—' ? 'Hackers (' + d.hackers + ')' : '',
    d.ybm !== '—' ? 'YBM (' + d.ybm + ')' : '',
    d.ets !== '—' ? 'ETS: ' + d.ets : ''
  ].filter(Boolean).join(' | ') || '—';
  const subValues = {
    ipa: d.ipa || '—', grammar: d.grammar || '—',
    vocab: d.vocab || '—', listening: d.listening || '—',
    books, review: d.review || '—',
  };
  const sub = subChecked[day] || {};
  const totalSubs = SUB_TASKS.filter(k => subValues[k] !== '—').length;
  const doneSubs  = SUB_TASKS.filter(k => subValues[k] !== '—' && sub[k]).length;
  const allSubsDone = totalSubs > 0 && doneSubs === totalSubs;
  const isDone = !!checkedDays[day];

  if (!isDone && !allSubsDone) {
    // shake the button to hint
    const btn = document.getElementById('btn-complete-' + day);
    if (btn) { btn.classList.add('shake'); setTimeout(() => btn.classList.remove('shake'), 500); }
    return;
  }

  checkedDays[day] = !isDone;
  if (!checkedDays[day]) delete checkedDays[day];
  localStorage.setItem('toeic_done', JSON.stringify(checkedDays));

  const newDone = !!checkedDays[day];
  const cb = document.getElementById('cb-' + day);
  if (cb) {
    cb.classList.toggle('checked', newDone);
    cb.classList.remove('ready', 'locked');
    cb.textContent = newDone ? '✓' : (allSubsDone ? '✓' : '');
    if (!newDone && allSubsDone) cb.classList.add('ready');
  }
  const card = document.getElementById('day-card-' + day);
  if (card) card.classList.toggle('is-done', newDone);

  const btn2 = document.getElementById('btn-complete-' + day);
  const hint = document.getElementById('hint-' + day);
  if (btn2) { btn2.textContent = newDone ? '✅ Đã hoàn thành' : '☐ Đánh dấu hoàn thành ngày'; btn2.classList.toggle('done', newDone); }
  if (hint) hint.textContent = newDone ? '✅ Ngày này đã hoàn thành!' : '🎉 Tất cả xong! Hãy đánh dấu ngày hoàn thành →';

  updateGlobalProgress();
  if (d) updateWeekProgress(d.week);
}

function updateWeekProgress(week) {
  const weekDays = DATA.roadmap.filter(d => d.week === week);
  const done = weekDays.filter(d => checkedDays[d.day]).length;
  const pct = Math.round(done / weekDays.length * 100);
  const fill = document.querySelector('#week-' + week + ' .week-progress-fill');
  const cnt  = document.querySelector('#week-' + week + ' .week-count');
  if (fill) fill.style.width = pct + '%';
  if (cnt)  cnt.textContent = done + '/' + weekDays.length;
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
