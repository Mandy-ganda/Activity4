const viz = document.getElementById('ll-viz');
const msg = document.getElementById('ll-msg');
const sizeEl = document.getElementById('ll-size');
const valueEl = document.getElementById('ll-value');
const insertIdx = document.getElementById('ll-insert-index');
const removeIdx = document.getElementById('ll-remove-index');

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function render(nodes, highlight) {
  viz.replaceChildren();
  viz.appendChild(el('span', 'll-tag', 'HEAD'));
  viz.appendChild(el('span', 'll-arrow', '→'));
  nodes.forEach((v, i) => {
    const node = el('div', 'll-node' + (i === highlight ? ' hit' : ''));
    const box = el('div', 'll-box');
    box.appendChild(el('b', '', v));
    box.appendChild(el('i', '', '•'));
    node.appendChild(box);
    node.appendChild(el('span', 'll-idx', 'index ' + i));
    viz.appendChild(node);
    viz.appendChild(el('span', 'll-arrow', '→'));
  });
  viz.appendChild(el('span', 'll-null', 'NULL'));
  sizeEl.textContent = nodes.length;
}

function update(data) {
  render(data.nodes, data.highlight);
  msg.textContent = data.message;
  msg.className = 'll-msg' + (data.ok ? '' : ' err');
}

async function act(action) {
  const body = { value: valueEl.value };
  if (action === 'insert') body.index = insertIdx.value;
  if (action === 'remove_at') body.index = removeIdx.value;
  const res = await fetch('/api/list/' + action, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const data = await res.json();
  update(data);
  if (data.ok && ['append', 'prepend', 'insert'].includes(action)) { valueEl.value = ''; valueEl.focus(); }
}

document.querySelectorAll('[data-action]').forEach(b => b.addEventListener('click', () => act(b.dataset.action)));
valueEl.addEventListener('keydown', (e) => { if (e.key === 'Enter') act('append'); });

fetch('/api/list').then(r => r.json()).then(update);
