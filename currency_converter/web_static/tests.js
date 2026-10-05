function test(name, callback) { try { callback(); return {name, ok:true}; } catch (error) { return {name, ok:false, message:error.message}; } }
function equal(actual, expected) { if (actual !== expected) throw new Error(`ожидалось ${expected}, получено ${actual}`); }
function run() { const {validateAmount, calculate} = window.CurrencyFlow; const results = [
  test('Конвертация USD → EUR', () => equal(Number(calculate(100, 'USD', 'EUR', {USD:'17.2', EUR:'20', MDL:'1'}).toFixed(2)), 86)),
  test('Обратная конвертация EUR → USD', () => equal(Number(calculate(86, 'EUR', 'USD', {USD:'17.2', EUR:'20', MDL:'1'}).toFixed(2)), 100)),
  test('Одинаковые валюты не меняют сумму', () => equal(calculate(12.5, 'EUR', 'EUR', {EUR:'20', MDL:'1'}), 12.5)),
  test('Принимается десятичная запятая', () => equal(validateAmount('12,50'), 12.5)),
  test('Ноль не проходит валидацию', () => { try { validateAmount('0'); } catch (_) { return; } throw new Error('ошибка не была показана'); }),
  test('Буквы не проходят валидацию', () => { try { validateAmount('abc'); } catch (_) { return; } throw new Error('ошибка не была показана'); })
]; const list = document.getElementById('test-list'); list.innerHTML = results.map(r => `<li class="${r.ok?'pass':'fail'}">${r.ok?'✓':'×'} ${r.name}${r.message ? `: ${r.message}` : ''}</li>`).join(''); }
document.getElementById('run-tests').addEventListener('click', run); run();
