/* Gold Coast Auto Group — quote form
   Submits to Web3Forms and shows the thank-you state.
*/
(function () {
  // Create a free access key at https://web3forms.com for the address that
  // should receive quote requests, and paste it here.
  var FORM_ENDPOINT = 'https://api.web3forms.com/submit';
  var FORM_ACCESS_KEY = '32fcca62-ab44-4ee3-b7f5-538fae74df97'; // empty = preview mode (shows thank-you, sends nothing)

  var quote = document.querySelector('.quote');
  var form = document.getElementById('quote-form');
  if (!quote || !form) return;

  var btn = form.querySelector('button[type="submit"]');
  var err = form.querySelector('.form-error');

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (form.querySelector('[name="botcheck"]').checked) return; // honeypot
    if (!form.checkValidity()) { form.reportValidity(); return; }
    err.style.display = 'none';
    btn.disabled = true;
    var done = function () { quote.classList.add('sent'); quote.scrollIntoView({ behavior: 'smooth', block: 'start' }); };
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
