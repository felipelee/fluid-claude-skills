document.addEventListener('DOMContentLoaded', function () {
  var section = document.querySelector('[data-bundle-section]');
  if (!section) return;
  initBundleBuilder(section);
});

function initBundleBuilder(section) {
  var state = { groups: [], slots: [], totalMax: 0 };

  section.querySelectorAll('[data-group-type="customizable"]').forEach(function (groupEl) {
    var g = {
      el: groupEl,
      id: groupEl.getAttribute('data-bundle-group-id'),
      min: parseInt(groupEl.getAttribute('data-min-selections') || '0', 10),
      max: parseInt(groupEl.getAttribute('data-max-selections') || '999', 10),
      type: groupEl.getAttribute('data-selection-type') || 'min',
      items: {}
    };
    state.totalMax += g.max;

    groupEl.querySelectorAll('.bbs-card[data-item-id]').forEach(function (card) {
      var id = card.getAttribute('data-item-id');
      var dq = parseInt(card.getAttribute('data-default-quantity') || '0', 10);
      g.items[id] = dq;
      if (dq > 0) { card.classList.add('is-selected'); setCardQty(card, dq); }

      bind(card, '.bbs-card-add', function (e) { e.stopPropagation(); adj(state, g, card, 1); });
      bind(card, '.bbs-qty-plus', function (e) { e.stopPropagation(); adj(state, g, card, 1); });
      bind(card, '.bbs-qty-minus', function (e) { e.stopPropagation(); adj(state, g, card, -1); });
      card.addEventListener('click', function () { if (!g.items[id]) adj(state, g, card, 1); });
    });

    state.groups.push(g);
  });

  state.slots = Array.from(section.querySelectorAll('[data-slot-container] .bbs-slot'));
  refresh(section, state);
  initSubscription(section);
  initAccordions(section);
  initSelects(section);
}

function bind(parent, sel, fn) {
  var el = parent.querySelector(sel);
  if (el) el.addEventListener('click', fn);
}

function adj(state, g, card, delta) {
  var id = card.getAttribute('data-item-id');
  var mq = card.getAttribute('data-max-quantity');
  var cur = g.items[id] || 0;
  var next = cur + delta;

  if (next < 0) return;
  if (mq && mq !== '' && next > parseInt(mq, 10)) return;
  if (delta > 0 && gTotal(g) >= g.max) return;

  g.items[id] = next;
  card.classList.toggle('is-selected', next > 0);
  setCardQty(card, next);

  if (delta > 0 && next === 1) pulseCard(card);
  refresh(card.closest('[data-bundle-section]'), state);
}

function pulseCard(card) {
  card.style.transform = 'scale(0.96)';
  setTimeout(function () { card.style.transform = ''; }, 150);
}

function setCardQty(card, qty) {
  var id = card.getAttribute('data-item-id');
  var badge = card.querySelector('[data-qty-badge]');
  if (badge) badge.textContent = qty > 0 ? qty + '\u00d7' : '0';
  var val = card.querySelector('.bbs-stepper-val[data-item-id="' + id + '"]');
  if (val) val.textContent = String(qty);
}

function gTotal(g) {
  var t = 0;
  for (var k in g.items) t += g.items[k] || 0;
  return t;
}

function refresh(section, state) {
  state.groups.forEach(function (g) { updateBadge(g); updateBtns(g); });
  updateSlots(section, state);
  updateProgress(section, state);
  updateSummary(section, state);
  updateCTA(section, state);
}

function updateBadge(g) {
  var t = gTotal(g);
  var badge = g.el.querySelector('.bbs-badge[data-group-id="' + g.id + '"]');
  if (!badge) return;
  var cnt = badge.querySelector('.bbs-sel-count');
  if (cnt) cnt.textContent = String(t);
  badge.classList.remove('is-complete', 'is-error');
  if (t === g.max) badge.classList.add('is-complete');
  else if (t > g.max) badge.classList.add('is-error');
}

function updateBtns(g) {
  var t = gTotal(g);
  g.el.querySelectorAll('.bbs-card[data-item-id]').forEach(function (card) {
    var id = card.getAttribute('data-item-id');
    var mq = card.getAttribute('data-max-quantity');
    var qty = g.items[id] || 0;
    var full = t >= g.max;
    var itemFull = mq && mq !== '' && qty >= parseInt(mq, 10);

    var addBtn = card.querySelector('.bbs-card-add');
    var plus = card.querySelector('.bbs-qty-plus');
    var minus = card.querySelector('.bbs-qty-minus');
    if (addBtn) addBtn.disabled = full || itemFull;
    if (plus) plus.disabled = full || itemFull;
    if (minus) minus.disabled = qty <= 0;
  });
}

function updateSlots(section, state) {
  if (!state.slots.length) return;
  var imgs = [];
  state.groups.forEach(function (g) {
    g.el.querySelectorAll('.bbs-card[data-item-id]').forEach(function (card) {
      var id = card.getAttribute('data-item-id');
      var qty = g.items[id] || 0;
      var src = card.getAttribute('data-item-image') || '';
      for (var i = 0; i < qty; i++) imgs.push(src);
    });
  });

  state.slots.forEach(function (slot, i) {
    var wasFilled = slot.classList.contains('is-filled');
    var shouldFill = i < imgs.length && imgs[i];

    if (shouldFill) {
      if (!wasFilled || !slot.querySelector('img') || slot.querySelector('img').src !== imgs[i]) {
        slot.innerHTML = '';
        slot.classList.add('is-filled');
        var img = document.createElement('img');
        img.src = imgs[i]; img.alt = ''; img.loading = 'lazy';
        slot.appendChild(img);
      }
    } else {
      slot.classList.remove('is-filled');
      slot.innerHTML = '';
    }
  });
}

function updateProgress(section, state) {
  var sel = 0, mx = 0;
  state.groups.forEach(function (g) { sel += gTotal(g); mx += g.max; });
  var pct = mx > 0 ? Math.min((sel / mx) * 100, 100) : 0;

  var fill = section.querySelector('[data-progress-fill]');
  if (fill) {
    fill.style.width = pct + '%';
    fill.classList.toggle('has-progress', pct > 0);
  }

  var label = section.querySelector('[data-progress-text]');
  if (label) {
    var rem = Math.max(mx - sel, 0);
    if (rem > 0) {
      label.textContent = 'PICK ' + rem + ' MORE';
      label.classList.remove('is-complete');
    } else {
      label.textContent = 'READY TO GO';
      label.classList.add('is-complete');
    }
  }
}

function updateSummary(section, state) {
  var container = section.querySelector('[data-summary-details]');
  if (!container) return;

  var html = '';
  state.groups.forEach(function (g) {
    g.el.querySelectorAll('.bbs-card[data-item-id]').forEach(function (card) {
      var id = card.getAttribute('data-item-id');
      var qty = g.items[id] || 0;
      if (qty <= 0) return;
      var img = card.getAttribute('data-item-image') || '';
      var name = card.getAttribute('data-item-name') || '';
      html += '<div class="bbs-panel-item">';
      if (img) html += '<img src="' + img + '" alt="" />';
      html += '<span class="bbs-panel-item-name">' + name + '</span>';
      html += '<span class="bbs-panel-item-qty">' + qty + '\u00d7</span>';
      html += '</div>';
    });
  });

  container.innerHTML = html;
}

function updateCTA(section, state) {
  var ok = true, sel = 0, mx = 0;
  state.groups.forEach(function (g) {
    var t = gTotal(g);
    sel += t; mx += g.max;
    if (g.type === 'exact') { if (t !== g.max) ok = false; }
    else if (g.type === 'range') { if (t < g.min || t > g.max) ok = false; }
    else { if (t < g.min) ok = false; }
  });

  var btn = section.querySelector('.bundle-add-to-cart-btn');
  var cta = section.querySelector('[data-cta-text]');
  var err = section.querySelector('.bundle-validation-error');

  if (btn) btn.disabled = !ok;

  if (cta) {
    if (!ok && mx > 0) {
      cta.textContent = 'PICK ' + (mx - sel) + ' MORE';
    } else {
      cta.textContent = 'Add to Cart';
    }
  }

  if (err) {
    err.style.display = (!ok && state.groups.length > 0) ? '' : 'none';
    err.classList.toggle('hidden', ok || !state.groups.length);
  }
}

function initSubscription(section) {
  var radios = section.querySelectorAll('input[name="fluid-checkout-subscribe"]');
  if (!radios.length) return;
  radios.forEach(function (r) {
    r.addEventListener('change', function () { subUI(section); });
  });
  var dd = section.querySelector('.subscription-plans-dropdown');
  if (dd) dd.addEventListener('change', function () { subPrice(section); subUI(section); });
  subUI(section);
  subPrice(section);
}

function subUI(section) {
  var chk = section.querySelector('input[name="fluid-checkout-subscribe"]:checked');
  var isSub = chk && chk.value === 'subscription';
  var btn = section.querySelector('.bundle-add-to-cart-btn');
  var plans = section.querySelector('.subscription-plans');
  if (isSub) {
    if (plans) plans.style.display = '';
    if (btn) { var dd = section.querySelector('.subscription-plans-dropdown'); btn.dataset.fluidSubscriptionPlanId = dd ? dd.value : ''; }
  } else {
    if (plans) plans.style.display = 'none';
    if (btn) btn.dataset.fluidSubscriptionPlanId = '';
  }
}

function subPrice(section) {
  var dd = section.querySelector('.subscription-plans-dropdown');
  if (!dd) return;
  var opt = dd.options[dd.selectedIndex];
  if (!opt) return;
  var price = opt.getAttribute('data-subscription-price');
  section.querySelectorAll('.subscription-price').forEach(function (el) { if (price) el.textContent = price; });
  var type = opt.getAttribute('data-price-adjustment-type');
  var amt = opt.getAttribute('data-price-adjustment-amount');
  var disc = section.querySelector('.subscribe-discount-value');
  var row = section.querySelector('.subscribe-offer-text');
  if (disc && amt) disc.textContent = type === 'fixed_amount' ? amt : amt + '%';
  if (row) row.style.display = (amt && parseFloat(amt) > 0) ? '' : 'none';
}

function initAccordions(section) {
  section.querySelectorAll('.bbs-acc-head').forEach(function (h) {
    h.addEventListener('click', function () {
      this.classList.toggle('is-open');
      var body = this.nextElementSibling;
      if (body && body.classList.contains('bbs-acc-body'))
        body.style.display = this.classList.contains('is-open') ? 'block' : 'none';
    });
  });
}

function initSelects(section) {
  section.querySelectorAll('select.custom-select').forEach(function (el) {
    if (typeof TomSelect !== 'undefined')
      new TomSelect(el, { allowEmptyOption: false, controlInput: null });
  });
}
