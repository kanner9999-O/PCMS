"""Dựng bộ QA giả cho spec 043 (không dùng dữ liệu thật). Chạy: PYTHONPATH=src:tests python3 specs/043-reclassify/qa_seed.py /tmp/pcms-043-qa"""
import base64,sys,uuid
from pcms.p01 import P01Store
from p01_fixtures import statement
st=P01Store(sys.argv[1]);act=lambda a,**d:st.apply(a,d,str(uuid.uuid4()))
ROWS=[('20/09/2026','Cho Ket vay 5tr','FT26267843740784','5000000','','995000000'),('25/09/2026','Cho Ket vay 10tr','K2','10000000','','985000000'),('26/09/2026','Ket tra goc','K3','','3000000','988000000'),
      ('27/09/2026','Ket tra lai','K4','','200000','988200000'),('28/09/2026','Tien luong','S1','','20000000','1008200000'),('29/09/2026','An uong va xang','X1','1000000','','1007200000'),('30/09/2026','Sieu thi','X2','600000','','1006600000')]
act('account',name='QA vay',reference='000123',opening='1000000000',effective_date='2026-09-01',opening_source='QA giả');aid=st.state()['accounts'][0]['id']
act('import',account=aid,filename='sao-ke-thang-9.xlsx',content=base64.b64encode(statement(ROWS,1000000000,1006600000,start='01/09/2026',end='30/09/2026')).decode());act('publish',batch=st.state()['imports'][-1]['id'])
act('object-quick-create',kind='LOAN',party_name='Kết',name='Kết 5tr');pr={p['name']:p['id'] for p in st.state()['profiles']}
act('object-quick-create',kind='LOAN',party=pr['Kết'],name='Kết 10tr');pr={p['name']:p['id'] for p in st.state()['profiles']}
for n,w in (('Kết 5tr','2026-09-20'),('Kết 10tr','2026-09-25')):act('loan-setup',profile=pr[n],direction='RECEIVABLE',opening='0',confirm_zero=True,effective_date=w,source='QA giả',reason='QA')
act('category-create',name='Kết',description='',parent='principal');kn=next(n['id'] for n in st.state()['categories'] if n['name']=='Kết')
tx={t['reference']:t['id'] for t in st.state()['transactions']}
st.require_membership=False                                                  # dữ liệu kiểu cũ (trước 042): ca Kết
act('classify',ids=[tx['FT26267843740784']],parts=[dict(category='principal',node=kn,profile=pr['Kết 5tr'])])
st.require_membership=True
for c in ('principal','interest'):act('category-object-add',category=c,profile=pr['Kết'])
act('classify',ids=[tx['K2']],parts=[dict(category='principal',profile=pr['Kết 10tr'])]);act('classify',ids=[tx['K3']],parts=[dict(category='principal',profile=pr['Kết 10tr'])])
act('classify',ids=[tx['K4']],parts=[dict(category='interest',profile=pr['Kết 10tr'])]);act('classify',ids=[tx['S1']],parts=[dict(category='income')])
for n in ('Ăn uống','Đi lại'):act('category-create',name=n,description='',parent='expense')
an,di=(next(n['id'] for n in st.state()['categories'] if n['name']==x) for x in ('Ăn uống','Đi lại'))
act('object-create',name='Mỹ',type='PERSON',category=an);act('object-create',name='Tươi',type='PERSON',category=an);pr={p['name']:p['id'] for p in st.state()['profiles']}
act('category-object-add',category=di,profile=pr['Mỹ'])
act('classify',ids=[tx['X1']],parts=[dict(category='expense',node=an,profile=pr['Mỹ'],amount='400000'),dict(category='expense',node=di,profile=pr['Mỹ'],amount='600000')])   # chia 2 phần
act('classify',ids=[tx['X2']],parts=[dict(category='expense',node=an,profile=pr['Tươi'])])
act('category-create',name='Nhà',description='',parent='investment');nha=next(n['id'] for n in st.state()['categories'] if n['name']=='Nhà')
act('object-create',name='Đất A',type='PROPERTY',category=nha);act('object-create',name='Đất B',type='PROPERTY',category=nha);pr={p['name']:p['id'] for p in st.state()['profiles']}
act('legacy-import',category=nha,profile=pr['Đất A'],account=aid,text="05/06/2023\tDat coc dat\tFT23Q1\t30,000,000\t\t1\n")
act('approve',account=aid,reason='Duyệt tháng 9 (QA giả)',confirm_unknown=True)
print('ok')
