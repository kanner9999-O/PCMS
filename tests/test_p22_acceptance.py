import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError

def D_(x):return Decimal(str(x))

class P22Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name)
        self.act('crypto-place',name='Binance',kind='EXCHANGE');self.act('crypto-place',name='Ví lạnh',kind='WALLET',start_date='2026-09-01')
        self.bn,self.vl=self.pid('Binance'),self.pid('Ví lạnh')
        self.bal(self.bn,'BTC','0.5');self.bal(self.bn,'USDT','10000')
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,a,**d):
        with self.assertRaises(ValidationError):self.act(a,**d)
    def view(self):return self.store.view()['crypto']
    def pid(self,name):return next(p['id'] for p in self.view()['places'] if p['name']==name)
    def place(self,pid):return next(p for p in self.view()['places'] if p['id']==pid)
    def q(self,pid,ticker,bucket='HOLDING'):
        r=next((c for c in self.place(pid)['components'] if c['ticker']==ticker and c['bucket']==bucket),None);return D_(r['quantity']) if r else None
    def bal(self,pid,t,qty,date='2026-10-01',bucket='HOLDING'):self.act('crypto-balance',place=pid,ticker=t,network='',bucket=bucket,quantity=qty,date=date,source='Ảnh chụp')
    def trade(self,kind,qty,price,date,**k):self.act('crypto-trade',kind=kind,place=self.bn,ticker='BTC',network='',quantity=qty,price=price,date=date,source='Mã GD',**k)

    def test_buy_sell_with_fee_example(self):
        self.trade('BUY','0.1','60000','2026-10-05',fee='6',fee_ticker='USDT')
        self.assertEqual((self.q(self.bn,'BTC'),self.q(self.bn,'USDT')),(D_('0.6'),D_('3994')))
        self.trade('SELL','0.2','65000','2026-10-08')
        self.assertEqual((self.q(self.bn,'BTC'),self.q(self.bn,'USDT')),(D_('0.4'),D_('16994')))
        row=next(c for c in self.place(self.bn)['components'] if c['ticker']=='BTC');self.assertEqual((row['confirmed_quantity'],row['ledger_moves']),('0.5',2))
        self.trade('BUY','0.1','50000','2026-10-09',fee='0.0001',fee_ticker='BTC');self.assertEqual(self.q(self.bn,'BTC'),D_('0.4999'))   # phí bằng coin trừ vào coin

    def test_same_day_and_earlier_not_counted_and_later_confirmation_resets(self):
        self.trade('BUY','1','100','2026-10-01');self.trade('BUY','1','100','2026-09-20')
        self.assertEqual(self.q(self.bn,'BTC'),D_('0.5'))                       # mốc 01/10 đã gồm
        self.trade('BUY','1','100','2026-10-02');self.assertEqual(self.q(self.bn,'BTC'),D_('1.5'))
        self.bal(self.bn,'BTC','1.4','2026-10-03');self.assertEqual(self.q(self.bn,'BTC'),D_('1.4'))     # mốc mới
        rec=self.place(self.bn)['reconciliations'];self.assertEqual((rec[0]['ticker'],D_(rec[0]['expected']),D_(rec[0]['difference'])),('BTC',D_('1.5'),D_('-0.1')))

    def test_transfer_fee_and_no_base_warning(self):
        self.act('crypto-transfer',from_place=self.bn,to_place=self.vl,ticker='BTC',network='',quantity='0.3',received='0.2995',date='2026-10-05',source='Tx')
        self.assertEqual(self.q(self.bn,'BTC'),D_('0.2'));self.assertEqual(self.q(self.vl,'BTC'),D_('0.2995'))
        w=self.view()['ledger_warnings'];self.assertEqual([(x['place'],x['code']) for x in w],[('Ví lạnh','NO_BASE')])
        self.assertEqual(next(c for c in self.place(self.vl)['components'] if c['ticker']=='BTC')['warnings'],['NO_BASE'])
        self.bal(self.vl,'BTC','0.2995','2026-10-06');self.assertEqual(self.view()['ledger_warnings'],[])

    def test_negative_not_in_value_and_void(self):
        self.act('crypto-price',ticker='BTC',network='',price='60000',date='2026-10-01',source='s')
        self.trade('SELL','1','60000','2026-10-02')
        self.assertEqual(self.q(self.bn,'BTC'),D_('-0.5'));self.assertEqual([x['code'] for x in self.view()['ledger_warnings']],['NEGATIVE'])
        self.assertEqual(D_(self.view()['totals']['value']),0)           # số âm không vào giá trị; USDT chưa có giá
        v=self.view();self.assertEqual(next(c for c in self.place(self.bn)['components'] if c['ticker']=='BTC')['value'],None)
        mid=v['movements'][0]['id'];self.err('crypto-movement-void',movement=mid,reason='')
        self.act('crypto-movement-void',movement=mid,reason='Nhập nhầm');self.assertEqual(self.q(self.bn,'BTC'),D_('0.5'));self.assertEqual(self.view()['movements'][0]['status'],'VOID')
        self.err('crypto-movement-void',movement=mid,reason='lần hai')

    def test_validation(self):
        base=dict(kind='BUY',place=self.bn,ticker='BTC',network='',quantity='0.1',price='60000',date='2026-10-05',source='s')
        for bad in (dict(kind='X'),dict(quantity='0'),dict(quantity='-1'),dict(quantity='0.1234567890123456789'),dict(price='0'),dict(price='1.1234567890123'),dict(source=''),dict(date=''),dict(ticker='USDT'),dict(fee='-1'),dict(fee='1',fee_ticker='ETH'),dict(place='nope')):
            self.err('crypto-trade',**{**base,**bad})
        self.err('crypto-trade',**{**base,'place':self.vl,'date':'2026-08-31'})                       # trước mốc theo dõi
        t=dict(from_place=self.bn,to_place=self.vl,ticker='BTC',network='',quantity='0.3',received='0.3',date='2026-10-05',source='s')
        for bad in (dict(to_place=self.bn),dict(received='0.4'),dict(received='0'),dict(quantity='0'),dict(source=''),dict(to_place='nope')):self.err('crypto-transfer',**{**t,**bad})
        self.act('crypto-place-archive',place=self.vl,reason='x');self.err('crypto-transfer',**t);self.err('crypto-trade',**{**base,'place':self.vl})

    def test_no_movements_same_as_before_and_assets_use_ledger(self):
        before=self.view();self.assertEqual(before['movements'],[]);self.assertEqual(before['ledger_warnings'],[])
        self.act('crypto-price',ticker='BTC',network='',price='60000',date='2026-10-01',source='s');self.act('crypto-price',ticker='USDT',network='',price='1',date='2026-10-01',source='s')
        v0=D_(self.view()['totals']['value']);self.assertEqual(v0,D_('0.5')*60000+10000)
        self.trade('BUY','0.1','60000','2026-10-05')
        v1=D_(self.view()['totals']['value']);self.assertEqual(v1,D_('0.6')*60000+4000)
        usdt=next(g for g in self.store.view()['assets']['currencies']['USDT']['assets']['groups'] if g['key']=='crypto');self.assertEqual(D_(usdt['value']),v1)

    def test_read_only_and_backup(self):
        self.trade('BUY','0.1','60000','2026-10-05');n=len(self.store.events());self.view();self.assertEqual(len(self.store.events()),n)
        other=P01Store(tempfile.mkdtemp());other.restore(self.store.backup(),str(uuid4()));self.assertEqual(len(other.view()['crypto']['movements']),1)

if __name__=='__main__':unittest.main()
