// Chạy: node tests/js/loan_business.test.cjs (spec 046: trích hàm thuần của bộ Chi tiết nghiệp vụ từ p01.js; không cần DOM)
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(require('path').join(__dirname,'../../src/pcms/web/p01.js'),'utf8').split('\n');
const grab=n=>{const l=src.find(x=>x.startsWith('function '+n+'('));assert(l,'không thấy '+n);return l};
eval(['lbComponentOptions','lbLineIn','lbRemaining','lbLoansFor'].map(grab).join(';')+';global.F={lbComponentOptions,lbRemaining,lbLoansFor}');
const comps={RECEIVABLE_OUT:{broker:'Trả phí môi giới',principal:'Giải ngân'},RECEIVABLE_IN:{interest:'Thu lãi',principal:'Thu gốc'},PAYABLE_IN:{principal:'Nhận tiền vay'},PAYABLE_OUT:{principal:'Trả gốc',interest:'Trả lãi'}};
assert.deepStrictEqual(F.lbComponentOptions(comps,'RECEIVABLE','IN',true).map(o=>o.value),['principal','interest']);        // tiền vào Cho vay: không có Giải ngân
assert.deepStrictEqual(F.lbComponentOptions(comps,'RECEIVABLE','OUT',false).map(o=>o.label),['Giải ngân']);                 // không môi giới: không có Trả phí môi giới
assert.deepStrictEqual(F.lbComponentOptions(comps,'RECEIVABLE','OUT',true).map(o=>o.value),['principal','broker']);
assert.deepStrictEqual(F.lbComponentOptions(comps,'PAYABLE','IN',true).map(o=>o.label),['Nhận tiền vay']);
const groups=[{category:'h',person:'k',amount:'70360000'},{category:'h',person:'t',amount:'5000000'}];
const r=F.lbRemaining(groups,[{category:'h',person:'k',amount:'60000000'},{category:'h',person:'k',amount:'300000'},{category:'h',person:'k',amount:''},{category:'h',person:'t',amount:'abc'}]);
assert.deepStrictEqual(r.map(x=>x.remaining),[10060000n,5000000n]);                                                         // số không hợp lệ không được tính
// vòng sửa 29/10 (PO review P2): phần đã chọn khoản khi phân loại chỉ nhận dòng của đúng khoản đó; phần cũ (loan null) nhận khoản khác
const g2=[{category:'h',person:'k',loan:'cv1',amount:'600000'},{category:'h',person:'k',loan:'cv2',amount:'400000'},{category:'h',person:'k',loan:null,amount:'100'}];
assert.deepStrictEqual(F.lbRemaining(g2,[{category:'h',person:'k',loan:'cv1',amount:'600000'},{category:'h',person:'k',loan:'cv2',amount:'100000'},{category:'h',person:'k',loan:'cv3',amount:'100'}]).map(x=>x.remaining),[0n,300000n,0n]);
const loans=[{id:'a',person:'k',direction:'RECEIVABLE',status:'ACTIVE'},{id:'b',person:'k',direction:'RECEIVABLE',status:'COMPLETED'},{id:'c',person:'k',direction:'PAYABLE',status:'ACTIVE'},{id:'d',person:'t',direction:'RECEIVABLE',status:'ACTIVE'}];
assert.deepStrictEqual(F.lbLoansFor(loans,'k','RECEIVABLE').map(l=>l.id),['a']);                                         // đúng người, đúng chiều, chưa hoàn tất
console.log('loan_business: OK');
