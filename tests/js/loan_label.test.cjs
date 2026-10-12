// Chạy: node tests/js/loan_label.test.cjs (trích loanLabel từ p01.js; không cần DOM)
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(require('path').join(__dirname,'../../src/pcms/web/p01.js'),'utf8');
const m=src.match(/^function loanLabel\(.*\}$/m);assert(m,'không thấy loanLabel');
global.fmt=n=>new Intl.NumberFormat('vi-VN').format(Number(n));global.dateText=v=>String(v).split('-').reverse().join('/');
eval(m[0]+';global.L=loanLabel');
assert.strictEqual(L({party_name:'Kết',name:'Kết 5tr',date:'2026-09-20',gross:'5000000',current:'5000000',setup:true}),'Kết · 20/09/2026 · gốc 5.000.000 · dư 5.000.000');
assert.strictEqual(L({party_name:'Kết',name:'Khoản mới',date:null,gross:null,current:null,setup:false}),'Kết · chưa có ngày · chưa thiết lập gốc (Khoản mới)');
assert(!/PERSON|LOAN|PROPERTY/.test(L({party_name:'Kết',name:'x',date:'2026-09-25',gross:'10000000',current:'7000000',setup:true})));
console.log('loan_label: OK');
