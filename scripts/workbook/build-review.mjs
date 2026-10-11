import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const [input, output] = process.argv.slice(2);
if (!input || !output) throw new Error('Usage: build-review.mjs input.json output-directory');
const p = JSON.parse(await fs.readFile(input, 'utf8'));
const owner = JSON.parse(await fs.readFile(new URL('../../config/owner-settings.json', import.meta.url), 'utf8')); 
const wb = Workbook.create();
const names = ['Tien_do','Thiet_lap','Tai_khoan','Doi_soat','Can_xac_nhan','Giao_dich'];
const sheets = Object.fromEntries(names.map(n => [n, wb.worksheets.add(n)]));
const fmt = '#,##0;(#,##0);0';
const categories = ['Chưa rõ','Lương / thu nhập','Chi sinh hoạt','Lãi nhận','Lãi / phí trả','Chuyển nội bộ','Đầu tư','Vay / trả nợ','Góp / rút vốn','Gốc và lãi cần tách','Hoàn / đảo giao dịch'];
const text = v => typeof v === 'string' && /^[=+@-]/.test(v) ? "'"+v : v;
const num = v => {const n = Number(v); if (!Number.isSafeInteger(n)) throw new Error('Unsafe workbook integer'); return n;};
function base(name,title,subtitle,headers,widths) {
  const s=sheets[name], last=String.fromCharCode(64+headers.length);
  s.showGridLines=false;
  s.getRange(`A1:${last}100`).format.font={name:'Arial',size:11,color:'#172B4D'};
  s.getRange(`A1:${last}100`).format.rowHeight=30;
  s.getRange('A1').values=[[title]];
  s.getRange('A1').format.font={name:'Arial',size:16,bold:true,color:'#172B4D'};
  s.getRange('A2').values=[[subtitle]];
  s.getRange('A2').format.font={name:'Arial',size:10,italic:true,color:'#46556B'};
  s.getRange(`A4:${last}4`).values=[headers];
  s.getRange(`A4:${last}4`).format={fill:'#233B53',font:{name:'Arial',color:'#FFFFFF',bold:true},wrapText:true,rowHeight:40};
  s.getRange(`A5:${last}100`).format.wrapText=true;
  s.getRange(`A4:${last}100`).format.verticalAlignment='center';
  widths.forEach((w,i)=>s.getRangeByIndexes(0,i,100,1).format.columnWidth=w);
  s.freezePanes.freezeRows(4);
  return s;
}
function rows(s,data){s.getRange('A5').write(data.map(r=>r.map(text)));}
function inputs(s,range){s.getRange(range).format.fill='#FFF1C2';s.getRange(range).format.font.color='#0000FF';}
function list(s,range,values){inputs(s,range);s.getRange(range).dataValidation={rule:{type:'list',values}};}
function note(s,cell,value){s.getRange(cell).values=[[value]];s.getRange(cell).format.wrapText=false;s.getRange(cell).format.font={name:'Arial',size:10,italic:true,color:'#46556B'};}

const settings=base('Thiet_lap','M0 — Thiết lập đợt thử','Ô vàng để điền; trả lời không tự kích hoạt ghi sổ hoặc đóng kỳ.',
 ['Nội dung cần chốt','Đề xuất / ngữ cảnh','Câu trả lời của owner','Lý do cần'],[30,43,35,43]);
rows(settings,[
 ['Người duyệt số liệu','Đã xác nhận trong trao đổi 28/09/2026',owner.approval_responsible,'Người chịu trách nhiệm xác nhận dữ liệu thật'],
 ['Phạm vi đợt thử','Hai tài khoản đã gửi; chưa đại diện toàn bộ tài sản',null,'Tránh tuyên bố đã có wealth map đầy đủ'],
 ['Đơn vị từng tài khoản','Đã xác nhận: giữ nguyên loại tiền / tài sản','VND giữ VND; USDT giữ USDT','Tổng hợp sang USDT để bước sau; nguồn tỷ giá chưa chốt'],
 ['Ngày opening','Kỳ sao kê bắt đầu 04/06/2024; số dư đầu kỳ đang lệch',null,'Chỉ chốt khi có bằng chứng phù hợp'],
 ['Múi giờ','Đề xuất Asia/Ho_Chi_Minh',null,'Sao kê hiện chỉ có ngày, không có giờ'],
 ['Người nhập / kiểm tra','Chưa xác nhận',null,'Phân công xử lý dữ liệu'],
 ['Nơi lưu / người truy cập','Hiện lưu local riêng; chưa chia sẻ cloud',null,'Quyền truy cập và backup cần được chốt'],
 ['Thu / chi theo thời điểm','Đề xuất theo thực thu / thực chi',null,'Tiền vay và mua đầu tư phải phân loại riêng'],
 ['Phạm vi chưa làm','LNW, hiệu quả đầu tư, AI, policy risk: chưa kích hoạt',null,'Không đặt con số hoặc policy ngầm'],
]);inputs(settings,'C5:C13');settings.getRange('A5:D13').format.rowHeight=54;settings.getRange('C5').format.fill='#E7EFE9';settings.getRange('C7').format.fill='#E7EFE9';

const ac=base('Tai_khoan','M1 — Danh mục tài khoản','Danh mục lấy từ hai file; owner chưa xác nhận đây là toàn bộ phạm vi.',
 ['Tài khoản','Nguồn','Loại tiền','Thuộc về ai?','Mục đích sử dụng','Đưa vào đợt thử?','Ghi chú'],[20,34,12,26,24,24,40]);
rows(ac,p.sources.map(s=>['****'+s.account_reference.slice(-4),s.source_filename,s.currency,null,null,'Chưa xác nhận',null]));
inputs(ac,'D5:E6');inputs(ac,'G5:G6');list(ac,'F5:F6',['Chưa xác nhận','Có','Không']);
list(ac,'E5:E6',['Chưa rõ','Sinh hoạt','Dự phòng','Đầu tư','Trading','Kinh doanh']);
note(ac,'A9','Tài sản và tài khoản khác chưa được kiểm kê. Tên trên sao kê không tự xác nhận quyền sở hữu kinh tế.');

const tx=base('Giao_dich','Giao dịch cần phân loại','Tiền vào / ra chưa phải thu nhập / chi phí. Chỉ điền I:K; nguồn và số tiền giữ nguyên.',
 ['STT','Tài khoản','Ngày','Nội dung trên sao kê','Tiền ra VND','Tiền vào VND','Số dư VND','Dòng nguồn','Phân loại đề xuất','Giải thích / tách khoản','Người review','Mã bank','ID nguồn'],
 [8,18,14,65,20,20,20,20,28,45,24,30,40]);
let transactions=[];
for (const s of p.sources) for (const t of s.transactions) transactions.push({s,t});
rows(tx,transactions.map(({s,t},i)=>[i+1,'****'+s.account_reference.slice(-4),new Date(t.effective_date+'T00:00:00Z'),t.description,num(t.debit),num(t.credit),num(t.reported_balance),`${s.source_id} / dòng ${t.source_row}`,'Chưa rõ',null,null,t.bank_reference,t.raw_record_id]));
// write preserves Date objects via direct values, not a JSON round-trip.
tx.getRange(`C5:C${transactions.length+4}`).setNumberFormat('dd/mm/yyyy');
tx.getRange(`E5:G${transactions.length+4}`).setNumberFormat(fmt);
tx.getRange(`A5:M${transactions.length+4}`).format.rowHeight=65;
list(tx,`I5:I${transactions.length+4}`,categories);inputs(tx,`J5:K${transactions.length+4}`);
tx.tables.add(`A4:M${transactions.length+4}`,true,'TransactionsReview');

const recon=base('Doi_soat','M2 — Đối soát sao kê','Đơn vị VND. Chênh lệch = số cuối kỳ nguồn − số cuối kỳ tính; chưa điều chỉnh đầu kỳ.',
 ['Tài khoản','Đầu kỳ nguồn','Tổng tiền vào','Tổng tiền ra','Cuối kỳ tính','Cuối kỳ nguồn','Chênh lệch','Số giao dịch','Nguồn'],
 [19,22,22,22,22,22,22,15,36]);
rows(recon,p.sources.map(s=>['****'+s.account_reference.slice(-4),num(s.reported_opening_balance),null,null,null,num(s.reported_closing_balance),null,null,s.source_filename]));
let cursor=5;
for (const [i,s] of p.sources.entries()) {
 const r=i+5, end=cursor+s.parsed_rows-1;
 recon.getRange(`C${r}`).formulas=[[`=SUM('Giao_dich'!F${cursor}:F${end})`]];
 recon.getRange(`D${r}`).formulas=[[`=SUM('Giao_dich'!E${cursor}:E${end})`]];
 recon.getRange(`E${r}`).formulas=[[`=B${r}+C${r}-D${r}`]];
 recon.getRange(`G${r}`).formulas=[[`=F${r}-E${r}`]];
 recon.getRange(`H${r}`).formulas=[[`=COUNT('Giao_dich'!A${cursor}:A${end})`]];
 cursor=end+1;
}
recon.getRange('B5:G6').setNumberFormat(fmt);
recon.getRange('G5:G6').conditionalFormats.add('cellIs',{operator:'notEqual',formula:0,format:{fill:'#FCE4D6',font:{color:'#9C2F20'}}});
note(recon,'A9','Số dư đầu kỳ của hai file trùng với số dư sau giao dịch đầu tiên. Xem Can_xac_nhan trước khi chốt.');
note(recon,'A10','Cuối kỳ trên sao kê là số liệu lịch sử năm 2024, không phải số dư hiện tại.');

const questions=base('Can_xac_nhan','Những việc cần owner xác nhận','Điền câu trả lời và nguồn bằng chứng. Không tự sửa số gốc; chưa có mục nào được coi là đã giải quyết.',
 ['Mã','Liên quan','Vấn đề','Cần làm gì?','Câu trả lời của owner','Bằng chứng / tham chiếu','Người trả lời'],[10,24,52,52,45,36,23]);
const qrows=[];
for(const s of p.sources){
 if(s.issues.some(i=>i.code==='PERIOD_BALANCE_MISMATCH'))qrows.push([`Q${qrows.length+1}`,'****'+s.account_reference.slice(-4),'Số dư đầu kỳ không khớp phép cộng toàn kỳ.','Xác nhận số dư ngay trước giao dịch đầu hoặc cung cấp chứng từ bổ sung.',null,null,null]);
 const repeated=s.issues.find(i=>i.code==='REPEATED_BANK_REFERENCE');
 if(repeated)qrows.push([`Q${qrows.length+1}`,`${s.source_id} dòng ${repeated.rows.join(', ')}`,'Hai dòng dùng chung mã bank, một tiền ra và một tiền vào.','Xác nhận bản chất hai dòng; không xóa vì trùng mã.',null,null,null]);
}
qrows.push([`Q${qrows.length+1}`,'Toàn bộ giao dịch','Tiền vào / ra chưa được phân loại kinh tế.','Chọn loại ở Giao_dich; khoản gồm gốc và lãi cần giải thích/tách số.',null,null,null]);
rows(questions,qrows);questions.getRange(`A5:G${qrows.length+4}`).format.rowHeight=65;
inputs(questions,`E5:G${qrows.length+4}`);

const progress=base('Tien_do','PCMS — Nghiệm thu theo milestone','Bản review 28/09/2026. Chưa có milestone nghiệp vụ nào được nghiệm thu hoàn thành.',
 ['Mốc','Kiểm chứng điều gì?','Đã có','Còn thiếu để đạt','Nghiệm thu'],[13,45,43,48,25]);
rows(progress,[
 ['M0','Phạm vi, người duyệt và cách vận hành được xác nhận.','Đã chốt Dũng duyệt; giữ nguyên loại tiền từng tài khoản.','Chốt phạm vi, opening, quyền truy cập và cách đóng kỳ.','Chưa nghiệm thu'],
 ['M1','Biết có những tài khoản, tài sản và nợ nào thuộc phạm vi.','Đã trích hai tài khoản từ sao kê.','Xác nhận sở hữu, mục đích và phạm vi đầy đủ.','Chưa nghiệm thu'],
 ['M2','Số dư khớp bằng chứng, không mất hoặc cộng trùng giao dịch.','Đã đưa 76 giao dịch vào review; có bảng đối soát.','Giải quyết hai số dư đầu kỳ; xác minh mã lặp; phân loại và duyệt ghi sổ.','Chưa nghiệm thu'],
 ['M3','Xem báo cáo và chạy được một kỳ review, đóng sổ, khôi phục.','Lõi chạy thử với dữ liệu giả lập đã có.','M2 đạt, báo cáo thật và quy trình đóng kỳ được owner duyệt.','Chưa nghiệm thu'],
]);progress.getRange('A5:E8').format.rowHeight=65;
progress.getRange('A11:B11').values=[['Việc đang xử lý','Số lượng']];
progress.getRange('A12').values=[['Giao dịch đã nhận']];
progress.getRange('B12').formulas=[[`=COUNT('Giao_dich'!A5:A${transactions.length+4})`]];
progress.getRange('A13').values=[['Giao dịch còn chưa rõ']];
progress.getRange('B13').formulas=[[`=COUNTIF('Giao_dich'!I5:I${transactions.length+4},"Chưa rõ")+COUNTBLANK('Giao_dich'!I5:I${transactions.length+4})`]];
progress.getRange('A14').values=[['Tài khoản còn lệch số dư']];
progress.getRange('B14').formulas=[['=COUNTIF(\'Doi_soat\'!G5:G6,"<>0")']];
progress.getRange('A12:A14').format.columnWidth=27;
note(progress,'A17','Thứ tự xem: Thiet_lap → Tai_khoan → Doi_soat → Can_xac_nhan → Giao_dich.');
note(progress,'A18','Ô vàng: mày điền. Các câu trả lời chỉ là đề nghị review, chưa tự ghi ledger hoặc duyệt milestone.');
note(progress,'A19','Đây là workbook nghiệm thu; file sao kê gốc được lưu riêng và không bị sửa khi điền workbook.');
note(progress,'A21','Nguồn: Account statement (12).xlsx và Account statement (13).xlsx; kỳ 04/06–02/08/2024.');

await fs.mkdir(output,{recursive:true});
// Verify arithmetic and live classification inputs before exporting.
const checks=await wb.inspect({kind:'table',range:'Doi_soat!A4:I6',include:'values,formulas',tableMaxRows:3,tableMaxCols:9});
await fs.writeFile(path.join(output,'formula-check.ndjson'),checks.ndjson);
const diffs=recon.getRange('G5:G6').values.flat();
if(diffs[0]!==-103000000||diffs[1]!==133799) throw new Error(`Unexpected reconciliation: ${diffs}`);
if(progress.getRange('B13').values[0][0]!==76) throw new Error('Unclassified count');
tx.getRange('I5').values=[['Chi sinh hoạt']];
if(progress.getRange('B13').values[0][0]!==75) throw new Error('Classification count did not update');
tx.getRange('I5').values=[['Chưa rõ']];
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},summary:'formula errors'});
await fs.writeFile(path.join(output,'error-scan.ndjson'),errors.ndjson);
for(const [name,range] of [['Tien_do','A1:E21'],['Thiet_lap','A1:D14'],['Tai_khoan','A1:G9'],['Doi_soat','A1:I10'],['Can_xac_nhan','A1:G9'],['Giao_dich','A1:H9'],['Giao_dich','I4:M9']]){
 const image=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(path.join(output,`${name}-${range.replace(':','-')}.png`),new Uint8Array(await image.arrayBuffer()));
}
const file=await SpreadsheetFile.exportXlsx(wb);
await file.save(path.join(output,'PCMS-nghiem-thu-v0.1.xlsx'));
console.log(JSON.stringify({workbook:path.join(output,'PCMS-nghiem-thu-v0.1.xlsx'),sheets:names,rows:transactions.length,reconciliation:diffs}));
