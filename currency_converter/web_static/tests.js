const cases = [
  ['usd-eur','Конвертация USD → EUR','100 USD при курсах 17,2 и 20 MDL дают 86 EUR.', () => equal(round(CurrencyFlow.calculate(100,'USD','EUR',{USD:'17.2',EUR:'20',MDL:'1'})),86)],
  ['eur-usd','Обратная конвертация EUR → USD','86 EUR возвращаются в 100 USD.', () => equal(round(CurrencyFlow.calculate(86,'EUR','USD',{USD:'17.2',EUR:'20',MDL:'1'})),100)],
  ['same','Одинаковые валюты','Сумма не меняется при EUR → EUR.', () => equal(CurrencyFlow.calculate(12.5,'EUR','EUR',{EUR:'20',MDL:'1'}),12.5)],
  ['comma','Десятичная запятая','Значение 12,50 принимается как число.', () => equal(CurrencyFlow.validateAmount('12,50'),12.5)],
  ['point','Десятичная точка','Значение 12.50 принимается как число.', () => equal(CurrencyFlow.validateAmount('12.50'),12.5)],
  ['empty','Пустая сумма','Пустое поле выдаёт понятную ошибку.', () => throws(() => CurrencyFlow.validateAmount(''))],
  ['zero','Нулевая сумма','Ноль не запускает конвертацию.', () => throws(() => CurrencyFlow.validateAmount('0'))],
  ['negative','Отрицательная сумма','Отрицательное число не принимается.', () => throws(() => CurrencyFlow.validateAmount('-10'))],
  ['letters','Буквы вместо суммы','Текст не проходит проверку.', () => throws(() => CurrencyFlow.validateAmount('abc'))],
  ['currency','Неизвестная валюта','Расчёт отклоняет отсутствующий код валюты.', () => throws(() => CurrencyFlow.calculate(10,'XXX','MDL',{MDL:'1'}))]
];
const state = {}; const grid = document.getElementById('test-grid');
function equal(actual, expected) { if (actual !== expected) throw new Error(`ожидалось ${expected}, получено ${actual}`); }
function round(value) { return Number(value.toFixed(2)); }
function throws(callback) { try { callback(); } catch (_) { return; } throw new Error('ожидалась ошибка, но её не было'); }
function execute(id) { const item = cases.find(([key]) => key === id); try { item[3](); state[id] = {ok:true, message:'Пройден'}; } catch (error) { state[id] = {ok:false, message:error.message}; } render(); }
function render() { grid.innerHTML = cases.map(([id,title,description]) => { const result = state[id]; return `<article class="test-card ${result ? (result.ok?'pass':'fail') : ''}"><h3>${title}</h3><p>${description}</p><footer><button data-test="${id}">Запустить</button><span class="test-state">${result ? (result.ok?'✓ '+result.message:'× '+result.message) : 'Не запускался'}</span></footer></article>`; }).join(''); document.querySelectorAll('[data-test]').forEach((button) => button.addEventListener('click', () => execute(button.dataset.test))); const results = Object.values(state); document.getElementById('test-summary').textContent = !results.length ? 'Ещё не запускались' : `Пройдено: ${results.filter(x=>x.ok).length} из ${cases.length}`; }
document.getElementById('run-all').addEventListener('click', () => cases.forEach(([id]) => execute(id))); render();
