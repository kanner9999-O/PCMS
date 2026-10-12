# Data Model — 013 asset-overview
`state['asset_snapshots']`: `[{id, at, note (≤500), actor, data, hash}]` — chỉ thêm.
`view['assets']`:
```
{currencies:{VND:{assets:{total, groups:[{key,label,value|None,has_data,basis,weight,as_of,detail[],target}]},
                  liabilities:{total, groups:[…]}, net:{value, label|None}},
              USDT:{…}},
 warnings:[{code,label,count,target}], realty_basis:{VALUE,COST,NONE:[{id,name}]},
 snapshots:[{id,at,note,hash,data,delta_vs_previous}], delta:{vs,VND:{assets,liabilities,net},USDT:{…}}|None, notes:[…]}
```
Nhóm VND tài sản: `bank`, `receivable`, `realty`; nợ: `payable`. Nhóm USDT tài sản: `crypto`, `trx_receivable`; nợ: `trx_advance`. Không có trường tổng hợp hai đồng tiền; không có tỷ giá.
