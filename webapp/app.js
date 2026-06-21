/**
 * ReciclaBot — Webapp TF.js Inference
 * Suporta: Webcam ao vivo + upload de imagem
 *
 * Arquitetura: MobileNetV2 com Transfer Learning (ImageNet weights)
 * Dataset: Super Dataset = TrashNet + Garbage Real World (Kaggle)
 *
 * A ordem das classes é a ordem alfabética usada pelo Keras ao escanear
 * o diretório do super dataset (image_dataset_from_directory).
 */

// ── Constants ──────────────────────────────────────────────────────────────
const CLASSES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash'];

const CLASS_META = {
  cardboard: {
    label: '📦 Papelão',
    icon:  '📦',
    color: '#fbbf24',
    tip:   'Desmonte as caixas. Remova fitas adesivas e plásticos.',
  },
  glass: {
    label: '🫙 Vidro',
    icon:  '🫙',
    color: '#a78bfa',
    tip:   'Separe por cor. Nunca misture com cerâmica ou espelhos.',
  },
  metal: {
    label: '🥫 Metal',
    icon:  '🥫',
    color: '#fb923c',
    tip:   'Amasse as latas para economizar espaço. O alumínio é infinitamente reciclável!',
  },
  paper: {
    label: '📄 Papel',
    icon:  '📄',
    color: '#34d399',
    tip:   'Mantenha seco e limpo. Papel picado não deve ser misturado.',
  },
  plastic: {
    label: '♻️ Plástico',
    icon:  '🧴',
    color: '#00c8ff',
    tip:   'Lave antes de reciclar. Remova as tampas quando possível.',
  },
  trash: {
    label: '🗑️ Lixo Geral',
    icon:  '🗑️',
    color: '#f87171',
    tip:   'Não reciclável. Tente reduzir o uso desta categoria!',
  },
};

// ⚠️ NORMALIZAÇÃO: O modelo usa Rescaling(1/127.5, offset=-1) internamente
// (padrão MobileNetV2 — escala [-1, 1]). Essa camada está DENTRO do modelo
// salvo, então o JS passa os pixels brutos [0, 255] normalmente.
const IMG_SIZE   = 224;
const MODEL_PATH = '../modelo_tfjs/model.json';

// ── State ──────────────────────────────────────────────────────────────────
let model       = null;
let cameraOn    = false;
let loopRunning = false;
let stream      = null;
let activeTab   = 'camera';

// ── DOM refs ───────────────────────────────────────────────────────────────
const elStatus          = document.getElementById('model-status');
const elWebcam          = document.getElementById('webcam');
const elCanvas          = document.getElementById('canvas-preview');
const elBtnCamera       = document.getElementById('btn-camera');
const elScanLine        = document.getElementById('scan-line');
const elVideoPlaceholder = document.getElementById('video-placeholder');

const elIdle    = document.getElementById('result-idle');
const elLoading = document.getElementById('result-loading');
const elOutput  = document.getElementById('result-output');
const elDivider = document.getElementById('bars-divider');
const elBarsSection = document.getElementById('bars-section');

const elResultIcon  = document.getElementById('result-icon');
const elResultLabel = document.getElementById('result-label');
const elResultConf  = document.getElementById('result-conf');
const elResultTip   = document.getElementById('result-tip');
const elBarsList    = document.getElementById('bars-list');

// ── Floating background emojis ─────────────────────────────────────────────
(function () {
  const items = [
    ["♻️",  4, 22, 0.0,  1.55, 12], ["📄", 16, 28, 3.5,  1.25, -8],
    ["🥫", 31, 19, 1.2,  1.70, 15], ["🍾", 47, 25, 5.8,  1.40, -5],
    ["📦", 62, 21, 2.1,  1.85,-18], ["♻️", 75, 30, 0.7,  1.10, 10],
    ["📄", 88, 17, 4.3,  1.55, -6], ["🥫",  9, 26, 8.0,  1.75,-12],
    ["♻️", 38, 32, 4.0,  1.45, -9], ["📄", 53, 18, 7.2,  1.60,  7],
  ];
  const bg = document.getElementById('waste-bg');
  if (bg) {
    items.forEach(([emoji, left, dur, delay, size, rot]) => {
      const s = document.createElement('span');
      s.textContent = emoji;
      s.style.cssText = `left:${left}vw;font-size:${size}rem;animation-duration:${dur}s;animation-delay:-${delay}s;--rs:${rot}deg;--re:${-rot}deg;`;
      bg.appendChild(s);
    });
  }
})();

// ── Model loading ──────────────────────────────────────────────────────────
async function loadModel() {
  setStatus('loading', '⏳ Carregando modelo…');
  try {
    model = await tf.loadLayersModel(MODEL_PATH);
    // Warm up: run a dummy tensor through the model so first real inference is fast
    tf.tidy(() => {
      const dummy = tf.zeros([1, IMG_SIZE, IMG_SIZE, 3]);
      model.predict(dummy);
    });
    setStatus('ready', '🟢 Modelo Pronto');
    buildBars(); // init confidence bars
  } catch (err) {
    console.error('Erro ao carregar modelo:', err);
    setStatus('error', '❌ Erro ao carregar modelo');
  }
}

function setStatus(type, text) {
  elStatus.className = `status-badge ${type}`;
  elStatus.innerHTML = `<span class="status-dot"></span> ${text}`;
}

// ── Tab switching ──────────────────────────────────────────────────────────
window.switchTab = function (tab) {
  activeTab = tab;

  // Update buttons
  document.getElementById('tab-camera').classList.toggle('active', tab === 'camera');
  document.getElementById('tab-upload').classList.toggle('active', tab === 'upload');

  // Show/hide panels
  document.getElementById('panel-camera').classList.toggle('hidden', tab !== 'camera');
  document.getElementById('panel-upload').classList.toggle('hidden', tab !== 'upload');

  // Stop camera loop if switching to upload
  if (tab === 'upload') {
    loopRunning = false;
    showIdle();
  } else if (tab === 'camera' && cameraOn) {
    loopRunning = true;
    requestAnimationFrame(inferenceLoop);
  }
};

// ── Camera ─────────────────────────────────────────────────────────────────
window.toggleCamera = async function () {
  if (!cameraOn) {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      elWebcam.srcObject = stream;
      await new Promise(r => { elWebcam.onloadedmetadata = r; });
      elWebcam.classList.add('active');
      elVideoPlaceholder.classList.add('hidden');
      elScanLine.classList.add('active');
      elBtnCamera.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/></svg> Parar câmera`;
      cameraOn = true;

      if (model) {
        loopRunning = true;
        requestAnimationFrame(inferenceLoop);
      }
    } catch (err) {
      console.error('Erro na câmera:', err);
      setStatus('error', '❌ Câmera não acessível');
    }
  } else {
    stopCamera();
    showIdle();
  }
};

function stopCamera() {
  loopRunning = false;
  cameraOn = false;
  if (stream) {
    stream.getTracks().forEach(t => t.stop());
    stream = null;
  }
  elWebcam.srcObject = null;
  elWebcam.classList.remove('active');
  elVideoPlaceholder.classList.remove('hidden');
  elScanLine.classList.remove('active');
  elBtnCamera.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg> Ativar câmera`;
}

// ── Camera inference loop ──────────────────────────────────────────────────
function inferenceLoop() {
  if (!loopRunning || !model || !cameraOn) return;

  tf.tidy(() => {
    const tensor = tf.browser
      .fromPixels(elWebcam)
      .resizeBilinear([IMG_SIZE, IMG_SIZE])
      .cast('float32')
      .expandDims(0);

    const preds = model.predict(tensor);
    const probs = Array.from(preds.dataSync());
    updateResult(probs, /* animate= */ false);
  });

  requestAnimationFrame(inferenceLoop);
}

// ── Upload flow ────────────────────────────────────────────────────────────
window.onDragOver = function (e) {
  e.preventDefault();
  document.getElementById('upload-zone').classList.add('drag-over');
};

window.onDragLeave = function () {
  document.getElementById('upload-zone').classList.remove('drag-over');
};

window.onDrop = function (e) {
  e.preventDefault();
  document.getElementById('upload-zone').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) loadUploadFile(file);
};

window.onFileSelect = function (e) {
  const file = e.target.files[0];
  if (file) loadUploadFile(file);
};

function loadUploadFile(file) {
  const reader = new FileReader();
  reader.onload = (ev) => {
    const img = document.getElementById('upload-img');
    img.src = ev.target.result;
    document.getElementById('upload-zone').classList.add('hidden');
    document.getElementById('upload-preview-wrap').classList.remove('hidden');
    showIdle();
  };
  reader.readAsDataURL(file);
}

window.clearUpload = function () {
  const fi = document.getElementById('file-input');
  fi.value = '';
  document.getElementById('upload-img').src = '';
  document.getElementById('upload-zone').classList.remove('hidden');
  document.getElementById('upload-preview-wrap').classList.add('hidden');
  document.getElementById('upload-scan').classList.remove('active');
  showIdle();
};

window.classifyUpload = async function () {
  if (!model) {
    setStatus('error', '⚠️ Modelo ainda não carregado');
    return;
  }
  const img = document.getElementById('upload-img');
  if (!img.src) return;

  showLoading();
  document.getElementById('upload-scan').classList.add('active');

  // Small delay so spinner is visible
  await new Promise(r => setTimeout(r, 300));

  const probs = tf.tidy(() => {
    const tensor = tf.browser
      .fromPixels(img)
      .resizeBilinear([IMG_SIZE, IMG_SIZE])
      .cast('float32')
      .expandDims(0);

    return Array.from(model.predict(tensor).dataSync());
  });

  document.getElementById('upload-scan').classList.remove('active');
  updateResult(probs, /* animate= */ true);
};

// ── UI helpers ─────────────────────────────────────────────────────────────
function showIdle() {
  elIdle.classList.remove('hidden');
  elLoading.classList.add('hidden');
  elOutput.classList.add('hidden');
  elDivider.style.display = 'none';
  elBarsSection.style.display = 'none';
}

function showLoading() {
  elIdle.classList.add('hidden');
  elLoading.classList.remove('hidden');
  elOutput.classList.add('hidden');
  elDivider.style.display = 'none';
  elBarsSection.style.display = 'none';
}

function updateResult(probs, animate) {
  // Find top class
  let topIdx = 0;
  probs.forEach((p, i) => { if (p > probs[topIdx]) topIdx = i; });

  const topClass = CLASSES[topIdx];
  const meta = CLASS_META[topClass];
  const conf = (probs[topIdx] * 100).toFixed(1);

  // Update result card
  elResultIcon.textContent = meta.icon;
  elResultLabel.textContent = meta.label;
  elResultLabel.style.color = meta.color;
  elResultConf.textContent = `${conf}%`;
  elResultConf.style.color = meta.color;
  elResultTip.style.borderColor = meta.color;
  elResultTip.innerHTML = `💡 <strong>Dica:</strong> ${meta.tip}`;

  elIdle.classList.add('hidden');
  elLoading.classList.add('hidden');
  elOutput.classList.remove('hidden');
  elDivider.style.display = '';
  elBarsSection.style.display = '';

  // Update bars
  updateBars(probs, animate);
}

function buildBars() {
  elBarsList.innerHTML = '';
  CLASSES.forEach(cls => {
    const meta = CLASS_META[cls];
    const row = document.createElement('div');
    row.className = 'bar-row';
    row.id = `bar-row-${cls}`;
    row.innerHTML = `
      <div class="bar-label-row">
        <span>${meta.label}</span>
        <span id="bar-pct-${cls}">0%</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" id="bar-fill-${cls}" style="width:0%;background:${meta.color};"></div>
      </div>
    `;
    elBarsList.appendChild(row);
  });
}

function updateBars(probs, animate) {
  // Sort by probability descending for visual ordering
  const sorted = CLASSES
    .map((cls, i) => ({ cls, prob: probs[i] }))
    .sort((a, b) => b.prob - a.prob);

  sorted.forEach(({ cls, prob }, i) => {
    const pct = (prob * 100).toFixed(1);
    const fill = document.getElementById(`bar-fill-${cls}`);
    const pctEl = document.getElementById(`bar-pct-${cls}`);

    if (fill && pctEl) {
      pctEl.textContent = `${pct}%`;
      if (animate) {
        fill.style.animation = 'none';
        fill.style.width = '0%';
        // Force reflow
        void fill.offsetWidth;
        fill.style.animation = '';
        fill.style.setProperty('--delay', `${i * 0.08}s`);
      }
      fill.style.width = `${pct}%`;
    }
  });
}

// ── Init ───────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  buildBars();
  loadModel();
});
