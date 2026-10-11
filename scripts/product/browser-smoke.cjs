// Run against an isolated synthetic store; this test intentionally changes data.
const {chromium}=require(process.env.PCMS_PLAYWRIGHT || 'playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const page=await browser.newPage({viewport:{width:1440,height:1100}}), errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.PCMS_TEST_URL||'http://127.0.0.1:8788';
 const get=()=>page.evaluate(async()=>await (await fetch('/api/state')).json());
 const go=async route=>{await page.goto(base+'/#'+route);await page.locator('#content .panel, #content .wealth').first().waitFor()};
 const click=async action=>page.locator(`[data-action="${action}"]`).first().click();
 const fill=async(name,value)=>page.locator(`[name="${name}"]`).fill(value);
 const submit=async()=>{await page.locator('#edit-form button[type=submit]').click();await page.locator('#modal').waitFor({state:'hidden'})};
 await go('overview');const initial=await get();assert.equal(initial.state.mode,'SYNTHETIC');
 await page.locator('#new-tx').click();await fill('amount','1000000');await fill('description','Chi phí QA');await submit();
 let v=await get();assert.equal(Number(v.report.net_worth),Number(initial.report.net_worth)-40);
 await go('transactions');await click('correct');await fill('amount','2000000');await fill('reason','Sửa sai QA');await submit();
 v=await get();assert.equal(Number(v.report.net_worth),Number(initial.report.net_worth)-80);
 await go('assets');await click('asset-detail');await click('valuation');await fill('price','4900000000');await submit();
 v=await get();assert.equal(Number(v.report.net_worth),Number(initial.report.net_worth)+3920);
 await go('allocation');await click('propose');await submit();await click('approve');await page.waitForFunction(()=>document.querySelector('[data-action=execute]'));await click('execute');await page.waitForFunction(()=>document.body.textContent.includes('Đã thực hiện'));
 v=await get();assert.equal(v.state.decisions.at(-1).status,'APPROVED');assert.ok(v.state.decisions.at(-1).executed);
 await go('imports');await click('sample');await page.locator('[data-action=accept]').first().waitFor();await click('accept');await submit();await click('reject');await fill('reason','Bỏ qua QA');await submit();
 assert.equal((await get()).report.pending_imports,0);
 await go('close');await click('reconcile-demo');await page.waitForFunction(()=>document.body.textContent.includes('Sẵn sàng chốt'));await click('close');await submit();
 v=await get();assert.equal(v.state.snapshots.at(-1).cutoff,'2026-09-28');const frozen=v.state.snapshots.at(-1);
 await page.locator('#new-tx').click();await fill('amount','1000');await submit();
 await click('reconcile-demo');await page.waitForFunction(()=>document.body.textContent.includes('Sẵn sàng chốt'));await click('close');await submit();
 v=await get();assert.equal(v.state.snapshots.at(-1).version,2);assert.deepEqual(v.state.snapshots.at(-2),frozen);
 await page.reload();await page.locator('#content .panel').first().waitFor();assert.equal((await get()).state.snapshots.at(-1).version,2);
 await go('settings');const downloadPromise=page.waitForEvent('download');await page.locator('a[href="/api/backup"]').click();const download=await downloadPromise;const backupPath='/tmp/pcms-browser-backup.json';await download.saveAs(backupPath);
 await page.locator('#restore-file').setInputFiles(backupPath);await page.locator('[name=confirm]').waitFor();await fill('confirm','KHOI PHUC');await submit();assert.equal((await get()).state.audit.at(-1).action,'RESTORE');
 for(const route of ['overview','assets','flows','transactions','imports','allocation','risk','planning','close','history','settings']){await go(route);assert.ok(await page.locator('h1').textContent());assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth),false,route+' overflows');}
 await go('planning');await page.locator('#plan-monthly').fill('1000');await page.locator('#plan-rate').fill('0');await page.locator('#plan-target').fill('1000000');await click('save-plan');await page.waitForFunction(()=>document.querySelector('#toast').textContent.includes('Đã lưu'));assert.equal((await get()).state.decisions.at(-1).title,'Kế hoạch vốn 1 / 3 / 5 năm');
 await go('assets');await page.screenshot({path:'/tmp/pcms-assets-qa.png',fullPage:true});
 await page.setViewportSize({width:390,height:844});for(const route of ['overview','assets','flows','transactions','imports','allocation','risk','planning','close','history','settings']){await go(route);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth),false,'mobile '+route+' overflows');}
 assert.deepEqual(errors,[]);console.log('PASS: 11 pages desktop/mobile, transaction, correction, valuation, approval/execution, import review, close/restatement, reload, backup/restore, capital planning; zero browser errors.');await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
