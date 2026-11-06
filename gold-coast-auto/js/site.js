/* Gold Coast Auto Group — site behaviour
   1. Mobile menu toggle
   2. Quote form: intent prefill, submit to the form service, thank-you state
*/
(function () {
  // ---- Config: set these once, no other code changes needed ----
  // Form delivery. Create a free access key at https://web3forms.com (it emails
  // submissions to the address you register) and paste it here.
  var FORM_ENDPOINT = 'https://api.web3forms.com/submit';
  var FORM_ACCESS_KEY = '';           // empty = preview mode (shows thank-you, sends nothing)

  // ---- Mobile menu ----
  var header = document.querySelector('.site-header');
  var menuBtn = document.querySelector('.menu-btn');
  if (header && menuBtn) {
    menuBtn.addEventListener('click', function () {
      var open = header.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('open')) {
        header.classList.remove('open');
        menuBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // ---- Quote form ----
  var quote = document.querySelector('.quote');
  var form = document.getElementById('quote-form');
  if (!quote || !form) return;

  var copy = {
    sourcing:  { title: 'Start your search',  sub: 'Tell us the exact build. We search all 50 states until we find it.', payment: 'Not sure yet', notes: '' },
    financing: { title: 'Discuss your terms', sub: 'Tell us the car and how you want to structure it. We negotiate the terms for you.', payment: 'Finance', notes: 'Interested in discussing lease and financing options.' },
    delivery:  { title: 'Arrange delivery',   sub: 'Wherever home is, we bring the car to your door.', payment: 'Not sure yet', notes: 'Please include delivery details in the quote.' },
    exotic:    { title: 'Private inquiry',    sub: 'Exotic, off-market and collection inquiries are handled personally and discreetly by Jared.', payment: 'Cash', notes: 'Exotic / off-market inquiry.' }
  };
  var intent = new URLSearchParams(location.search).get('intent');
  var c = copy[intent];
  if (c) {
    var t = document.getElementById('form-title'); if (t) t.textContent = c.title;
    var s = document.getElementById('form-sub');   if (s) s.textContent = c.sub;
    var pay = form.querySelector('[name="payment"]'); if (pay) pay.value = c.payment;
    var notes = form.querySelector('[name="notes"]'); if (notes && !notes.value) notes.value = c.notes;
    var subj = form.querySelector('[name="subject"]'); if (subj) subj.value = 'Quote request (' + intent + ') from the website';
  }

  var btn = form.querySelector('button[type="submit"]');
  var err = form.querySelector('.form-error');

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (form.querySelector('[name="botcheck"]').checked) return; // honeypot
    err.style.display = 'none';
    btn.disabled = true;
    var done = function () { quote.classList.add('sent'); window.scrollTo({ top: quote.offsetTop - 60, behavior: 'smooth' }); };
    var fail = function () { btn.disabled = false; err.style.display = 'block'; };

    if (!FORM_ACCESS_KEY) {
      console.warn('Quote form is in preview mode: no FORM_ACCESS_KEY set, nothing was sent.');
      setTimeout(done, 400);
      return;
    }
    var data = new FormData(form);
    data.append('access_key', FORM_ACCESS_KEY);
    data.append('from_name', 'Gold Coast Auto Group website');
    fetch(FORM_ENDPOINT, { method: 'POST', body: data, headers: { 'Accept': 'application/json' } })
      .then(function (r) { return r.json(); })
      .then(function (j) { if (j && j.success) done(); else fail(); })
      .catch(fail);
  });
})();
