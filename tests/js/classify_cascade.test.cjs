// Chạy: node tests/js/classify_cascade.test.cjs (trích hàm chọn danh mục theo cấp từ p01.js; không cần DOM)
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(require('path').join(__dirname,'../../src/pcms/web/p01.js'),'utf8').split('\n');
const grab=n=>{const l=src.find(x=>x.startsWith('function '+n+'('));assert(l,'không thấy '+n);return l};
eval(['cascChildren','cascValue','cascPathFor'].map(grab).join(';')+';global.F={cascChildren,cascValue,cascPathFor}');
const nodes=[{id:'r1',name:'Property',parent:null,root:'expense',status:'ACTIVE'},{id:'c1',name:'Chung cư',parent:'r1',root:'expense',status:'ACTIVE'},{id:'g1',name:'Chung cư A',parent:'c1',root:'expense',status:'ACTIVE'},
  {id:'e1',name:'Ăn uống',parent:'expense',root:'expense',status:'ACTIVE'},{id:'a1',name:'Cũ',parent:'r1',root:'expense',status:'ARCHIVED'},{id:'p1',name:'Cho vay A',parent:'principal',root:'principal',status:'ACTIVE'}];
const c={nodes};
assert.deepStrictEqual(F.cascChildren(c,'N:r1').map(n=>n.id),['c1']);                               // lưu trữ không hiện
assert.deepStrictEqual(F.cascChildren(c,'S:expense').map(n=>n.id),['e1']);assert.deepStrictEqual(F.cascChildren(c,'S:principal').map(n=>n.id),['p1']);
assert.deepStrictEqual(F.cascChildren(c,'c1').map(n=>n.id),['g1']);assert.deepStrictEqual(F.cascChildren(c,'S:unknown'),[]);
assert.deepStrictEqual(F.cascValue(c,['S:expense']),{category:'expense',node:''});assert.deepStrictEqual(F.cascValue(c,['S:unknown']),{category:'unknown',node:''});
assert.deepStrictEqual(F.cascValue(c,['N:r1','c1','g1']),{category:'expense',node:'g1'});assert.deepStrictEqual(F.cascValue(c,['S:principal','p1']),{category:'principal',node:'p1'});
assert.deepStrictEqual(F.cascValue(c,['N:r1']),{category:'expense',node:'r1'});assert.deepStrictEqual(F.cascValue(c,[]),{category:'expense',node:''});
assert.deepStrictEqual(F.cascPathFor(c,'expense','g1'),['N:r1','c1','g1']);assert.deepStrictEqual(F.cascPathFor(c,'expense','r1'),['N:r1']);
assert.deepStrictEqual(F.cascPathFor(c,'expense','e1'),['S:expense','e1']);assert.deepStrictEqual(F.cascPathFor(c,'principal','p1'),['S:principal','p1']);
assert.deepStrictEqual(F.cascPathFor(c,'income',''),['S:income']);assert.deepStrictEqual(F.cascPathFor(c,'expense','a1'),['N:r1','a1']);
for(const [cat,node] of [['expense','g1'],['principal','p1'],['expense','e1'],['unknown','']])assert.deepStrictEqual(F.cascValue(c,F.cascPathFor(c,cat,node)),{category:cat,node});   // vòng khứ hồi
console.log('classify_cascade: OK');
