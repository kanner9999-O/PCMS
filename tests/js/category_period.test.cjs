// Chạy: node tests/js/category_period.test.cjs (trích catPeriodRange từ p01.js; không cần DOM)
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(require('path').join(__dirname,'../../src/pcms/web/p01.js'),'utf8');
const m=src.match(/^function catPeriodRange\(.*\}$/m);assert(m,'không thấy catPeriodRange');eval(m[0]+';global.R=catPeriodRange');
assert.deepStrictEqual(R('this_month','2026-10-12'),{start:'2026-10-01',end:'2026-10-31'});
assert.deepStrictEqual(R('last_month','2026-10-12'),{start:'2026-09-01',end:'2026-09-30'});
assert.deepStrictEqual(R('last_month','2026-01-15'),{start:'2025-12-01',end:'2025-12-31'},'tháng 1 → tháng 12 năm trước');
assert.deepStrictEqual(R('this_month','2028-02-10'),{start:'2028-02-01',end:'2028-02-29'},'năm nhuận');
assert.deepStrictEqual(R('this_quarter','2026-10-12'),{start:'2026-10-01',end:'2026-12-31'});
assert.deepStrictEqual(R('last_quarter','2026-10-12'),{start:'2026-07-01',end:'2026-09-30'});
assert.deepStrictEqual(R('last_quarter','2026-02-01'),{start:'2025-10-01',end:'2025-12-31'},'quý 1 → quý 4 năm trước');
assert.deepStrictEqual(R('this_quarter','2026-05-31'),{start:'2026-04-01',end:'2026-06-30'});
assert.deepStrictEqual(R('all','2026-10-12'),{start:'',end:''});
console.log('category_period: OK');
