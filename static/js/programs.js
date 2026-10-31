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

/* Queue: enqueue and dequeue */
const qViz = $('q-viz'), qMsg = $('q-msg'), qSize = $('q-size'), qVal = $('q-value');
function qEl(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }
function qRender(d) {
  qViz.replaceChildren();
  if (!d.items.length) qViz.appendChild(qEl('span', 'q-empty', 'Queue is empty'));
  d.items.forEach((v, i) => {
    const last = d.items.length - 1;
    const hit = (d.highlight === 'front' && i === 0) || (d.highlight === 'rear' && i === last);
    const node = qEl('div', 'q-item' + (hit ? ' hit' : ''));
    node.appendChild(qEl('span', 'q-tag', i === 0 && i === last ? 'FRONT / REAR' : i === 0 ? 'FRONT' : i === last ? 'REAR' : ' '));
    node.appendChild(qEl('div', 'q-box', v));
    qViz.appendChild(node);
  });
  qSize.textContent = d.size + ' / ' + d.capacity;
  qMsg.textContent = d.message;
  qMsg.className = 'll-msg' + (d.ok ? '' : ' err');
}
async function qAct(action) {
  const res = await fetch('/api/queue/' + action, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ value: qVal.value }) });
  const d = await res.json();
  qRender(d);
  if (d.ok && action === 'enqueue') { qVal.value = ''; qVal.focus(); }
}
document.querySelectorAll('[data-q]').forEach((b) => b.addEventListener('click', () => qAct(b.dataset.q)));
qVal.addEventListener('keydown', (e) => { if (e.key === 'Enter') qAct('enqueue'); });
fetch('/api/queue').then((r) => r.json()).then(qRender);

/* Sorting algorithms */
(function () {
  const info = JSON.parse($('sort-info-data').textContent);
  const tabs = [...document.querySelectorAll('#sort-tabs .tab')];
  const input = $('sort-in'), viz = $('sort-viz'), msg = $('sort-msg'), stats = $('sort-stats'), done = $('sort-done');
  const playBtn = $('sort-play'), backBtn = $('sort-back'), nextBtn = $('sort-next'), speedEl = $('sort-speed');
  const SPEEDS = [1200, 800, 500, 300, 150];
  const LECTURE = { merge: [35, 22, 90, 4, 50, 20, 30, 40, 1], other: [4, 3, 7, 1, 5] };
  let algo = 'bubble', frames = [], idx = 0, timer = null, lastKey = '', moves = 'Swaps';

  function parse() {
    const parts = input.value.trim().split(/[\s,]+/).filter(Boolean);
    if (parts.length < 2 || parts.length > 12) throw new Error('Enter 2 to 12 whole numbers.');
    return parts.map((p) => {
      if (!/^-?\d+$/.test(p)) throw new Error('"' + p + '" is not a whole number.');
      const n = parseInt(p, 10);
      if (Math.abs(n) > 999) throw new Error('Keep each number between -999 and 999.');
      return n;
    });
  }
  function say(text, isErr) { msg.textContent = text; msg.className = 'sort-msg' + (isErr ? ' err' : ''); }

  function draw(f) {
    viz.replaceChildren();
    const inRange = f.range ? (i) => i >= f.range[0] && i <= f.range[1] : () => true;
    f.a.forEach((v, i) => {
      const box = document.createElement('div');
      let cls = 'sbox';
      if (f.range && !inRange(i)) cls += ' dim';
      if (f.sorted.includes(i)) cls += ' sorted';
      if (f.mark === i) cls += ' mark';
      if (f.cmp.includes(i)) cls += ' cmp';
      if (f.swap.includes(i)) cls += ' swap';
      box.className = cls;
      const num = document.createElement('span'); num.className = 'sval'; num.textContent = v;
      const ix = document.createElement('span'); ix.className = 'sidx'; ix.textContent = i;
      box.append(num, ix);
      viz.appendChild(box);
    });
  }
  const plain = (a) => ({ a, cmp: [], swap: [], mark: null, range: null, sorted: [] });

  function showInfo() {
    const s = info[algo];
    $('si-def').textContent = s.definition;
    $('si-best').replaceChildren(...s.best_for.map((t) => { const li = document.createElement('li'); li.textContent = t; return li; }));
    $('si-best-t').textContent = s.best_time; $('si-avg-t').textContent = s.avg_time;
    $('si-worst-t').textContent = s.worst_time; $('si-space').textContent = s.space;
    document.querySelectorAll('#complexity-table tbody tr').forEach((tr) => tr.classList.toggle('current', tr.dataset.algo === algo));
    moves = s.moves_label;
  }

  function setIdx(i) {
    idx = Math.max(0, Math.min(frames.length - 1, i));
    const f = frames[idx];
    draw(f); say(f.msg);
    stats.textContent = 'Step ' + (idx + 1) + ' of ' + frames.length + '  ·  Comparisons: ' + f.c + '  ·  ' + moves + ': ' + f.s;
    backBtn.disabled = idx === 0;
    nextBtn.disabled = idx === frames.length - 1;
    if (idx === frames.length - 1) done.textContent = info[algo].name + ' finished with ' + f.c + ' comparisons and ' + f.s + ' ' + moves.toLowerCase() + '.';
  }

  function invalidate() {
    pause(); frames = []; lastKey = ''; stats.textContent = ''; done.textContent = '';
    backBtn.disabled = nextBtn.disabled = false;
    try { draw(plain(parse())); say('Press “Sort and play” to start.'); }
    catch (e) { viz.replaceChildren(); say(e.message, true); }
  }

  async function ensure() {
    let values;
    try { values = parse(); } catch (e) { say(e.message, true); return false; }
    const key = algo + '|' + values.join(',');
    if (key === lastKey && frames.length) return true;
    const res = await fetch('/api/sort', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ algorithm: algo, values }) });
    const data = await res.json();
    if (!data.ok) { say(data.error, true); return false; }
    frames = data.frames; lastKey = key; moves = data.moves_label; setIdx(0);
    return true;
  }

  function pause() { if (timer) { clearInterval(timer); timer = null; } playBtn.textContent = '▶ Sort and play'; }
  function startTimer() {
    clearInterval(timer);
    timer = setInterval(() => { if (idx >= frames.length - 1) { pause(); return; } setIdx(idx + 1); }, SPEEDS[speedEl.value - 1]);
    playBtn.textContent = '⏸ Pause';
  }
  async function play() {
    if (timer) { pause(); return; }
    if (!(await ensure())) return;
    if (idx >= frames.length - 1) setIdx(0);
    startTimer();
  }

  tabs.forEach((t) => t.addEventListener('click', () => {
    algo = t.dataset.algo;
    tabs.forEach((x) => { const on = x === t; x.classList.toggle('active', on); x.setAttribute('aria-selected', on); });
    showInfo(); invalidate();
  }));
  input.addEventListener('input', invalidate);
  playBtn.addEventListener('click', play);
  nextBtn.addEventListener('click', async () => { pause(); if (await ensure()) setIdx(idx + 1); });
  backBtn.addEventListener('click', async () => { pause(); if (await ensure()) setIdx(idx - 1); });
  $('sort-reset').addEventListener('click', () => { pause(); if (frames.length) { setIdx(0); } else invalidate(); });
  speedEl.addEventListener('input', () => { if (timer) startTimer(); });
  $('sort-random').addEventListener('click', () => {
    const set = new Set();
    while (set.size < 8) set.add(1 + Math.floor(Math.random() * 99));
    input.value = [...set].join(', '); invalidate();
  });
  $('sort-example').addEventListener('click', () => {
    input.value = (algo === 'merge' ? LECTURE.merge : LECTURE.other).join(', '); invalidate();
  });

  showInfo(); invalidate();
})();
