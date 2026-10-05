let snapshot = null;
const $ = (id) => document.getElementById(id);

function validateAmount(raw) {
  const normalized = raw.trim().replace(',', '.');
  if (!normalized) throw new Error('Введите сумму для конвертации.');
  const value = Number(normalized);
  if (!Number.isFinite(value) || value <= 0) throw new Error('Сумма должна быть числом больше нуля.');
  return value;
}

function calculate(amount, from, to, rates) {
  if (!rates[from] || !rates[to]) throw new Error('Выбранная валюта отсутствует в текущем курсе.');
  return from === to ? amount : amount * Number(rates[from]) / Number(rates[to]);
}

function setStatus(text, kind = 'loading') { const node = $('status'); node.textContent = text; node.className = `status ${kind}`; }
function format(value, currency) { return new Intl.NumberFormat('ru-RU', {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(value) + ' ' + currency; }

function populate(data) {
  snapshot = data.snapshot;
  const codes = Object.keys(snapshot.rates).sort();
  for (const id of ['source', 'target']) {
    const select = $(id); const current = select.value;
    select.innerHTML = codes.map((code) => `<option value="${code}">${code}</option>`).join('');
    select.value = codes.includes(current) ? current : (id === 'source' && codes.includes('EUR') ? 'EUR' : 'MDL');
    select.disabled = false;
  }
  $('from-sign').textContent = $('source').value;
  $('convert').disabled = !$('amount').value.trim();
  const d = new Date(`${snapshot.effective_date}T12:00:00`);
  const dateText = d.toLocaleDateString('ru-RU', {day:'2-digit',month:'long',year:'numeric'});
  const modifier = data.from_cache ? ' Используются сохранённые локальные данные.' : data.prior_date ? ' Использован ближайший опубликованный рабочий день.' : '';
  $('rate-meta').textContent = `Источник: ${snapshot.source}. Дата курса: ${dateText}.${modifier}`;
  setStatus(data.from_cache ? 'Работаем с сохранённым курсом' : 'Официальные курсы загружены', data.from_cache ? 'warning' : 'good');
}

async function loadRates(forceCache = false) {
  setStatus(forceCache ? 'Загружаем сохранённый курс…' : 'Обновляем официальные курсы…');
  try {
    const response = await fetch(`/api/rates${forceCache ? '?cache=1' : ''}`);
    const data = await response.json();
    if (!response.ok) {
      if (data.cache_available && confirm(`Нет соединения с BNM. Использовать сохранённый курс от ${data.cached_date}?`)) return loadRates(true);
      throw new Error(data.error || 'Не удалось получить курсы.');
    }
    populate(data);
  } catch (error) {
    setStatus(error.message || 'Не удалось получить курсы.', 'error');
    $('rate-meta').textContent = 'После первого успешного обновления здесь будет доступен сохранённый курс.';
  }
}

function convert() {
  const error = $('amount-error'); error.textContent = '';
  try {
    if (!snapshot) throw new Error('Курсы ещё загружаются. Подождите немного.');
    const amount = validateAmount($('amount').value);
    const from = $('source').value, to = $('target').value;
    const result = calculate(amount, from, to, snapshot.rates);
    $('result').textContent = format(result, to);
    $('formula').textContent = from === to ? 'Выбрана одинаковая валюта — сумма не меняется.' : `${format(amount, from)} → ${format(result, to)}`;
  } catch (err) { $('amount-error').textContent = err.message; $('result').textContent = '—'; }
}

function init() {
  if (!$('amount')) return;
  $('amount').addEventListener('input', () => { $('convert').disabled = !$('amount').value.trim(); $('from-sign').textContent = $('source').value; });
  $('source').addEventListener('change', () => $('from-sign').textContent = $('source').value);
  $('convert').addEventListener('click', convert);
  $('amount').addEventListener('keydown', (event) => { if (event.key === 'Enter') convert(); });
  $('swap').addEventListener('click', () => { const from = $('source').value; $('source').value = $('target').value; $('target').value = from; $('from-sign').textContent = $('source').value; convert(); });
  $('refresh').addEventListener('click', () => loadRates());
  loadRates();
}
window.CurrencyFlow = { validateAmount, calculate };
document.addEventListener('DOMContentLoaded', init);
