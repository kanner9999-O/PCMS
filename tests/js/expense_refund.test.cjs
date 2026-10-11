// Chạy: node tests/js/expense_refund.test.cjs (trích catLabel, spendNet từ p01.js; không cần DOM)
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(require('path').join(__dirname,'../../src/pcms/web/p01.js'),'utf8');
const grab=n=>{const m=src.match(new RegExp('^function '+n+'\\(.*\\}$','m'));assert(m,'không thấy '+n);return m[0]};
const categories={income:'Thu nhập',expense:'Chi tiêu',principal:'Gốc vay'};
eval(grab('catLabel')+';'+grab('spendNet')+';global.L=catLabel;global.N=spendNet');
assert.strictEqual(L('expense',true),'Hoàn chi tiêu');assert.strictEqual(L('expense',false),'Chi tiêu');
assert.strictEqual(L('income',true),'Thu nhập');assert.strictEqual(L('principal',true),'Gốc vay');
assert.strictEqual(N('1000000','600000'),'400000','chi ròng = chi − hoàn chi');
assert.strictEqual(N('100000','600000'),'-500000','âm khi hoàn nhiều hơn chi');
assert.strictEqual(N(undefined,'300000'),'-300000');assert.strictEqual(N('1000000',undefined),'1000000');
assert.strictEqual(N('9007199254740993','1'),'9007199254740992','số lớn > 2^53 đúng bằng BigInt');
console.log('expense_refund: OK');
