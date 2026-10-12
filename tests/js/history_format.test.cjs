// Chạy: node tests/js/history_format.test.cjs (trích stmtRowHtml/stmtListHtml từ p01.js; không cần DOM)
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(require('path').join(__dirname,'../../src/pcms/web/p01.js'),'utf8');
const row=src.match(/^function stmtRowHtml\(.*\}$/m),list=src.match(/^function stmtListHtml\(.*\}$/m);assert(row&&list,'không thấy hàm dòng chuẩn');
global.esc=v=>String(v??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));global.fmt=n=>new Intl.NumberFormat('vi-VN').format(Number(n));
eval(row[0]+';'+list[0]+';global.R=stmtRowHtml;global.L=stmtListHtml');
const base={transaction:'t1',date:'2026-09-24',reference:'L1',description:'ck',amount:'500000',direction:'OUT',label:'Gốc vay',sources:1};
assert(R(base).includes('-500.000')&&R(base).includes('Xem nguồn · 1 liên kết')&&R(base).includes('L1'));
assert(R({...base,direction:'IN'}).includes('income')&&!R({...base,direction:'IN'}).includes('-500'));
assert(R({...base,split:true,tx_amount:'900000'}).includes('phần của giao dịch 900.000'));
assert(R({...base,account:'Tech-999'}).includes('· Tech-999'));assert(['c-date','c-ref','c-desc','c-src','c-amt','c-lab'].every(k=>R(base).includes(k)),'đủ sáu ô');
assert(R({...base,status:'APPROVED',badge:'đã lưu trữ'}).includes('đã duyệt')&&R({...base,badge:'đã lưu trữ'}).includes('đã lưu trữ'));
const html=L([{...base,date:'2026-09-01',reference:'A'},{...base,date:'2026-09-24',reference:'B'},{...base,date:'2026-09-24',reference:'C'}]);
assert(html.indexOf('>C<')<html.indexOf('>B<')&&html.indexOf('>B<')<html.indexOf('>A<'),'mới nhất trước, hòa theo mã giảm dần');
console.log('history_format: OK');
