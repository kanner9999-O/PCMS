// Chạy: node tests/js/default_report_date.test.cjs  (trích hàm thuần từ p01.js, không cần DOM)
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(require('path').join(__dirname,'../../src/pcms/web/p01.js'),'utf8');
const grab=n=>{const m=src.match(new RegExp('^function '+n+'\\(.*\\}$','m'));assert(m,'không thấy '+n);return m[0]};
const dateText=s=>s,esc=s=>s;
eval(grab('defaultReportDate')+';'+grab('reportCoverage')+';global.f=defaultReportDate;global.c=reportCoverage');
const R=(...p)=>({source_periods:p.map(([start,end])=>({start,end}))});
assert.deepStrictEqual(f([R(['2026-09-01','2026-09-30'])],'2026-09-15'),{date:'2026-09-15',usedLatestSource:false},'hôm nay trong kỳ');
assert.deepStrictEqual(f([R(['2026-09-01','2026-09-30'])],'2026-10-11'),{date:'2026-09-30',usedLatestSource:true},'hôm nay ngoài kỳ');
assert.deepStrictEqual(f([R(['2026-09-01','2026-09-30']),R(['2026-08-01','2026-10-05'])],'2026-10-11'),{date:'2026-10-05',usedLatestSource:true},'nhiều tài khoản');
assert.deepStrictEqual(f([R()],'2026-10-11'),{date:'2026-10-11',usedLatestSource:false},'không có nguồn');
const rp=[R(['2026-09-01','2026-09-30'])];
assert.match(c(rp,'2026-11-01','2026-12-01'),/chưa có nguồn/,'kỳ ngoài nguồn');
assert.match(c(rp,'2026-09-15','2026-10-15'),/một phần kỳ/,'một phần');
assert.strictEqual(c(rp,'2026-09-01','2026-10-01'),'','phủ đủ');
console.log('default_report_date: OK');
