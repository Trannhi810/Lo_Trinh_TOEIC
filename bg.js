/* bg.js — Background manager with saved custom list + deletable presets */

const DEFAULT_PRESETS = [
  { id: 'n61ULEU7CO0', title: 'Lofi Girl - Study', type: 'youtube', thumb: 'https://img.youtube.com/vi/n61ULEU7CO0/hqdefault.jpg' },
  { id: '0nTOJnaEqmM', title: 'Tokyo Night Walk', type: 'youtube', thumb: 'https://img.youtube.com/vi/0nTOJnaEqmM/hqdefault.jpg' },
  { id: '7NOSDKb0HlU', title: 'Lofi Boy - Chill', type: 'youtube', thumb: 'https://img.youtube.com/vi/7NOSDKb0HlU/hqdefault.jpg' },
  { id: 'F1B9Fk_SgI0', title: 'Ghibli Piano', type: 'youtube', thumb: 'https://img.youtube.com/vi/F1B9Fk_SgI0/hqdefault.jpg' },
  { id: 'lP26UCnoH9s', title: 'Cozy Cabin Rain', type: 'youtube', thumb: 'https://img.youtube.com/vi/lP26UCnoH9s/hqdefault.jpg' },
  { id: 'V1RPi2MYptM', title: '4K Anime City', type: 'youtube', thumb: 'https://img.youtube.com/vi/V1RPi2MYptM/hqdefault.jpg' }
];

let currentBg = null;
let customBgList = [];   // list of {id, title, type, thumb?, value}
let deletedPresets = []; // ids of deleted default presets

function loadBgStorage() {
  try { currentBg     = JSON.parse(localStorage.getItem('toeic_bg') || 'null'); }     catch(e) { currentBg = null; }
  try { customBgList  = JSON.parse(localStorage.getItem('toeic_bg_custom') || '[]'); }catch(e) { customBgList = []; }
  try { deletedPresets= JSON.parse(localStorage.getItem('toeic_bg_deleted') || '[]');}catch(e) { deletedPresets = []; }
}
function saveBgStorage() {
  if (currentBg) localStorage.setItem('toeic_bg', JSON.stringify(currentBg));
  else localStorage.removeItem('toeic_bg');
  localStorage.setItem('toeic_bg_custom',  JSON.stringify(customBgList));
  localStorage.setItem('toeic_bg_deleted', JSON.stringify(deletedPresets));
}

function initBg() {
  loadBgStorage();
  injectBgContainer();
  injectBgModal();
  renderBg();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initBg);
} else {
  initBg();
}

function injectBgContainer() {
  const container = document.createElement('div');
  container.id = 'global-bg-container';
  document.body.prepend(container);
}

function injectBgModal() {
  const modalEl = document.createElement('div');
  modalEl.innerHTML = `
    <div class="bg-modal-overlay" id="bg-modal-overlay" onclick="closeBgModal(event)">
      <div class="bg-modal" onclick="event.stopPropagation()">
        <div class="bg-modal-header">
          <div class="bg-modal-title">🖼️ Hình nền</div>
          <button class="bg-modal-close" onclick="closeBgModal()">✕</button>
        </div>
        <div class="bg-modal-body">
          <div class="bg-input-group">
            <label class="bg-input-label">Link ảnh / GIF / YouTube</label>
            <div class="bg-input-row">
              <div class="bg-input-wrapper">
                <span class="bg-input-icon">▶</span>
                <input type="text" class="bg-input" id="bg-input-url" placeholder="https://www.youtube.com/watch?v=..." oninput="handleUrlInput()" />
              </div>
              <input type="text" class="bg-input bg-title-input" id="bg-input-title" placeholder="Tên gợi nhớ (tuỳ chọn)" />
              <button class="bg-btn bg-btn-save-custom" onclick="saveCustomBg()">💾 Lưu</button>
            </div>
            <div id="bg-input-feedback" style="font-size:12px; color:var(--success); margin-top:8px; display:none;"></div>
          </div>

          <!-- SAVED CUSTOM LIST -->
          <div id="bg-custom-section" style="display:none;">
            <div class="bg-presets-title">🎬 Video nền đã lưu</div>
            <div class="bg-preset-grid" id="bg-custom-grid"></div>
          </div>

          <!-- DEFAULT PRESETS -->
          <div id="bg-default-section">
            <div class="bg-presets-title">Hoặc chọn Preset (Study with me)</div>
            <div class="bg-preset-grid" id="bg-preset-grid"></div>
          </div>
        </div>
        <div class="bg-modal-footer">
          <button class="bg-btn bg-btn-clear" onclick="clearBg()">✕ Xóa nền</button>
          <div class="bg-footer-right">
            <button class="bg-btn bg-btn-cancel" onclick="closeBgModal()">Hủy</button>
            <button class="bg-btn bg-btn-apply" onclick="applyBgFromInput()">✓ Áp dụng</button>
          </div>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(modalEl.firstElementChild);
}

function openBgModal(e) {
  if (e) e.preventDefault();
  document.getElementById('bg-modal-overlay').classList.add('show');
  renderPresetGrid();
}

function closeBgModal(e) {
  if (e && e.target.id !== 'bg-modal-overlay') return;
  document.getElementById('bg-modal-overlay').classList.remove('show');
}

function parseYoutubeUrl(url) {
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
  const match = url.match(regExp);
  return (match && match[2].length === 11) ? match[2] : null;
}

function handleUrlInput() {
  const url = document.getElementById('bg-input-url').value.trim();
  const feedback = document.getElementById('bg-input-feedback');
  if (!url) { feedback.style.display = 'none'; return; }
  const ytId = parseYoutubeUrl(url);
  if (ytId) {
    feedback.textContent = '✓ Nhận diện link YouTube hợp lệ';
    feedback.style.color = 'var(--success)';
    feedback.style.display = 'block';
  } else if (url.match(/\.(jpeg|jpg|gif|png|webp)$/i)) {
    feedback.textContent = '✓ Nhận diện link Ảnh hợp lệ';
    feedback.style.color = 'var(--success)';
    feedback.style.display = 'block';
  } else {
    feedback.textContent = 'Link không rõ định dạng, vẫn có thể thử!';
    feedback.style.color = 'var(--warning)';
    feedback.style.display = 'block';
  }
}

function saveCustomBg() {
  const url = document.getElementById('bg-input-url').value.trim();
  if (!url) return;
  const title = document.getElementById('bg-input-title').value.trim() || 'Nền tùy chỉnh';
  const ytId = parseYoutubeUrl(url);
  const entry = {
    id: 'custom_' + Date.now(),
    title,
    type: ytId ? 'youtube' : 'image',
    value: ytId || url,
    thumb: ytId ? `https://img.youtube.com/vi/${ytId}/hqdefault.jpg` : url
  };
  customBgList.unshift(entry);
  saveBgStorage();
  document.getElementById('bg-input-url').value = '';
  document.getElementById('bg-input-title').value = '';
  document.getElementById('bg-input-feedback').style.display = 'none';
  renderPresetGrid();
  showBgToast('💾 Đã lưu nền!');
}

function deleteCustomBg(id, event) {
  event.stopPropagation();
  customBgList = customBgList.filter(b => b.id !== id);
  if (currentBg && currentBg._id === id) { currentBg = null; renderBg(); }
  saveBgStorage();
  renderPresetGrid();
}

function deleteDefaultPreset(id, event) {
  event.stopPropagation();
  if (!deletedPresets.includes(id)) deletedPresets.push(id);
  if (currentBg && currentBg.type === 'youtube' && currentBg.value === id) { currentBg = null; renderBg(); }
  saveBgStorage();
  renderPresetGrid();
}

function selectCustomBg(entry) {
  document.getElementById('bg-input-url').value = entry.type === 'youtube'
    ? `https://youtube.com/watch?v=${entry.value}` : entry.value;
  document.getElementById('bg-input-title').value = entry.title;
  handleUrlInput();
  // Directly apply
  saveAndRenderBg({ type: entry.type, value: entry.value, _id: entry.id });
  closeBgModal();
}

function selectPreset(id) {
  document.querySelectorAll('.bg-preset-item').forEach(el => el.classList.remove('active'));
  const el = document.getElementById('preset-' + id);
  if (el) el.classList.add('active');
  document.getElementById('bg-input-url').value = 'https://youtube.com/watch?v=' + id;
  handleUrlInput();
  saveAndRenderBg({ type: 'youtube', value: id });
  closeBgModal();
}

function renderPresetGrid() {
  // Custom list
  const customSection = document.getElementById('bg-custom-section');
  const customGrid = document.getElementById('bg-custom-grid');
  if (customBgList.length > 0) {
    customSection.style.display = '';
    customGrid.innerHTML = customBgList.map(entry => `
      <div class="bg-preset-item ${currentBg && currentBg._id === entry.id ? 'active' : ''}" onclick="selectCustomBg(${JSON.stringify(entry).replace(/"/g,'&quot;')})">
        <img src="${entry.thumb || ''}" alt="${entry.title}" onerror="this.style.display='none'" />
        <div class="bg-preset-label">${entry.title}</div>
        <button class="bg-preset-delete" onclick="deleteCustomBg('${entry.id}', event)" title="Xóa">✕</button>
      </div>
    `).join('');
  } else {
    customSection.style.display = 'none';
    customGrid.innerHTML = '';
  }

  // Default presets (hide deleted ones)
  const defaultGrid = document.getElementById('bg-preset-grid');
  const visiblePresets = DEFAULT_PRESETS.filter(p => !deletedPresets.includes(p.id));
  const defaultSection = document.getElementById('bg-default-section');
  if (visiblePresets.length > 0) {
    defaultSection.style.display = '';
    defaultGrid.innerHTML = visiblePresets.map(p => `
      <div class="bg-preset-item ${currentBg && currentBg.type === 'youtube' && currentBg.value === p.id ? 'active' : ''}" id="preset-${p.id}" onclick="selectPreset('${p.id}')">
        <img src="${p.thumb}" alt="${p.title}" />
        <div class="bg-preset-label">${p.title}</div>
        <button class="bg-preset-delete" onclick="deleteDefaultPreset('${p.id}', event)" title="Xóa preset này">✕</button>
      </div>
    `).join('');
  } else {
    defaultSection.style.display = 'none';
  }
}

function applyBgFromInput() {
  const url = document.getElementById('bg-input-url').value.trim();
  if (!url) return;
  const ytId = parseYoutubeUrl(url);
  let config = ytId ? { type: 'youtube', value: ytId } : { type: 'image', value: url };
  saveAndRenderBg(config);
  closeBgModal();
}

function clearBg() {
  saveAndRenderBg(null);
  closeBgModal();
}

function saveAndRenderBg(config) {
  currentBg = config;
  saveBgStorage();
  renderBg();
}

function renderBg() {
  const container = document.getElementById('global-bg-container');
  if (!container) return;
  container.innerHTML = '';
  container.style.backgroundImage = 'none';

  if (!currentBg) {
    container.style.opacity = '0';
    return;
  }
  container.style.opacity = '1';

  if (currentBg.type === 'youtube') {
    container.style.backgroundColor = '#000';
    const overlay = document.createElement('div');
    overlay.style.cssText = 'position:absolute;inset:0;background:rgba(11,13,23,0.65);z-index:1;';
    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube.com/embed/${currentBg.value}?autoplay=1&mute=1&controls=0&loop=1&playlist=${currentBg.value}&modestbranding=1&showinfo=0`;
    iframe.frameBorder = '0';
    iframe.allow = 'autoplay; encrypted-media';
    container.appendChild(iframe);
    container.appendChild(overlay);
  } else if (currentBg.type === 'image') {
    container.style.backgroundImage = `linear-gradient(rgba(11,13,23,0.7), rgba(11,13,23,0.7)), url('${currentBg.value}')`;
  }
}

function showBgToast(msg) {
  const t = document.createElement('div');
  t.style.cssText = `position:fixed;bottom:24px;right:24px;z-index:20000;background:rgba(10,12,28,0.95);border:1px solid rgba(99,102,241,0.4);color:#a5b4fc;padding:10px 18px;border-radius:12px;font-size:14px;font-weight:600;font-family:Inter,sans-serif;backdrop-filter:blur(12px);animation:bgToastIn .3s ease;`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => { if (document.body.contains(t)) document.body.removeChild(t); }, 2500);
}
