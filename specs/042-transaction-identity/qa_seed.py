import base64,uuid,sys
from pcms.p01 import P01Store
from p01_fixtures import statement
st=P01Store('/tmp/pcms-042-qa');act=lambda a,**d:st.apply(a,d,str(uuid.uuid4()))
stage=sys.argv[1]
ROWS=[('20/09/2026','Cho Ket vay 5tr','FT26267843740784','5000000','','995000000'),('25/09/2026','Cho Ket vay 10tr','K2','10000000','','985000000'),('26/09/2026','Ket tra goc','K3','','3000000','988000000'),
      ('27/09/2026','Ket tra lai','K4','','200000','988200000'),('28/09/2026','Tien luong','S1','','20000000','1008200000'),('29/09/2026','Chua dung','X1','10000','','1008190000')]
if stage=='old':
    act('account',name='QA vay',reference='000123',opening='1000000000',effective_date='2026-09-01',opening_source='QA giả');aid=st.state()['accounts'][0]['id']
    act('import',account=aid,filename='sao-ke-thang-9.xlsx',content=base64.b64encode(statement(ROWS,1000000000,1008190000,start='01/09/2026',end='30/09/2026')).decode());act('publish',batch=st.state()['imports'][-1]['id'])
    act('object-quick-create',kind='LOAN',party_name='Kết',name='Khoản Kết');pr={p['name']:p['id'] for p in st.state()['profiles']}
    act('loan-setup',profile=pr['Khoản Kết'],direction='RECEIVABLE',opening='0',confirm_zero=True,effective_date='2026-09-20',source='QA giả',reason='QA')
    act('category-create',name='Kết',description='',parent='principal');kn=next(n['id'] for n in st.state()['categories'] if n['name']=='Kết')
    act('category-object-add',category='principal',profile=pr['Kết'])                                       # người Kết là thành viên Gốc vay
    tx={t['reference']:t['id'] for t in st.state()['transactions']}
    act('classify',ids=[tx['FT26267843740784']],parts=[dict(category='principal',node=kn,profile=pr['Khoản Kết'])])   # ca lỗi: phân loại ở Gốc vay › Kết
    act('classify',ids=[tx['K2']],parts=[dict(category='principal',profile=pr['Khoản Kết'])]);act('classify',ids=[tx['K3']],parts=[dict(category='principal',profile=pr['Khoản Kết'])])
    act('classify',ids=[tx['K4']],parts=[dict(category='interest',profile=pr['Khoản Kết'])]);act('classify',ids=[tx['S1']],parts=[dict(category='income')])
    act('category-create',name='Property',type='expense')
    pc=next(n['id'] for n in st.state()['categories'] if n['name']=='Property')
    act('legacy-import',category=pc,name='Xuân Mai QA',type='PROPERTY',text="31/08/2023\tCK ket dat XM\tFT23243502050032\\BNK\t700,000,000\t\t1\n19/11/2022\tRut tien XM\tTT2232308045\\XMI\t350,000,000\t\t2\n")   # lịch sử cũ, chưa có tài khoản (mã P43)
else:
    aid=st.state()['accounts'][0]['id']
    act('import',account=aid,filename='sao-ke-thang-9-nhap-lai.xlsx',content=base64.b64encode(statement(ROWS,1000000000,1008190000,start='01/09/2026',end='30/09/2026')).decode())    # nhập lặp nguyên file
    bad=[list(r) for r in ROWS];bad[2][4]='3500000'
    act('import',account=aid,filename='sao-ke-sai-noi-dung.xlsx',content=base64.b64encode(statement([tuple(r) for r in bad],1000000000,1008190000,start='01/09/2026',end='30/09/2026')).decode())   # cùng mã K3 khác số tiền
    act('account',name='QA tài khoản khác',reference='000456',opening='1000000000',effective_date='2026-09-01',opening_source='QA giả');other=st.state()['accounts'][-1]['id']
    act('import',account=other,filename='sao-ke-tai-khoan-khac.xlsx',content=base64.b64encode(statement(ROWS,1000000000,1008190000,start='01/09/2026',end='30/09/2026',account='000456')).decode())   # cùng mã, khác tài khoản
    for b in st.state()['imports']:
        if b['status']!='PUBLISHED':act('recheck-import',batch=b['id'])
print('ok',stage)
