/* ═══════════════════════════════════════════════════════════════
   DiabetesAI — Application Logic
   ═══════════════════════════════════════════════════════════════ */

const API_BASE = 'http://localhost:5000';

// ── Field metadata ──────────────────────────────────────────────
const FIELDS = [
  { id: 'pregnancies',    label: 'Pregnancies',    min: 0,   max: 20,   unit: 'count'  },
  { id: 'glucose',        label: 'Glucose',        min: 0,   max: 300,  unit: 'mg/dL'  },
  { id: 'blood_pressure', label: 'Blood Pressure', min: 0,   max: 200,  unit: 'mmHg'   },
  { id: 'skin_thickness', label: 'Skin Thickness', min: 0,   max: 100,  unit: 'mm'     },
  { id: 'insulin',        label: 'Insulin',        min: 0,   max: 900,  unit: 'μU/mL'  },
  { id: 'bmi',            label: 'BMI',            min: 0,   max: 70,   unit: 'kg/m²'  },
  { id: 'dpf',            label: 'Diabetes Pedigree', min: 0, max: 3,   unit: 'score'  },
  { id: 'age',            label: 'Age',            min: 1,   max: 120,  unit: 'yrs'    },
];

const RISK_CONFIG = {
  'Low':       { icon: '✅', cls: 'low',       color: '#10B981' },
  'Moderate':  { icon: '⚠️', cls: 'moderate',  color: '#F59E0B' },
  'High':      { icon: '🔴', cls: 'high',      color: '#EF4444' },
  'Very High': { icon: '🚨', cls: 'very-high', color: '#DC2626' },
};

// ── Particle System ─────────────────────────────────────────────
class ParticleSystem {
  constructor() {
    this.canvas = document.getElementById('particles-canvas');
    this.ctx    = this.canvas.getContext('2d');
    this.particles = [];
    this.resize();
    this.init();
    window.addEventListener('resize', () => this.resize());
    this.animate();
  }

  resize() {
    this.canvas.width  = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }

  init() {
    const count = Math.floor(window.innerWidth / 12);
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        r: Math.random() * 1.5 + 0.3,
        dx: (Math.random() - 0.5) * 0.3,
        dy: (Math.random() - 0.5) * 0.3,
        o: Math.random() * 0.5 + 0.1,
      });
    }
  }

  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    for (const p of this.particles) {
      p.x += p.dx;
      p.y += p.dy;
      if (p.x < 0) p.x = this.canvas.width;
      if (p.x > this.canvas.width) p.x = 0;
      if (p.y < 0) p.y = this.canvas.height;
      if (p.y > this.canvas.height) p.y = 0;

      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      this.ctx.fillStyle = `rgba(100, 160, 255, ${p.o})`;
      this.ctx.fill();
    }
    requestAnimationFrame(() => this.animate());
  }
}

// ── Navbar scroll effect ────────────────────────────────────────
function initNavbar() {
  const nav = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 20);
  }, { passive: true });
}

// ── Range bar updates ───────────────────────────────────────────
function updateRangeBar(field) {
  const input = document.getElementById(field.id);
  const bar   = document.getElementById(`range-${field.id}`);
  const check = document.getElementById(`check-${field.id}`);

  function update() {
    const val = parseFloat(input.value);
    const pct = Math.max(0, Math.min(100, ((val - field.min) / (field.max - field.min)) * 100));
    bar.style.width = pct + '%';

    // Validity
    const valid = val >= field.min && val <= field.max && !isNaN(val);
    input.classList.toggle('valid', valid);
    input.classList.toggle('invalid', !valid && input.value !== '');

    // Checklist
    if (check) {
      check.classList.toggle('active', valid);
    }
  }

  input.addEventListener('input', update);
  update();
}

// ── Form initialization ─────────────────────────────────────────
function initForm() {
  FIELDS.forEach(f => updateRangeBar(f));

  document.getElementById('reset-btn').addEventListener('click', () => {
    const defaults = { pregnancies:1, glucose:110, blood_pressure:72, skin_thickness:20,
                       insulin:79, bmi:25.0, dpf:0.50, age:33 };
    FIELDS.forEach(f => {
      const inp = document.getElementById(f.id);
      inp.value = defaults[f.id];
      inp.dispatchEvent(new Event('input'));
    });
    showPanel('idle');
  });
}

// ── Panel management ────────────────────────────────────────────
function showPanel(which) {
  document.getElementById('result-idle').hidden  = which !== 'idle';
  document.getElementById('result-card').hidden  = which !== 'result';
  document.getElementById('error-card').hidden   = which !== 'error';
}

// ── Gauge animation ─────────────────────────────────────────────
function animateGauge(probability) {
  const fill    = document.getElementById('gauge-fill');
  const needle  = document.getElementById('gauge-needle');
  const valueEl = document.getElementById('gauge-value');

  // Arc total length = π × r = π × 78 ≈ 244.9
  const arcLen     = 244.9;
  const dashOffset = arcLen - (probability * arcLen);

  // Needle sweeps from -90° (left = 0%) to +90° (right = 100%)
  const angle = -90 + (probability * 180);

  const highRisk = probability >= 0.5;

  // Switch gradient colour
  fill.setAttribute('stroke', highRisk ? 'url(#gaugeGradHigh)' : 'url(#gaugeGradLow)');

  // Small delay lets the browser register the element is visible before transitioning
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      fill.style.strokeDashoffset = dashOffset;
      // *** CSS style.transform — NOT setAttribute — so the CSS transition fires ***
      needle.style.transform = `rotate(${angle}deg)`;
    });
  });

  // Count-up number animation
  let current = 0;
  const target   = Math.round(probability * 100);
  const stepSize = target === 0 ? 0 : target / 55;
  valueEl.style.color = highRisk ? '#EF4444' : '#10B981';

  if (target === 0) {
    valueEl.textContent = '0%';
    return;
  }

  const interval = setInterval(() => {
    current = Math.min(current + stepSize, target);
    valueEl.textContent = Math.round(current) + '%';
    if (current >= target) clearInterval(interval);
  }, 18);
}

// ── Confidence bars ─────────────────────────────────────────────
function animateConfBars(probability) {
  const lowPct  = Math.round((1 - probability) * 100);
  const highPct = Math.round(probability * 100);

  document.getElementById('conf-low').textContent  = lowPct + '%';
  document.getElementById('conf-high').textContent = highPct + '%';

  setTimeout(() => {
    document.getElementById('conf-bar-low').style.width  = lowPct + '%';
    document.getElementById('conf-bar-high').style.width = highPct + '%';
  }, 300);
}

// ── Render result ───────────────────────────────────────────────
function renderResult(data, inputValues) {
  const isPositive  = data.prediction === 1;
  const probability = data.probability;
  const riskLevel   = data.risk_level;
  const risk        = RISK_CONFIG[riskLevel] || RISK_CONFIG['Moderate'];

  // Header
  const iconEl  = document.getElementById('result-icon');
  const titleEl = document.getElementById('result-title');

  iconEl.textContent  = isPositive ? '⚠️' : '✅';
  iconEl.className    = `result-icon ${isPositive ? 'positive' : 'negative'}`;
  titleEl.textContent = isPositive ? 'High Risk of Diabetes' : 'Low Risk of Diabetes';
  titleEl.className   = `result-title ${isPositive ? 'positive' : 'negative'}`;

  // Gauge
  animateGauge(probability);

  // Risk badge
  const badge = document.getElementById('risk-badge');
  badge.className = `risk-badge ${risk.cls}`;
  document.getElementById('risk-icon').textContent  = risk.icon;
  document.getElementById('risk-level').textContent = riskLevel;
  document.getElementById('risk-level').style.color = risk.color;

  // Confidence bars
  animateConfBars(probability);

  // Feature summary
  const fsGrid = document.getElementById('fs-grid');
  fsGrid.innerHTML = '';
  FIELDS.forEach((f, i) => {
    const div = document.createElement('div');
    div.className = 'fs-item';
    div.innerHTML = `<span>${f.label}</span><span>${inputValues[i]} ${f.unit}</span>`;
    fsGrid.appendChild(div);
  });

  showPanel('result');
}

// ── Form submission ─────────────────────────────────────────────
async function handleSubmit(e) {
  e.preventDefault();

  // Read values
  const inputValues = FIELDS.map(f => parseFloat(document.getElementById(f.id).value));

  // Check validity
  const invalid = FIELDS.some((f, i) => isNaN(inputValues[i]) || inputValues[i] < f.min || inputValues[i] > f.max);
  if (invalid) {
    FIELDS.forEach((f, i) => {
      const inp = document.getElementById(f.id);
      const val = inputValues[i];
      if (isNaN(val) || val < f.min || val > f.max) {
        inp.classList.add('invalid');
        inp.classList.remove('valid');
        inp.style.animation = 'shake 0.4s ease';
        setTimeout(() => inp.style.animation = '', 400);
      }
    });
    return;
  }

  // Loading state
  const btn     = document.getElementById('predict-btn');
  const btnText = btn.querySelector('.btn-text');
  const btnLoad = btn.querySelector('.btn-loader');
  btnText.hidden = true;
  btnLoad.hidden = false;
  btn.disabled   = true;

  const payload = {};
  FIELDS.forEach((f, i) => { payload[f.id] = inputValues[i]; });

  try {
    const res  = await fetch(`${API_BASE}/api/predict`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || `HTTP ${res.status}`);
    }

    const data = await res.json();
    renderResult(data, inputValues);

    // Scroll to result on mobile
    if (window.innerWidth < 1024) {
      document.getElementById('result-panel').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

  } catch (err) {
    document.getElementById('error-msg').textContent =
      err.message || 'Unable to reach the API. Is the Flask server running on port 5000?';
    showPanel('error');
  } finally {
    btnText.hidden = false;
    btnLoad.hidden = true;
    btn.disabled   = false;
  }
}

// ── Back button ─────────────────────────────────────────────────
function initBackBtn() {
  document.getElementById('back-btn').addEventListener('click', () => {
    showPanel('idle');
    document.getElementById('prediction-form').scrollIntoView({ behavior: 'smooth' });
  });

  document.getElementById('retry-btn').addEventListener('click', () => {
    document.getElementById('prediction-form').requestSubmit();
  });
}

// ── Intersection Observer for scroll animations ──────────────────
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.about-card, .section-header, .form-panel').forEach(el => {
    el.classList.add('fade-up');
    observer.observe(el);
  });
}

// ── Shake keyframe (injected) ────────────────────────────────────
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
  @keyframes shake {
    0%,100% { transform: translateX(0); }
    25% { transform: translateX(-6px); }
    75% { transform: translateX(6px); }
  }
`;
document.head.appendChild(shakeStyle);

// ── Init ────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  new ParticleSystem();
  initNavbar();
  initForm();
  initBackBtn();
  initScrollAnimations();
  showPanel('idle');

  document.getElementById('prediction-form').addEventListener('submit', handleSubmit);

  // Live checklist sync on any input change
  FIELDS.forEach(f => {
    document.getElementById(f.id).addEventListener('input', () => {
      const val = parseFloat(document.getElementById(f.id).value);
      const valid = !isNaN(val) && val >= f.min && val <= f.max;
      const check = document.getElementById(`check-${f.id}`);
      if (check) check.classList.toggle('active', valid);
    });
  });

  // Trigger initial state
  FIELDS.forEach(f => {
    document.getElementById(f.id).dispatchEvent(new Event('input'));
  });
});
