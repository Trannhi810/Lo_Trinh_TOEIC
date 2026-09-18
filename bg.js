/* bg.js */

const PRESETS = [
  { id: 'jfKfPfyJRdk', title: 'Lofi Girl - Study', type: 'youtube', thumb: 'https://img.youtube.com/vi/jfKfPfyJRdk/mqdefault.jpg' },
  { id: '4xDzrIxZZ0k', title: 'Tokyo Night Walk', type: 'youtube', thumb: 'https://img.youtube.com/vi/4xDzrIxZZ0k/mqdefault.jpg' },
  { id: '7NOSDKb0HlU', title: 'Lofi Boy - Chill', type: 'youtube', thumb: 'https://img.youtube.com/vi/7NOSDKb0HlU/mqdefault.jpg' },
  { id: 'F1B9Fk_SgI0', title: 'Ghibli Piano', type: 'youtube', thumb: 'https://img.youtube.com/vi/F1B9Fk_SgI0/mqdefault.jpg' },
  { id: 'lP26UCnoH9s', title: 'Cozy Cabin Rain', type: 'youtube', thumb: 'https://img.youtube.com/vi/lP26UCnoH9s/mqdefault.jpg' },
  { id: 'aGSYKFb_zxg', title: '4K Anime City', type: 'youtube', thumb: 'https://img.youtube.com/vi/aGSYKFb_zxg/mqdefault.jpg' }
];

let currentBg = null;

function initBg() {
  injectBgContainer();
  injectBgModal();
  loadBg();
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
  const modalHTML = `
    <div class="bg-modal-overlay" id="bg-modal-overlay" onclick="closeBgModal(event)">
      <div class="bg-modal" onclick="event.stopPropagation()">
        <div class="bg-modal-header">
          <div class="bg-modal-title">🖼️ Hình nền</div>
          <button class="bg-modal-close" onclick="closeBgModal()">✕</button>
        </div>
        <div class="bg-modal-body">
          <div class="bg-input-group">
            <label class="bg-input-label">Link ảnh / GIF / YouTube</label>
            <div class="bg-input-wrapper">
              <span class="bg-input-icon">▶</span>
              <input type="text" class="bg-input" id="bg-input-url" placeholder="https://www.youtube.com/watch?v=..." oninput="handleUrlInput()" />
            </div>
            <div id="bg-input-feedback" style="font-size:12px; color:var(--success); margin-top:8px; display:none;"></div>
          </div>
          
          <div class="bg-presets-title">Hoặc chọn Preset (Study with me)</div>
          <div class="bg-preset-grid" id="bg-preset-grid">
            ${PRESETS.map(p => `
              <div class="bg-preset-item" id="preset-${p.id}" onclick="selectPreset('${p.id}')">
                <img src="${p.thumb}" alt="${p.title}" />
                <div class="bg-preset-label">${p.title}</div>
              </div>
            `).join('')}
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
  document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function openBgModal(e) {
  if (e) e.preventDefault();
  document.getElementById('bg-modal-overlay').classList.add('show');
  
  // Highlight current preset if it's one of them
  document.querySelectorAll('.bg-preset-item').forEach(el => el.classList.remove('active'));
  if (currentBg && currentBg.type === 'youtube') {
    const el = document.getElementById('preset-' + currentBg.value);
    if (el) el.classList.add('active');
  }
}

function closeBgModal(e) {
  if (e && e.target.id !== 'bg-modal-overlay') return;
  document.getElementById('bg-modal-overlay').classList.remove('show');
}

function parseYoutubeUrl(url) {
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
  const match = url.match(regExp);
  return (match && match[2].length === 11) ? match[2] : null;
}

function handleUrlInput() {
  const url = document.getElementById('bg-input-url').value.trim();
  const feedback = document.getElementById('bg-input-feedback');
  if (!url) {
    feedback.style.display = 'none';
    return;
  }
  const ytId = parseYoutubeUrl(url);
  if (ytId) {
    feedback.textContent = '✓ Nhận diện link YouTube hợp lệ';
    feedback.style.color = 'var(--success)';
    feedback.style.display = 'block';
  } else if (url.match(/\.(jpeg|jpg|gif|png)$/i)) {
    feedback.textContent = '✓ Nhận diện link Ảnh hợp lệ';
    feedback.style.color = 'var(--success)';
    feedback.style.display = 'block';
  } else {
    feedback.textContent = 'Link có vẻ không phải YouTube hoặc định dạng ảnh cơ bản, nhưng vẫn có thể thử!';
    feedback.style.color = 'var(--warning)';
    feedback.style.display = 'block';
  }
}

function selectPreset(id) {
  document.querySelectorAll('.bg-preset-item').forEach(el => el.classList.remove('active'));
  document.getElementById('preset-' + id).classList.add('active');
  document.getElementById('bg-input-url').value = 'https://youtube.com/watch?v=' + id;
  handleUrlInput();
}

function applyBgFromInput() {
  const url = document.getElementById('bg-input-url').value.trim();
  if (!url) return;
  
  const ytId = parseYoutubeUrl(url);
  let config = null;
  if (ytId) {
    config = { type: 'youtube', value: ytId };
  } else {
    config = { type: 'image', value: url };
  }
  
  saveAndRenderBg(config);
  closeBgModal();
}

function clearBg() {
  saveAndRenderBg(null);
  closeBgModal();
}

function saveAndRenderBg(config) {
  currentBg = config;
  if (config) {
    localStorage.setItem('toeic_bg', JSON.stringify(config));
  } else {
    localStorage.removeItem('toeic_bg');
  }
  renderBg();
}

function loadBg() {
  try {
    const stored = localStorage.getItem('toeic_bg');
    if (stored) {
      currentBg = JSON.parse(stored);
      renderBg();
    }
  } catch(e) {}
}

function renderBg() {
  const container = document.getElementById('global-bg-container');
  if (!container) return;
  
  container.innerHTML = '';
  container.style.backgroundImage = 'none';
  
  if (!currentBg) {
    // Default mode, rely on .page-bg in CSS
    container.style.opacity = '0';
    return;
  }
  
  container.style.opacity = '1';
  
  if (currentBg.type === 'youtube') {
    // Add overlay to darken video slightly
    container.style.backgroundColor = '#000';
    const overlay = document.createElement('div');
    overlay.style.position = 'absolute';
    overlay.style.inset = '0';
    overlay.style.backgroundColor = 'rgba(11, 13, 23, 0.65)';
    overlay.style.zIndex = '1';
    
    const iframe = document.createElement('iframe');
    iframe.src = \`https://www.youtube.com/embed/\${currentBg.value}?autoplay=1&mute=1&controls=0&loop=1&playlist=\${currentBg.value}&modestbranding=1&showinfo=0\`;
    iframe.frameBorder = '0';
    iframe.allow = 'autoplay; encrypted-media';
    
    container.appendChild(iframe);
    container.appendChild(overlay);
  } else if (currentBg.type === 'image') {
    container.style.backgroundImage = \`linear-gradient(rgba(11, 13, 23, 0.7), rgba(11, 13, 23, 0.7)), url('\${currentBg.value}')\`;
  }
}
