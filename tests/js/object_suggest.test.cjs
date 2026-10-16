// Chạy: node tests/js/object_suggest.test.cjs (trích hàm gợi ý đối tượng từ p01.js; không cần DOM)
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(require('path').join(__dirname,'../../src/pcms/web/p01.js'),'utf8');
for(const f of ['objNorm','objMatchRange','objSuggest']){assert(new RegExp('^function '+f+'\\(').test(src.split('\n').find(l=>l.startsWith('function '+f+'(')) ||''),'không thấy '+f)}
const grab=n=>src.split('\n').find(l=>l.startsWith('function '+n+'('));
eval([grab('objNorm'),grab('objMatchRange'),grab('objSuggest'),'global.N=objNorm;global.R=objMatchRange;global.S=objSuggest'].join(';'));
const rows=[{name:'Tươi',kind:'PERSON'},{name:'Kết',kind:'PERSON'},{name:'Kết2',kind:'OBJECT'},{name:'Xuân Mai',kind:'PROPERTY'},{name:'Mỹ Kết',kind:'PERSON'},{name:'Đức',kind:'PERSON'}];
assert.strictEqual(N('Đức Xuân'),'duc xuan');
assert.deepStrictEqual(S(rows,'tuoi','all').map(o=>o.name),['Tươi']);
assert.deepStrictEqual(S(rows,'KET','all').map(o=>o.name),['Kết','Kết2','Mỹ Kết']);          // khớp đầu tên xếp trước
assert.deepStrictEqual(S(rows,'ket','PERSON').map(o=>o.name),['Kết','Mỹ Kết']);                 // lọc loại
assert.deepStrictEqual(S(rows,'xuan mai','all').map(o=>o.name),['Xuân Mai']);
assert.deepStrictEqual(S(rows,'duc','all').map(o=>o.name),['Đức']);
assert.strictEqual(S(rows,'','all').length,6);assert.strictEqual(S(rows,'zzz','all').length,0);
assert.deepStrictEqual(R('Xuân Mai','mai'),[5,8]);assert.deepStrictEqual(R('Mỹ Kết','ket'),[3,6]);assert.strictEqual(R('Tươi','x'),null);assert.deepStrictEqual(R('Tươi',''),[0,0]);
console.log('object_suggest: OK');
