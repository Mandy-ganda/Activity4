const $ = (id) => document.getElementById(id);
const fmt = (n) => Number(n).toLocaleString(undefined, { maximumFractionDigits: 4 });

async function post(url, body) {
  const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  return res.json();
}
function show(el, data) {
  if (data.ok) {
    el.className = 'result';
    el.innerHTML = `<span class="big">${fmt(data.area)} square units</span><span></span>`;
    el.lastChild.textContent = data.steps;
  } else {
    el.className = 'result err';
    el.textContent = data.error;
  }
}
const debounce = (fn, ms = 250) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

/* Circle */
const radius = $('radius');
radius.addEventListener('input', debounce(async () => {
  if (radius.value === '') { $('circle-result').className = 'result'; $('circle-result').textContent = 'Enter a radius to see the area.'; return; }
  const data = await post('/api/area/circle', { radius: radius.value });
  show($('circle-result'), data);
  if (data.ok) {
    const r = Math.max(4, Math.min(90, 60 * Math.sqrt(Math.max(parseFloat(radius.value), 0)) / Math.sqrt(5)));
    $('circle-shape').setAttribute('r', r);
    $('circle-radius').setAttribute('x2', 100 + r);
  }
}));

/* Triangle */
let mode = 'bh';
document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => {
  mode = tab.dataset.mode;
  document.querySelectorAll('.tab').forEach(t => { const on = t === tab; t.classList.toggle('active', on); t.setAttribute('aria-selected', on); });
  $('mode-bh').hidden = mode !== 'bh';
  $('mode-sides').hidden = mode !== 'sides';
  $('tri-formula').textContent = mode === 'bh' ? 'A = ½ × b × h' : "Heron's formula: A = √(s(s−a)(s−b)(s−c))";
  $('tri-result').className = 'result';
  $('tri-result').textContent = 'Enter your measurements to see the area.';
  calcTriangle();
}));

const calcTriangle = debounce(async () => {
  const body = mode === 'bh'
    ? { base: $('base').value, height: $('height').value }
    : { mode: 'sides', a: $('sa').value, b: $('sb').value, c: $('sc').value };
  if (Object.values(body).filter(v => v !== 'sides').some(v => v === '')) return;
  const data = await post('/api/area/triangle', body);
  show($('tri-result'), data);
  if (data.ok && mode === 'bh') {
    const b = parseFloat($('base').value), h = parseFloat($('height').value);
    const k = 130 / Math.max(b, h, 0.0001);
    const w = Math.max(20, b * k), ht = Math.max(20, h * k);
    const x1 = 100 - w / 2, x2 = 100 + w / 2, y = 165;
    $('tri-shape').setAttribute('points', `${x1},${y} ${x2},${y} ${100},${y - ht}`);
  }
});
['base', 'height', 'sa', 'sb', 'sc'].forEach(id => $(id).addEventListener('input', calcTriangle));

/* Uppercase converter */
const upIn = $('upper-in'), upOut = $('upper-out'), upCount = $('upper-count');
upIn.addEventListener('input', debounce(async () => {
  const text = upIn.value;
  if (!text) { upOut.value = ''; upCount.textContent = '0 characters'; return; }
  const data = await post('/api/uppercase', { text });
  if (data.ok) { upOut.value = data.result; upCount.textContent = data.length + ' characters'; }
  else { upOut.value = ''; upCount.textContent = data.error; }
}, 120));
$('upper-copy').addEventListener('click', async (e) => {
  if (!upOut.value) { upCount.textContent = 'Nothing to copy yet.'; return; }
  try { await navigator.clipboard.writeText(upOut.value); }
  catch (err) { upOut.select(); document.execCommand('copy'); }
  const btn = e.currentTarget; btn.textContent = 'Copied!';
  setTimeout(() => { btn.textContent = 'Copy result'; }, 1400);
});
$('upper-clear').addEventListener('click', () => { upIn.value = ''; upOut.value = ''; upCount.textContent = '0 characters'; upIn.focus(); });

/* Infix to postfix */
const inIn = $('infix-in'), inRes = $('postfix-result'), inSteps = $('postfix-steps');
const inBody = inSteps.querySelector('tbody');
const inRun = debounce(async () => {
  const expression = inIn.value.trim();
  if (!expression) {
    inRes.className = 'result'; inRes.textContent = 'Type an expression to convert it.'; inSteps.hidden = true; return;
  }
  const data = await post('/api/infix-postfix', { expression });
  if (!data.ok) { inRes.className = 'result err'; inRes.textContent = data.error; inSteps.hidden = true; return; }
  inRes.className = 'result';
  inRes.replaceChildren();
  const big = document.createElement('span'); big.className = 'big'; big.textContent = data.postfix;
  inRes.appendChild(big);
  if (data.value !== null && data.value !== undefined) {
    const v = document.createElement('span'); v.textContent = 'Value: ' + fmt(data.value); inRes.appendChild(v);
  }
  inBody.replaceChildren();
  data.steps.forEach((s) => {
    const tr = document.createElement('tr');
    [s.token, s.action, s.stack, s.output].forEach((txt, i) => {
      const td = document.createElement('td'); td.textContent = txt; if (i === 0) td.className = 'tok'; tr.appendChild(td);
    });
    inBody.appendChild(tr);
  });
  inSteps.hidden = false;
}, 200);
inIn.addEventListener('input', inRun);
document.querySelectorAll('[data-ex]').forEach((b) => b.addEventListener('click', () => { inIn.value = b.dataset.ex; inRun(); inIn.focus(); }));
