let snapshot = null;
const HISTORY_KEY = 'kurs-converter-history-v1';
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

function format(value, currency) {
  return `${new Intl.NumberFormat('ru-RU', {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(value)} ${currency}`;
}

function setStatus(text, kind = 'loading') { const element = $('status'); element.textContent = text; element.className = `status ${kind}`; }
function currentDateText() { return snapshot ? new Date(`${snapshot.effective_date}T12:00:00`).toLocaleDateString('ru-RU', {day:'2-digit', month:'long', year:'numeric'}) : '—'; }

function updateRateInfo() {
  if (!snapshot) return;
  const from = $('source').value, to = $('target').value;
  $('from-sign').textContent = from;
  $('pair-rate').textContent = from && to ? `1 ${from} = ${format(calculate(1, from, to, snapshot.rates), to)}` : '—';
  $('rate-date').textContent = currentDateText();
}

function populate(data) {
  snapshot = data.snapshot;
  const currencies = Object.keys(snapshot.rates).sort();
  for (const id of ['source', 'target']) {
    const select = $(id), old = select.value;
    select.innerHTML = currencies.map((code) => `<option value="${code}">${code}</option>`).join('');
    select.value = currencies.includes(old) ? old : (id === 'source' && currencies.includes('EUR') ? 'EUR' : 'MDL');
    select.disabled = false;
  }
  const note = data.from_cache ? ' Используются сохранённые локальные данные.' : data.prior_date ? ' Использован ближайший опубликованный рабочий день.' : '';
  $('rate-meta').textContent = `Источник: ${snapshot.source}.${note}`;
  setStatus(data.from_cache ? 'Работаем с сохранённым курсом' : 'Официальные курсы загружены', data.from_cache ? 'warning' : 'good');
  $('convert').disabled = !$('amount').value.trim();
  updateRateInfo();
}

async function loadRates(useCache = false) {
  setStatus(useCache ? 'Загружаем сохранённый курс…' : 'Обновляем официальные курсы…');
  try {
    const response = await fetch(`/api/rates${useCache ? '?cache=1' : ''}`);
    const data = await response.json();
    if (!response.ok) {
      if (data.cache_available && confirm(`Нет соединения с BNM. Использовать сохранённый курс от ${data.cached_date}?`)) return loadRates(true);
      throw new Error(data.error || 'Не удалось получить курсы.');
    }
    populate(data);
  } catch (error) {
    setStatus(error.message || 'Не удалось получить курсы.', 'error');
    $('rate-meta').textContent = 'После первого успешного обновления здесь станет доступен сохранённый курс.';
  }
}

function readHistory() { try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); } catch (_) { return []; } }
function renderHistory() {
  const items = readHistory(), node = $('history'), clear = $('clear-history');
  clear.hidden = items.length === 0;
  if (!items.length) { node.className = 'history-empty'; node.textContent = 'Здесь появятся последние выполненные конвертации.'; return; }
  node.className = 'history-list';
  node.innerHTML = items.map((item) => `<article class="history-item"><b>${item.fromAmount} → ${item.toAmount}</b><span>${item.date}</span></article>`).join('');
}
function saveHistory(amount, from, result, to) {
  const next = [{fromAmount: format(amount, from), toAmount: format(result, to), date: `Курс BNM · ${currentDateText()}`}, ...readHistory()].slice(0, 6);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(next)); renderHistory();
}

function convert() {
  const error = $('amount-error'); error.textContent = '';
  try {
    if (!snapshot) throw new Error('Курсы ещё загружаются. Подождите немного.');
    const amount = validateAmount($('amount').value), from = $('source').value, to = $('target').value;
    const result = calculate(amount, from, to, snapshot.rates);
    $('result').textContent = format(result, to);
    $('formula').textContent = from === to ? 'Выбрана одинаковая валюта — сумма не меняется.' : `${format(amount, from)} → ${format(result, to)}`;
    $('copy-result').disabled = false;
    saveHistory(amount, from, result, to);
  } catch (err) { $('amount-error').textContent = err.message; $('result').textContent = '—'; $('copy-result').disabled = true; }
}

async function copyResult() {
  const text = $('result').textContent;
  try { await navigator.clipboard.writeText(text); $('copy-result').textContent = 'Скопировано ✓'; setTimeout(() => { $('copy-result').textContent = 'Скопировать результат'; }, 1500); } catch (_) { $('amount-error').textContent = 'Не удалось скопировать результат автоматически.'; }
}

function init() {
  if (!$('amount')) return;
  $('amount').addEventListener('input', () => { $('convert').disabled = !$('amount').value.trim(); $('amount-error').textContent = ''; });
  ['source','target'].forEach((id) => $(id).addEventListener('change', updateRateInfo));
  $('convert').addEventListener('click', convert);
  $('amount').addEventListener('keydown', (event) => { if (event.key === 'Enter') convert(); });
  document.querySelectorAll('[data-amount]').forEach((button) => button.addEventListener('click', () => { $('amount').value = button.dataset.amount; $('convert').disabled = false; convert(); }));
  $('swap').addEventListener('click', () => { const from = $('source').value; $('source').value = $('target').value; $('target').value = from; updateRateInfo(); if ($('amount').value.trim()) convert(); });
  $('refresh').addEventListener('click', () => loadRates());
  $('copy-result').addEventListener('click', copyResult);
  $('clear-history').addEventListener('click', () => { localStorage.removeItem(HISTORY_KEY); renderHistory(); });
  renderHistory(); loadRates();
}

window.CurrencyFlow = { validateAmount, calculate, format };
document.addEventListener('DOMContentLoaded', init);
