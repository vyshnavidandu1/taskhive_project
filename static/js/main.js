/* ============================================
   TaskHive – Main JavaScript
   ============================================ */

'use strict';

// ─── Sidebar Toggle ────────────────────────
(function() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  const openBtn = document.getElementById('sidebarOpen');
  const closeBtn = document.getElementById('sidebarClose');

  if (!sidebar) return;

  function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (openBtn) openBtn.addEventListener('click', openSidebar);
  if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
  if (overlay) overlay.addEventListener('click', closeSidebar);

  // Close on resize to desktop
  window.addEventListener('resize', function() {
    if (window.innerWidth >= 992) closeSidebar();
  });
})();

// ─── Auto-dismiss Alerts ───────────────────
(function() {
  document.querySelectorAll('.alert-toast').forEach(function(alert) {
    setTimeout(function() {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 4500);
  });
})();

// ─── Confirm Dialogs ───────────────────────
document.addEventListener('click', function(e) {
  const btn = e.target.closest('[data-confirm]');
  if (btn) {
    const msg = btn.dataset.confirm || 'Are you sure?';
    if (!confirm(msg)) e.preventDefault();
  }
});

// ─── Active Nav Highlighting ───────────────
(function() {
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(function(link) {
    const href = link.getAttribute('href');
    if (href && href !== '/' && currentPath.startsWith(href)) {
      link.classList.add('active');
    }
  });
})();

// ─── Date Input: Set Minimum to Today ──────
(function() {
  document.querySelectorAll('input[type="date"]').forEach(function(input) {
    if (!input.min && !input.dataset.notoday) {
      const today = new Date().toISOString().split('T')[0];
      input.min = today;
    }
  });
})();

// ─── CSRF Token Helper ─────────────────────
function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : '';
}

// ─── Tooltip Init ──────────────────────────
(function() {
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach(function(el) {
    new bootstrap.Tooltip(el, { trigger: 'hover' });
  });
})();

// ─── Progress Bar Animation ────────────────
(function() {
  document.querySelectorAll('.progress-bar[style*="width"]').forEach(function(bar) {
    const targetWidth = bar.style.width;
    bar.style.width = '0%';
    requestAnimationFrame(function() {
      setTimeout(function() {
        bar.style.transition = 'width 0.8s cubic-bezier(.4,0,.2,1)';
        bar.style.width = targetWidth;
      }, 100);
    });
  });
})();

// ─── Form Validation Styles ────────────────
(function() {
  document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function() {
      form.querySelectorAll('.form-control, .form-select').forEach(function(input) {
        if (input.value.trim() !== '' || !input.required) {
          input.classList.add('is-valid');
        }
      });
    });
  });
})();

// ─── Character Counter for Textareas ───────
document.querySelectorAll('textarea[maxlength]').forEach(function(ta) {
  const max = ta.getAttribute('maxlength');
  const counter = document.createElement('small');
  counter.className = 'text-muted float-end';
  counter.textContent = `0 / ${max}`;
  ta.parentNode.appendChild(counter);
  ta.addEventListener('input', function() {
    counter.textContent = `${ta.value.length} / ${max}`;
  });
});

// ─── Search Input Debounce ─────────────────
(function() {
  const searchInputs = document.querySelectorAll('input[name="q"]');
  searchInputs.forEach(function(input) {
    let timeout;
    input.addEventListener('input', function() {
      clearTimeout(timeout);
      timeout = setTimeout(function() {
        // Only auto-submit if user stopped typing
      }, 600);
    });
  });
})();
