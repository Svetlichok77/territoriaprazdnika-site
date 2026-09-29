// Территория праздника — меню и подбор квеста
(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  var form = document.getElementById('picker-form');
  if (!form) return;
  var cards = Array.prototype.slice.call(document.querySelectorAll('[data-quest]'));
  var count = document.getElementById('picker-count');
  var empty = document.getElementById('picker-empty');
  var keys = ['age', 'occ', 'place', 'group'];

  function plural(n) {
    var m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return 'квест';
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return 'квеста';
    return 'квестов';
  }

  function apply() {
    var shown = 0;
    cards.forEach(function (card) {
      var ok = keys.every(function (k) {
        var v = form.elements[k].value;
        if (v === 'any') return true;
        return (' ' + card.getAttribute('data-' + k) + ' ').indexOf(' ' + v + ' ') !== -1;
      });
      card.hidden = !ok;
      if (ok) shown++;
    });
    count.textContent = shown ? 'Нашли ' + shown + ' ' + plural(shown) : 'Ничего не нашли';
    empty.hidden = shown !== 0;
  }

  // фильтры из адреса: ?povod=ny&vozrast=k57
  var map = { vozrast: 'age', povod: 'occ', gde: 'place', igroki: 'group' };
  var params = new URLSearchParams(location.search);
  Object.keys(map).forEach(function (p) {
    var v = params.get(p), el = form.elements[map[p]];
    if (v && el && el.querySelector('option[value="' + v + '"]')) el.value = v;
  });

  form.addEventListener('change', apply);
  document.querySelectorAll('[data-reset]').forEach(function (b) {
    b.addEventListener('click', function () {
      keys.forEach(function (k) { form.elements[k].value = 'any'; });
      apply();
    });
  });
  apply();
})();
