// Chạy: node tests/js/classification_sort.test.cjs (trích compareTx từ p01.js, không cần DOM)
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(require('path').join(__dirname,'../../src/pcms/web/p01.js'),'utf8');
const m=src.match(/^function compareTx\(.*\}$/m);assert(m,'không thấy compareTx');eval(m[0]+';global.cmp=compareTx');
const T=(ref,amount,date,order=1)=>({reference:ref,signed_amount:String(amount),date,order});
const list=[T('a',-50000,'2026-09-02'),T('b',20000,'2026-09-05'),T('c',-20000,'2026-09-03'),T('d',0,'2026-09-01'),T('e',-1000000,'2026-09-04'),T('f',20000,'2026-09-05',2)];
const refs=mode=>list.slice().sort(cmp(mode)).map(t=>t.reference).join('');
assert.strictEqual(refs('amount_asc'),'dfbcae','tăng dần theo trị tuyệt đối; hòa → ngày mới trước, rồi order lớn trước');
assert.strictEqual(refs('amount_desc'),'eafbcd','giảm dần theo trị tuyệt đối');
assert.strictEqual(refs('date'),'fbecad','mặc định theo ngày mới nhất');
const big=[T('x','9007199254740993','2026-09-01'),T('y','9007199254740992','2026-09-01'),T('z','-9007199254740994','2026-09-01')];
assert.strictEqual(big.slice().sort(cmp('amount_asc')).map(t=>t.reference).join(''),'yxz','số lớn hơn 2^53 so đúng bằng BigInt');
console.log('classification_sort: OK');
