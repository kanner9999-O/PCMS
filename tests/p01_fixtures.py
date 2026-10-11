"""Independent synthetic statements for P01 QA; amounts are integer VND."""
from test_bank_statement import workbook


def statement(rows, opening, closing, start='01/10/2026', end='03/10/2026', account='000123', **changes):
    mapping={'B1':start,'D1':end,'B2':account}
    mapping.update(changes)
    return workbook(rows=rows,opening=str(opening),closing=str(closing),changes=mapping)


def fixtures():
    first=[('01/10/2026','Synthetic deposit','IN-01','','20000000','120000000'),('02/10/2026','Synthetic expense','OUT-01','5000000','','115000000')]
    overlap=[first[1],('03/10/2026','Synthetic new expense','OUT-02','3000000','','112000000')]
    return {
        '01-first.xlsx':statement(first,100000000,115000000,end='02/10/2026'),
        '02-overlap.xlsx':statement(overlap,120000000,112000000,start='02/10/2026'),
        '03-distinct.xlsx':statement([('04/10/2026','Same value A','OUT-03','1000000','','111000000'),('04/10/2026','Same value B','OUT-04','1000000','','110000000')],112000000,110000000,start='04/10/2026',end='04/10/2026'),
        '04-conflict.xlsx':statement([('01/10/2026','Changed amount','IN-01','','21000000','121000000'),('02/10/2026','Fresh must not post','OTHER','1000000','','120000000')],100000000,120000000),
        '05-mismatch.xlsx':statement(first,100000000,114000000),
        '06-split.xlsx':statement([('04/10/2026','Principal and interest','SPLIT-01','22000000','','90000000')],112000000,90000000,start='04/10/2026',end='04/10/2026'),
        '07-transfer-out.xlsx':statement([('05/10/2026','Own transfer out','TRANSFER-OUT','10000000','','80000000')],90000000,80000000,start='05/10/2026',end='05/10/2026'),
        '08-transfer-in.xlsx':statement([('06/10/2026','Own transfer in','TRANSFER-IN','','10000000','30000000')],20000000,30000000,start='06/10/2026',end='06/10/2026',account='000456'),
        '09-unsupported.xlsx':b'not a workbook',
        '10-pagination.xlsx':statement([('01/10/2026',f'Pagination QA {i:02}',f'PAGE-{i:02}','1000000','',str(100000000-i*1000000)) for i in range(1,26)],100000000,75000000,account='009999',end='01/10/2026'),
    }

if __name__=='__main__':
    from pathlib import Path
    destination=Path('outputs/p01-qa/fixtures')
    destination.mkdir(parents=True,exist_ok=True)
    for name,raw in fixtures().items():(destination/name).write_bytes(raw)
