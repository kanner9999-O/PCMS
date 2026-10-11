# Contracts — 011 realty
Actions `POST /api/action`: `realty-valuation {property,value,date,source,note?}` · `realty-valuation-void {valuation,reason}` · `realty-mortgage {property,loan,purpose,note?}` · `realty-mortgage-end {mortgage,reason}` · `realty-contribution {property,party,amount,evidence,date?,note?}` · `realty-contribution-void {contribution,reason}`.
`GET /api/state`: `realty` + capability `realty`. `POST /api/realty-history {property}` → `{property,name,evidence,source_notice,capital,costs,rows[]}`.
Lỗi nghiệp vụ → `ValidationError` tiếng Việt. UI: nút "Bất động sản"; thẻ BĐS; hộp thoại Giá trị / Thế chấp / Góp vốn / Lịch sử; nhãn chênh lệch: "chưa thực hiện, chưa trừ chi phí và nợ, không phải lãi/lỗ".
