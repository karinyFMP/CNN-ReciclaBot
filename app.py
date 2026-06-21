"""
TrashNet CNN Waste Classifier — Streamlit App
=============================================
Mock implementation simulating a CNN trained on the TrashNet dataset.
Run with: python -m streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import random
import time
from PIL import Image
import io
import base64

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ReciclaBot",
    page_icon="♻️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# MOCK MODEL — simulates CNN inference
# ─────────────────────────────────────────────
CATEGORIES = {
    "♻️ Plástico": {"color": "#00c8ff", "icon": "🧴", "tip": "Lave antes de reciclar. Remova as tampas quando possível."},
    "🫙 Vidro":    {"color": "#a78bfa", "icon": "🍶", "tip": "Separe por cor. Nunca misture com cerâmica ou espelhos."},
    "🔩 Metal":    {"color": "#fb923c", "icon": "🥫", "tip": "Amasse as latas para economizar espaço. O alumínio é infinitamente reciclável!"},
    "📄 Papel":    {"color": "#34d399", "icon": "📰", "tip": "Mantenha seco e limpo. Papel picado não deve ser misturado."},
    "📦 Papelão":  {"color": "#fbbf24", "icon": "📦", "tip": "Desmonte as caixas. Remova fitas adesivas e plásticos."},
    "🗑️ Geral":    {"color": "#f87171", "icon": "🚮", "tip": "Não reciclável. Tente reduzir o uso desta categoria primeiro!"},
}

def mock_cnn_predict(image: Image.Image) -> tuple[str, float, dict]:
    """
    Simulates CNN forward pass on the TrashNet dataset classes.
    Returns: (predicted_label, confidence_score, all_scores_dict)
    """
    # Simulate processing delay (mimics GPU inference time)
    time.sleep(random.uniform(1.2, 2.4))

    labels = list(CATEGORIES.keys())

    # Generate softmax-like distribution (one dominant class)
    dominant_idx = random.randint(0, len(labels) - 1)
    scores = [random.uniform(0.01, 0.08) for _ in labels]
    scores[dominant_idx] = random.uniform(0.65, 0.97)  # High confidence for top class

    # Normalize to sum ~1 (softmax approximation)
    total = sum(scores)
    scores = [round(s / total, 4) for s in scores]

    predicted_label = labels[dominant_idx]
    confidence = scores[dominant_idx]
    all_scores = dict(zip(labels, scores))

    return predicted_label, confidence, all_scores


# ─────────────────────────────────────────────
# FLOATING BACKGROUND — animated waste emojis
# ─────────────────────────────────────────────
def inject_floating_bg():
    """
    Injects 16 floating waste-emoji elements as a fixed, blurred background.
    Uses components.html (iframe) + a JS snippet that writes the layer into
    the parent document — the only way to bypass Streamlit's CSS sanitiser
    for position:fixed rules.
    """

    # (emoji, left-vw, duration-s, delay-s, font-size-rem, rot-start-deg)
    items = [
        # spread across full viewport width, staggered start times
        ("♻️", 4,  22, 0.0,  1.55, 12),
        ("📄", 16, 28, 3.5,  1.25, -8),
        ("🥫", 31, 19, 1.2,  1.70, 15),
        ("🍾", 47, 25, 5.8,  1.40, -5),
        ("📦", 62, 21, 2.1,  1.85,-18),
        ("♻️", 75, 30, 0.7,  1.10, 10),
        ("📄", 88, 17, 4.3,  1.55, -6),
        ("🥫", 93, 24, 6.5,  1.30, 20),
        ("🍾",  9, 26, 8.0,  1.75,-12),
        ("📦", 23, 20, 1.9,  1.15, 16),
        ("♻️", 38, 32, 4.0,  1.45, -9),
        ("📄", 53, 18, 7.2,  1.60,  7),
        ("🥫", 68, 23, 3.0,  1.25,-14),
        ("🍾", 80, 27, 5.0,  1.70, 11),
        ("📦", 11, 16, 9.1,  1.40, -3),
        ("♻️", 57, 29, 2.7,  1.85, 18),
    ]

    # Build JS that creates span elements and appends them to parent body
    span_js_lines = []
    for emoji, left, dur, delay, size, rot in items:
        span_js_lines.append(
            f"s=d.createElement('span');"
            f"s.textContent='{emoji}';"
            f"s.style.cssText='left:{left}vw;font-size:{size:.2f}rem;"
            f"animation-duration:{dur}s;animation-delay:-{delay}s;"
            f"--rs:{rot}deg;--re:{-rot}deg;';"
            f"bg.appendChild(s);"
        )

    spans_js = "\n        ".join(span_js_lines)

    html = f"""
    <script>
    (function() {{
      var d = window.parent.document;
      // Avoid duplicate injection on Streamlit hot-reloads
      if (d.getElementById('waste-bg-layer')) return;

      // Inject keyframe CSS into parent <head>
      var style = d.createElement('style');
      style.id = 'waste-bg-style';
      style.textContent = `
        #waste-bg-layer {{
          position: fixed !important;
          inset: 0 !important;
          z-index: 0 !important;
          pointer-events: none !important;
          overflow: hidden !important;
        }}
        #waste-bg-layer span {{
          position: absolute !important;
          bottom: -12% !important;
          display: block !important;
          opacity: 0.12 !important;
          filter: blur(2.5px) !important;
          user-select: none !important;
          animation-name: wbFloatUp !important;
          animation-timing-function: ease-in-out !important;
          animation-iteration-count: infinite !important;
        }}
        @keyframes wbFloatUp {{
          0%   {{ transform: translateY(0)      translateX(0)    rotate(var(--rs)); opacity:0;    }}
          7%   {{ opacity: 0.12; }}
          50%  {{ transform: translateY(-55vh)  translateX(16px) rotate(var(--re)); opacity:0.12; }}
          93%  {{ opacity: 0.12; }}
          100% {{ transform: translateY(-115vh) translateX(-8px) rotate(var(--rs)); opacity:0;    }}
        }}
      `;
      d.head.appendChild(style);

      // Create the container and all emoji spans
      var bg = d.createElement('div');
      bg.id = 'waste-bg-layer';
      bg.setAttribute('aria-hidden', 'true');
      var s;
      {spans_js}
      d.body.appendChild(bg);
    }})();
    </script>
    """

    # height=0 renders an invisible iframe; scrolling="no" prevents layout shift
    components.html(html, height=0, scrolling=False)





# ─────────────────────────────────────────────
# CUSTOM CSS — animations, glow effects, modern UI
# ─────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&family=Space+Grotesk:wght@400;700&display=swap');

    /* ── Global Reset & Background ── */
    html, body, [data-testid="stAppViewContainer"] {
        background: radial-gradient(ellipse at 20% 10%, #0f172a 0%, #060b18 60%, #0a0f1e 100%);
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] { background: #0d1424 !important; }
    .block-container { padding-top: 2rem !important; max-width: 780px !important; }

    /* ── Hero Title ── */
    .hero-title {
        text-align: center;
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2rem, 6vw, 3.2rem);
        font-weight: 700;
        background: linear-gradient(135deg, #00c8ff 0%, #a78bfa 50%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 4s ease-in-out infinite alternate;
        letter-spacing: -0.5px;
    }

    /* ── Keyframe: gradient title shift ── */
    @keyframes gradientShift {
        0%   { filter: hue-rotate(0deg);   }
        100% { filter: hue-rotate(40deg);  }
    }

    /* ── Keyframe: glow pulse on cards ── */
    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(0,200,255,0.15), 0 0 40px rgba(167,139,250,0.05); }
        50%       { box-shadow: 0 0 35px rgba(0,200,255,0.35), 0 0 70px rgba(167,139,250,0.20); }
    }

    /* ── Keyframe: upload area pulse ── */
    @keyframes uploadPulse {
        0%, 100% {
            border-color: rgba(0,200,255,0.4);
            box-shadow: 0 0 0 0 rgba(0,200,255,0.3);
        }
        50% {
            border-color: rgba(0,200,255,0.9);
            box-shadow: 0 0 0 12px rgba(0,200,255,0.0);
        }
    }

    /* ── Keyframe: spinner ring ── */
    @keyframes spinRing {
        to { transform: rotate(360deg); }
    }

    /* ── Keyframe: slide up on result ── */
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0);    }
    }

    /* ── Keyframe: icon bounce ── */
    @keyframes iconBounce {
        0%, 100% { transform: translateY(0) scale(1);    }
        40%       { transform: translateY(-8px) scale(1.12); }
        70%       { transform: translateY(-3px) scale(1.05); }
    }

    /* ── Keyframe: progress bar fill ── */
    @keyframes barFill {
        from { width: 0%; }
    }

    /* ── Keyframe: scanline on image ── */
    @keyframes scanline {
        0%   { top: -10%; }
        100% { top: 110%; }
    }

    /* ── Subtitle ── */
    .hero-sub {
        text-align: center;
        font-size: 0.95rem;
        color: #64748b;
        margin-top: -0.4rem;
        margin-bottom: 2rem;
        letter-spacing: 0.3px;
    }

    /* ── Card wrapper ── */
    .card {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 20px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.4rem;
        animation: glowPulse 3s ease-in-out infinite;
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease;
    }
    .card:hover { transform: translateY(-2px); }

    /* ── Upload area override ── */
    [data-testid="stFileUploader"] > div {
        border: 2px dashed rgba(0,200,255,0.5) !important;
        border-radius: 16px !important;
        background: rgba(0,200,255,0.03) !important;
        animation: uploadPulse 2.5s ease-in-out infinite !important;
        transition: background 0.3s ease;
        padding: 1.5rem !important;
    }
    [data-testid="stFileUploader"] > div:hover {
        background: rgba(0,200,255,0.08) !important;
    }
    [data-testid="stFileUploader"] label {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
    }

    /* ── Camera input override ── */
    [data-testid="stCameraInput"] > div {
        border: 2px dashed rgba(167,139,250,0.5) !important;
        border-radius: 16px !important;
        background: rgba(167,139,250,0.03) !important;
        transition: background 0.3s ease;
    }
    [data-testid="stCameraInput"] > div:hover {
        background: rgba(167,139,250,0.08) !important;
    }

    /* ── Analyzing loader ── */
    .analyzing-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        padding: 2rem;
        text-align: center;
    }
    .spin-ring {
        width: 60px;
        height: 60px;
        border: 4px solid rgba(0,200,255,0.15);
        border-top: 4px solid #00c8ff;
        border-radius: 50%;
        animation: spinRing 0.9s linear infinite;
    }
    .analyzing-text {
        font-size: 1.05rem;
        color: #94a3b8;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* ── Result card ── */
    .result-card {
        border-radius: 20px;
        padding: 2rem;
        margin-top: 1.2rem;
        animation: slideUp 0.6s ease forwards;
        border: 1px solid;
        position: relative;
        overflow: hidden;
    }
    .result-icon {
        font-size: 3.5rem;
        display: block;
        text-align: center;
        animation: iconBounce 1.8s ease infinite;
        margin-bottom: 0.5rem;
    }
    .result-label {
        text-align: center;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .confidence-text {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 900;
        margin-bottom: 0.6rem;
    }
    .tip-box {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 0.7rem 1rem;
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 0.8rem;
        border-left: 3px solid;
    }

    /* ── Score bar row ── */
    .score-row { margin: 0.35rem 0; }
    .score-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        color: #94a3b8;
        margin-bottom: 3px;
    }
    .score-track {
        background: rgba(255,255,255,0.05);
        border-radius: 999px;
        height: 8px;
        overflow: hidden;
    }
    .score-fill {
        height: 100%;
        border-radius: 999px;
        animation: barFill 0.8s ease forwards;
        animation-delay: var(--delay);
    }

    /* ── Tab styling ── */
    [data-testid="stTabs"] [role="tab"] {
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 0.5rem 1.2rem !important;
        transition: color 0.2s ease;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: #00c8ff !important;
        border-bottom: 2px solid #00c8ff !important;
        background: rgba(0,200,255,0.06) !important;
    }

    /* ── Streamlit button ── */
    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, #00c8ff, #a78bfa) !important;
        color: #060b18 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 2rem !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px !important;
        transition: opacity 0.2s ease, transform 0.15s ease !important;
        box-shadow: 0 4px 20px rgba(0,200,255,0.25) !important;
    }
    [data-testid="stButton"] > button:hover {
        opacity: 0.88 !important;
        transform: scale(1.02) !important;
    }

    /* ── Divider ── */
    hr { border-color: rgba(255,255,255,0.06) !important; }

    /* ── Image preview ── */
    .img-preview-wrap {
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .img-preview-wrap::after {
        content: '';
        position: absolute;
        left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, transparent, #00c8ff, transparent);
        animation: scanline 2s linear infinite;
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        font-size: 0.78rem;
        color: #334155;
        padding: 2rem 0 1rem;
    }

    /* ==========================================================
       Info / Welcome Card — "Como funciona"
       ========================================================== */

    /* ── Outer card ── */
    .info-card {
      position: relative;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(0, 200, 255, 0.14);
      border-radius: 20px;
      padding: 1.8rem;
      backdrop-filter: blur(16px);
      overflow: hidden;
      box-shadow:
        -4px 0   24px rgba(0, 200, 255, 0.08),
         4px 0   24px rgba(52, 211, 153, 0.06),
         0   12px 40px rgba(0, 0, 0, 0.35);
      animation: infoGlow 4s ease-in-out infinite alternate;
      transition: transform 0.3s ease;
      margin-bottom: 2rem;
    }
    .info-card:hover { transform: translateY(-2px); }

    /* Top-edge neon accent line */
    .info-card::before {
      content: '';
      position: absolute;
      top: 0; left: 10%; right: 10%;
      height: 2px;
      background: linear-gradient(90deg,
        transparent,
        rgba(0, 200, 255, 0.6) 30%,
        rgba(52, 211, 153, 0.6) 70%,
        transparent
      );
      border-radius: 999px;
    }

    @keyframes infoGlow {
      from {
        box-shadow:
          -4px 0 24px rgba(0,200,255,0.08),
           4px 0 24px rgba(52,211,153,0.06),
           0  12px 40px rgba(0,0,0,0.35);
      }
      to {
        box-shadow:
          -4px 0 40px rgba(0,200,255,0.18),
           4px 0 40px rgba(52,211,153,0.14),
           0  16px 50px rgba(0,0,0,0.40);
      }
    }

    /* ── Intro row (icon + text) ── */
    .info-intro {
      display: flex;
      gap: 1.1rem;
      align-items: flex-start;
    }

    .info-intro-icon {
      font-size: 2.2rem;
      line-height: 1;
      flex-shrink: 0;
      margin-top: 2px;
      animation: iconFloat 3.5s ease-in-out infinite;
      filter: drop-shadow(0 0 10px rgba(0, 200, 255, 0.4));
    }
    
    @keyframes iconFloat {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-5px); }
    }

    .info-title {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 1rem;
      font-weight: 600;
      color: #f8fafc;
      margin-top: 0;
      margin-bottom: 0.55rem;
    }

    .info-body {
      font-size: 0.875rem;
      line-height: 1.7;
      color: #94a3b8;
      margin: 0;
    }
    .info-body strong { color: #f8fafc; }
    .info-body em     { color: #34d399; font-style: normal; font-weight: 600; }

    /* Category pill tags */
    .info-tag {
      display: inline-block;
      background: rgba(0, 200, 255, 0.07);
      border: 1px solid rgba(0, 200, 255, 0.18);
      border-radius: 6px;
      padding: 0.08rem 0.5rem;
      font-size: 0.8rem;
      color: #00c8ff;
      font-weight: 500;
      margin: 0.15rem 0.15rem 0 0;
      white-space: nowrap;
      transition: background 0.3s ease, border-color 0.3s ease;
    }
    .info-tag:hover {
      background: rgba(0, 200, 255, 0.14);
      border-color: rgba(0, 200, 255, 0.4);
    }

    /* ── Divider ── */
    .info-divider {
      height: 1px;
      background: linear-gradient(90deg,
        transparent,
        rgba(255,255,255,0.06) 20%,
        rgba(255,255,255,0.06) 80%,
        transparent
      );
      margin: 1.4rem 0;
    }

    /* ── Steps header label ── */
    .info-steps-label {
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #64748b;
      margin-bottom: 1.1rem;
    }

    /* ── Step grid ── */
    .info-steps {
      list-style: none;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.6rem;
      padding: 0;
      margin: 0;
    }

    /* ── Single step card ── */
    .info-step {
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 1rem;
      padding: 1.6rem 0.8rem 1.4rem;
      background: rgba(255,255,255,0.02);
      border: 1px solid rgba(255,255,255,0.05);
      border-radius: 12px;
      transition: background 0.3s ease, border-color 0.3s ease, transform 0.3s ease;
    }
    .info-step:hover {
      background: rgba(0,200,255,0.04);
      border-color: rgba(0,200,255,0.18);
      transform: translateY(-3px);
    }

    /* Step number badge */
    .step-num {
      position: absolute;
      top: 0.45rem; right: 0.55rem;
      font-size: 0.62rem;
      font-weight: 800;
      color: #475569;
      font-family: 'Space Grotesk', sans-serif;
    }

    /* ── Step icon circles ── */
    .step-circle {
      width: 46px; height: 46px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: box-shadow 0.3s ease;
    }
    .step-circle svg { width: 20px; height: 20px; }

    .step-1 {
      background: rgba(0, 200, 255, 0.10);
      border: 1px solid rgba(0, 200, 255, 0.28);
      color: #00c8ff;
      animation: stepGlowCyan 3s ease-in-out infinite alternate;
    }
    .info-step:hover .step-1 { box-shadow: 0 0 28px rgba(0,200,255,0.30); }

    .step-2 {
      background: rgba(167, 139, 250, 0.10);
      border: 1px solid rgba(167, 139, 250, 0.28);
      color: #a78bfa;
      animation: stepGlowViolet 3s ease-in-out infinite alternate;
    }
    .info-step:hover .step-2 { box-shadow: 0 0 28px rgba(167,139,250,0.30); }

    .step-3 {
      background: rgba(52, 211, 153, 0.10);
      border: 1px solid rgba(52, 211, 153, 0.28);
      color: #34d399;
      animation: stepGlowGreen 3s ease-in-out infinite alternate;
    }
    .info-step:hover .step-3 { box-shadow: 0 0 28px rgba(52,211,153,0.30); }

    @keyframes stepGlowCyan   { from { box-shadow: 0 0 10px rgba(0,200,255,0.08);   } to { box-shadow: 0 0 22px rgba(0,200,255,0.22);   } }
    @keyframes stepGlowViolet { from { box-shadow: 0 0 10px rgba(167,139,250,0.08); } to { box-shadow: 0 0 22px rgba(167,139,250,0.22); } }
    @keyframes stepGlowGreen  { from { box-shadow: 0 0 10px rgba(52,211,153,0.08);  } to { box-shadow: 0 0 22px rgba(52,211,153,0.22);  } }

    /* ── Step text ── */
    .step-text { display: flex; flex-direction: column; gap: 0.2rem; }
    .step-text strong { font-size: 0.82rem; font-weight: 700; color: #f8fafc; line-height: 1.2; }
    .step-text span   { font-size: 0.73rem; color: #94a3b8; line-height: 1.4; }

    /* ── Mobile: stack vertically ── */
    @media (max-width: 520px) {
      .info-steps { grid-template-columns: 1fr; gap: 0.5rem; }
      .info-step  { flex-direction: row; text-align: left; padding: 0.85rem 1rem; gap: 0.9rem; }
      .step-text  { align-items: flex-start; }
      .info-intro { flex-direction: column; gap: 0.6rem; }
    }

    /* ── Streamlit File Uploader Override (To match custom drop-zone) ── */
    [data-testid="stFileUploaderDropzone"] {
        border: 2px dashed rgba(0, 200, 255, 0.35) !important;
        border-radius: 12px !important;
        background: transparent !important;
        transition: border-color 0.3s, background 0.3s !important;
        animation: uploadPulse 2.8s ease-in-out infinite !important;
        padding: 2.5rem 1.5rem !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    [data-testid="stFileUploaderDropzone"]:hover,
    [data-testid="stFileUploaderDropzone"]:focus {
        border-color: #00c8ff !important;
        background: rgba(0, 200, 255, 0.05) !important;
    }
    @keyframes uploadPulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(0, 200, 255, 0.20); }
        50% { box-shadow: 0 0 0 10px rgba(0, 200, 255, 0.00); }
    }
    /* Hide the default small 'Drag and drop file here' text since we added custom text */
    [data-testid="stFileUploaderDropzoneInstructions"] {
        opacity: 0.8;
    }
    [data-testid="stFileUploaderDropzoneIcon"] {
        color: #00c8ff !important;
    }

    /* ── Hide Streamlit Header (Deploy, Hamburger Menu, etc) ── */
    [data-testid="stHeader"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER — render animated confidence bars
# ─────────────────────────────────────────────
def render_score_bars(all_scores: dict):
    """Renders an HTML bar chart for all category confidence scores."""
    bars_html = ""
    for i, (label, score) in enumerate(
        sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
    ):
        pct = round(score * 100, 1)
        color = CATEGORIES[label]["color"]
        delay = f"{i * 0.1}s"
        bars_html += f"""
        <div class="score-row">
            <div class="score-label">
                <span>{CATEGORIES[label]['icon']} {label}</span>
                <span>{pct}%</span>
            </div>
            <div class="score-track">
                <div class="score-fill"
                     style="width:{pct}%; background:{color}; --delay:{delay};">
                </div>
            </div>
        </div>
        """
    st.markdown(bars_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER — render result card
# ─────────────────────────────────────────────
def render_result(label: str, confidence: float, all_scores: dict):
    """Renders the animated prediction result card."""
    meta = CATEGORIES[label]
    color = meta["color"]
    icon  = meta["icon"]
    tip   = meta["tip"]
    pct   = round(confidence * 100, 1)

    st.markdown(f"""
    <div class="result-card"
         style="background: linear-gradient(135deg, {color}12, {color}05);
                border-color: {color}55;
                box-shadow: 0 0 40px {color}22;">
        <span class="result-icon">{icon}</span>
        <div class="result-label" style="color:{color};">{label}</div>
        <div class="confidence-text" style="color:{color};">{pct}%</div>
        <div style="text-align:center; color:#64748b; font-size:0.8rem;">
            Confiança do Modelo
        </div>
        <div class="tip-box" style="border-color:{color}88;">
            💡 <strong>Dica:</strong> {tip}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Score breakdown section
    st.markdown("#### 📊 Detalhamento das Previsões")
    render_score_bars(all_scores)


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    inject_css()
    inject_floating_bg()   # animated waste-emoji background layer

    # ── Hero Header ──
    st.markdown('<h1 class="hero-title">♻️ ReciclaBot</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">Visão Computacional · Classificação de Resíduos · Deep Learning</p>',
        unsafe_allow_html=True,
    )

    # ── Info / Welcome Card ──
    info_html = """
<section class="info-card">
  <div class="info-intro">
    <div class="info-intro-icon">🧠</div>
    <div>
      <h5 class="info-title">O que é esta ferramenta?</h5>
      <p class="info-body">
        Este classificador utiliza uma <strong>Rede Neural Convolucional (CNN)</strong> treinada no dataset <em>TrashNet</em> para identificar automaticamente o tipo de resíduo em uma imagem. O modelo reconhece as categorias:
        <br><br>
        <span class="info-tag">♻️ Plástico</span>
        <span class="info-tag">🫙 Vidro</span>
        <span class="info-tag">🔩 Metal</span>
        <span class="info-tag">📄 Papel</span>
        <span class="info-tag">📦 Papelão</span>
        <br><br>
        auxiliando na triagem correta para a <em>reciclagem</em>.
      </p>
    </div>
  </div>

  <div class="info-divider"></div>

  <div class="info-steps-wrap">
    <div class="info-steps-label">Como funciona</div>
    
    <ul class="info-steps">
      <li class="info-step">
        <span class="step-num">1</span>
        <div class="step-circle step-1">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M12 16V4m0 0L8 8m4-4 4 4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20 16v2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="step-text">
          <strong>Envie uma foto</strong>
          <span>Faça upload ou arraste uma imagem do resíduo</span>
        </div>
      </li>
      
      <li class="info-step">
        <span class="step-num">2</span>
        <div class="step-circle step-2">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="step-text">
          <strong>A IA processa</strong>
          <span>A CNN analisa padrões visuais em milissegundos</span>
        </div>
      </li>
      
      <li class="info-step">
        <span class="step-num">3</span>
        <div class="step-circle step-3">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M9 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="12" r="9"/>
          </svg>
        </div>
        <div class="step-text">
          <strong>Veja o resultado</strong>
          <span>Categoria, confiança e dica de descarte correto</span>
        </div>
      </li>
    </ul>
  </div>
</section>
"""
    import re
    clean_html = re.sub(r'^\s+', '', info_html, flags=re.MULTILINE)
    st.markdown(clean_html, unsafe_allow_html=True)

    # ── Image Input ──
    image_to_classify: Image.Image | None = None
    input_source = None

    st.markdown("**Arraste uma imagem de resíduo abaixo** — JPG, PNG, ou WEBP suportados.")
    uploaded_file = st.file_uploader(
        label="Enviar imagem",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        image_to_classify = Image.open(uploaded_file).convert("RGB")
        input_source = "upload"

    # ── Preview + Classify ──
    if image_to_classify:
        st.markdown("---")
        col_img, col_btn = st.columns([3, 1], vertical_alignment="bottom")

        with col_img:
            st.markdown('<div class="img-preview-wrap">', unsafe_allow_html=True)
            st.image(image_to_classify, caption="📷 Pré-visualização da Imagem", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_btn:
            classify_btn = st.button("🔍 Classificar", use_container_width=True)

        # ── Run mock CNN on button click ──
        if classify_btn:
            st.markdown("---")

            # Animated loading indicator
            loading_placeholder = st.empty()
            loading_placeholder.markdown("""
            <div class="analyzing-box">
                <div class="spin-ring"></div>
                <div class="analyzing-text">Analisando imagem…</div>
                <div style="color:#334155; font-size:0.78rem;">Executando inferência da CNN</div>
            </div>
            """, unsafe_allow_html=True)

            # Simulate inference (mock model)
            label, confidence, all_scores = mock_cnn_predict(image_to_classify)

            # Clear loader and display result
            loading_placeholder.empty()
            render_result(label, confidence, all_scores)

    # ── Footer ──
    st.markdown(
        '<div class="footer">ReciclaBot · Demonstração Simulada · Construído com Streamlit</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
