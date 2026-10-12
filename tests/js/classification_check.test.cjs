// Chạy: node tests/js/classification_check.test.cjs (trích checkRowLabel từ p01.js; không cần DOM)
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(require('path').join(__dirname,'../../src/pcms/web/p01.js'),'utf8');
const m=src.match(/^function checkRowLabel\(.*\}$/m);assert(m,'không thấy checkRowLabel');eval(m[0]+';global.L=checkRowLabel');
assert.strictEqual(L({label:'Gốc vay',split:false,tx_amount:'500000000'}),'Gốc vay');
assert.strictEqual(L({label:'Chi tiêu › Ăn uống',split:true,tx_amount:'100000'}),'Chi tiêu › Ăn uống (phần của giao dịch 100000)');
assert.strictEqual(L({label:'Hoàn chi tiêu',split:false,tx_amount:'300000'}),'Hoàn chi tiêu');
console.log('classification_check: OK');
