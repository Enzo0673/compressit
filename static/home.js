/* =========================================================
   CompressIt — home.js
   - Drag & drop global sur la page d'accueil (détection type → redirection)
   - Historique des outils récents (localStorage)
   ========================================================= */

(function () {

  // ── Mapping extension → outil ──────────────────────────────────────────────
  const EXT_MAP = {
    // PDF
    pdf:  '/tool/compress-pdf',
    // Images
    jpg: '/tool/compress-image', jpeg: '/tool/compress-image',
    png: '/tool/compress-image', webp: '/tool/compress-image',
    gif: '/tool/compress-image', bmp:  '/tool/compress-image',
    tiff:'/tool/compress-image', tif:  '/tool/compress-image',
    // Vidéo
    mp4: '/tool/compress-video', mov: '/tool/compress-video',
    avi: '/tool/compress-video', mkv: '/tool/compress-video',
    webm:'/tool/compress-video',
    // Archives
    zip: '/tool/compress-archive', '7z': '/tool/compress-archive',
    rar: '/tool/compress-archive', tar: '/tool/compress-archive',
    gz:  '/tool/compress-archive', bz2: '/tool/compress-archive',
    zst: '/tool/compress-archive',
    // Office
    doc: '/tool/office-to-pdf', docx: '/tool/office-to-pdf',
    xls: '/tool/office-to-pdf', xlsx: '/tool/office-to-pdf',
    ppt: '/tool/office-to-pdf', pptx: '/tool/office-to-pdf',
  };

  function getExt(filename) {
    return filename.split('.').pop().toLowerCase();
  }

  // ── Drag & drop global ─────────────────────────────────────────────────────
  const overlay = document.createElement('div');
  overlay.id = 'drop-overlay';
  overlay.innerHTML = `
    <div class="drop-overlay-inner">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
        <path d="M32 12V44M32 12L20 24M32 12L44 24" stroke="#6366f1" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M12 52H52" stroke="#6366f1" stroke-width="4" stroke-linecap="round"/>
      </svg>
      <p class="drop-overlay-title">Déposez votre fichier</p>
      <p class="drop-overlay-sub" id="dropOverlaySub">Détection automatique de l'outil</p>
    </div>
  `;
  document.body.appendChild(overlay);

  let dragCounter = 0;

  document.addEventListener('dragenter', e => {
    if (!e.dataTransfer.types.includes('Files')) return;
    dragCounter++;
    // Détecter le type si possible
    const items = Array.from(e.dataTransfer.items || []);
    const file = items.find(i => i.kind === 'file');
    if (file) {
      const name = file.getAsFile ? (file.getAsFile()?.name || '') : '';
      const ext = getExt(name);
      const tool = EXT_MAP[ext];
      document.getElementById('dropOverlaySub').textContent =
        tool ? `→ ${toolLabel(tool)}` : 'Déposez pour choisir l\'outil';
    }
    overlay.classList.add('active');
  });

  document.addEventListener('dragleave', e => {
    dragCounter--;
    if (dragCounter <= 0) { dragCounter = 0; overlay.classList.remove('active'); }
  });

  document.addEventListener('dragover', e => e.preventDefault());

  document.addEventListener('drop', e => {
    e.preventDefault();
    dragCounter = 0;
    overlay.classList.remove('active');
    const file = e.dataTransfer.files[0];
    if (!file) return;
    const ext = getExt(file.name);
    const tool = EXT_MAP[ext];
    if (tool) {
      window.location.href = tool;
    } else {
      // Pas de mapping → afficher un toast
      showToast(`Format .${ext} non reconnu — choisissez un outil manuellement`);
    }
  });

  function toolLabel(path) {
    const labels = {
      '/tool/compress-pdf':    'Compresser PDF',
      '/tool/compress-image':  'Compresser image',
      '/tool/compress-video':  'Compresser vidéo',
      '/tool/compress-archive':'Compresser archive',
      '/tool/office-to-pdf':   'Word/Excel → PDF',
    };
    return labels[path] || path;
  }

  function showToast(msg) {
    const t = document.createElement('div');
    t.className = 'home-toast';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.classList.add('visible'), 10);
    setTimeout(() => { t.classList.remove('visible'); setTimeout(() => t.remove(), 300); }, 3000);
  }

  // ── Historique des outils récents ──────────────────────────────────────────
  const HISTORY_KEY = 'compressit-history';
  const MAX_HISTORY = 5;

  function getHistory() {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); }
    catch { return []; }
  }

  function saveToHistory(toolPath, toolName, toolIcon) {
    let h = getHistory().filter(x => x.path !== toolPath);
    h.unshift({ path: toolPath, name: toolName, icon: toolIcon, ts: Date.now() });
    h = h.slice(0, MAX_HISTORY);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(h));
  }

  // Enregistrer la visite d'un outil quand on clique sur une carte
  document.querySelectorAll('.tool-card[href]').forEach(card => {
    card.addEventListener('click', () => {
      const path = card.getAttribute('href');
      const name = card.querySelector('.tool-name')?.textContent || path;
      const icon = card.querySelector('.tool-icon')?.textContent || '🔧';
      saveToHistory(path, name, icon);
    });
  });

  // Afficher l'historique
  function renderHistory() {
    const h = getHistory();
    if (h.length === 0) return;

    const section = document.createElement('section');
    section.className = 'tool-section history-section';
    section.innerHTML = `
      <div class="section-header">
        <span class="section-icon" style="background:#f1f5f9">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="10" r="7" stroke="#64748b" stroke-width="1.5" fill="none"/>
            <path d="M10 6v4l3 2" stroke="#64748b" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </span>
        <h2 class="section-title" style="color:var(--text-muted);font-size:1rem">Récents</h2>
        <button id="clearHistory" style="margin-left:auto;background:none;border:none;color:var(--text-muted);font-size:0.8rem;cursor:pointer;opacity:0.6">Effacer</button>
      </div>
      <div class="tools-grid" id="historyGrid"></div>
    `;

    const grid = section.querySelector('#historyGrid');
    h.forEach(item => {
      const card = document.createElement('a');
      card.className = 'tool-card';
      card.href = item.path;
      card.innerHTML = `
        <span class="tool-icon">${item.icon}</span>
        <span class="tool-name">${item.name}</span>
      `;
      card.addEventListener('click', () => saveToHistory(item.path, item.name, item.icon));
      grid.appendChild(card);
    });

    section.querySelector('#clearHistory').addEventListener('click', e => {
      e.preventDefault();
      localStorage.removeItem(HISTORY_KEY);
      section.remove();
    });

    // Insérer avant la première section outil
    const firstSection = document.querySelector('.tool-section');
    if (firstSection) firstSection.parentNode.insertBefore(section, firstSection);
  }

  renderHistory();

})();
