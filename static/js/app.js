// ── Global JS ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

  // Auto-dismiss flash messages
  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'opacity 0.5s, transform 0.5s';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      setTimeout(function () { alert.remove(); }, 500);
    }, 4000);

    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        alert.style.opacity = '0';
        setTimeout(function () { alert.remove(); }, 300);
      });
    }
  });

  // Mobile nav toggle
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.navbar-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
    });
    document.addEventListener('click', function (e) {
      if (!toggle.contains(e.target) && !nav.contains(e.target)) {
        nav.classList.remove('open');
      }
    });
  }

  // Option selection highlight
  document.querySelectorAll('.option-label').forEach(function (label) {
    label.addEventListener('click', function () {
      const name = this.querySelector('input[type="radio"]').name;
      document.querySelectorAll(`input[name="${name}"]`).forEach(function (r) {
        r.closest('.option-label').classList.remove('selected');
      });
      this.classList.add('selected');
    });
  });

  // Keyboard shortcut for options (1-4)
  document.addEventListener('keydown', function (e) {
    const key = e.key;
    if (['1', '2', '3', '4'].includes(key)) {
      const options = document.querySelectorAll('.option-label');
      const idx = parseInt(key) - 1;
      if (options[idx]) options[idx].click();
    }
  });

  // Score ring animation
  const fill = document.querySelector('.score-ring .fill');
  if (fill) {
    const pct = parseFloat(fill.dataset.score || 0);
    const r = parseFloat(fill.getAttribute('r'));
    const circ = 2 * Math.PI * r;
    fill.style.strokeDasharray = circ;
    fill.style.strokeDashoffset = circ;
    setTimeout(function () {
      fill.style.strokeDashoffset = circ - (circ * pct / 100);
    }, 200);
  }

  // Confirm delete
  document.querySelectorAll('.confirm-delete').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      if (!confirm('Are you sure you want to delete this? This action cannot be undone.')) {
        e.preventDefault();
      }
    });
  });

  // Progress tracking for quiz
  const form = document.getElementById('quiz-form');
  if (form) {
    const totalQ = parseInt(form.dataset.total || 0);
    function updateProgress() {
      const answered = new Set();
      form.querySelectorAll('input[type="radio"]:checked').forEach(function (r) {
        answered.add(r.name);
      });
      const pct = totalQ > 0 ? (answered.size / totalQ * 100) : 0;
      const bar = document.querySelector('.quiz-progress-fill');
      if (bar) bar.style.width = pct + '%';
      const counter = document.getElementById('answered-count');
      if (counter) counter.textContent = answered.size;
    }
    form.addEventListener('change', updateProgress);
    updateProgress();
  }

});

// ── Quiz Timer ──────────────────────────────────────────
function startQuizTimer(seconds, inputId) {
  const display = document.getElementById('timer-display');
  const widget  = document.querySelector('.timer-widget');
  const input   = document.getElementById(inputId);
  let elapsed   = 0;
  let remaining = seconds;

  function tick() {
    if (remaining <= 0) {
      display.textContent = '00:00';
      document.getElementById('quiz-form').submit();
      return;
    }
    const m = Math.floor(remaining / 60);
    const s = remaining % 60;
    display.textContent = String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
    if (input) input.value = elapsed;
    if (remaining <= 30 && widget) widget.classList.add('urgent');
    remaining--;
    elapsed++;
    setTimeout(tick, 1000);
  }
  tick();
}
