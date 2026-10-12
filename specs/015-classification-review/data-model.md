# Data Model — 015 classification-review
Không đổi lưu trữ. `classification_review` trả:
```
{account, scope:{mode,start,end,cutoff?}, now,
 summary:{transactions, classified, unclassified, in, out, net, spend?},
 checks:{transactions:{source,grouped,ok,difference}, money_in:{…}, money_out:{…}}, reconciled,
 groups:[{key,name,type,transactions,in,out,net_spend?,latest,unclassified:bool,
          rows:[{transaction,date,reference,description,amount,direction,label,object,split,tx_amount,classified_at,recent,status,sources}]}],
 empty:bool, draft:true}
```
`status` ∈ DRAFT|APPROVED (có trong snapshot nào); `sources` = số liên kết nguồn; `classified_at` ISO hoặc `null`.
