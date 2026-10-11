import copy
import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError

def D_(x):return Decimal(str(x))

class P14Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,a,**d):
        with self.assertRaises(ValidationError):self.act(a,**d)
    def view(self):return self.store.view()['crypto']
    def place(self,name):return next(p for p in self.view()['places'] if p['name']==name)
    def coin(self,key):return next((c for c in self.view()['coins'] if c['key']==key),None)
    def pid(self,name):return self.place(name)['id']
    def setup(self):
        self.act('crypto-place',name='Ví lạnh 1',kind='WALLET');self.act('crypto-place',name='Binance',kind='EXCHANGE');self.act('crypto-place',name='BingX',kind='EXCHANGE',start_date='2026-09-01')
    def bal(self,place,ticker,qty,date='2026-10-01',bucket='HOLDING',network='',source='Ảnh chụp'):
        self.act('crypto-balance',place=self.pid(place),ticker=ticker,network=network,bucket=bucket,quantity=qty,date=date,source=source)

    # ---- US1 -----------------------------------------------------------
    def test_confirmations_latest_void_and_validation(self):
        self.setup();self.bal('Ví lạnh 1','btc','0.5','2026-10-01');self.bal('Ví lạnh 1','BTC','0.6','2026-10-08')
        row=lambda:next(c for c in self.place('Ví lạnh 1')['components'] if c['ticker']=='BTC')
        self.assertEqual(D_(row()['quantity']),Decimal('0.6'));self.assertEqual(len(self.place('Ví lạnh 1')['history']),2)
        newest=next(b for b in self.place('Ví lạnh 1')['history'] if b['quantity']=='0.6')['id'];self.err('crypto-balance-void',balance=newest,reason='')
        self.act('crypto-balance-void',balance=newest,reason='Nhập nhầm');self.assertEqual(D_(row()['quantity']),Decimal('0.5'));self.assertEqual(len(self.place('Ví lạnh 1')['history']),2)
        self.err('crypto-balance-void',balance=newest,reason='lần hai')
        self.bal('Ví lạnh 1','BTC','0','2026-10-09');self.assertEqual(D_(row()['quantity']),0)              # số lượng 0 hợp lệ
        self.bal('Ví lạnh 1','ETH','1.123456789012345678');self.assertEqual(next(c for c in self.place('Ví lạnh 1')['components'] if c['ticker']=='ETH')['quantity'],'1.123456789012345678')
        for bad in (dict(quantity='-1'),dict(quantity='0.1234567890123456789'),dict(quantity='abc'),dict(ticker='b t c'),dict(ticker=''),dict(source=''),dict(date='bad'),dict(date='')):
            args=dict(place=self.pid('Ví lạnh 1'),ticker='BTC',network='',bucket='HOLDING',quantity='1',date='2026-10-01',source='s');args.update(bad);self.err('crypto-balance',**args)
        self.err('crypto-balance',place=self.pid('BingX'),ticker='BTC',network='',bucket='HOLDING',quantity='1',date='2026-08-31',source='s')   # trước mốc theo dõi
        self.err('crypto-place',name='ví LẠNH 1',kind='WALLET');self.err('crypto-place',name='X',kind='BANK');self.err('crypto-place',name='',kind='WALLET')

    def test_wallet_buckets_networks_and_archive(self):
        self.setup()
        for b in ('EARN_LOCKED','MARGIN_COLLATERAL','OPEN_POSITION','MARGIN_DEBT'):
            self.err('crypto-balance',place=self.pid('Ví lạnh 1'),ticker='BTC',network='',bucket=b,quantity='1',date='2026-10-01',source='s')   # ví riêng chỉ đang giữ
            self.bal('Binance','BTC','1',bucket=b)
        self.bal('Ví lạnh 1','USDT','100',network='trc20');self.bal('Ví lạnh 1','USDT','50',network='ERC20');self.bal('Ví lạnh 1','USDT','7')
        keys={c['key']:c['quantity'] for c in self.view()['coins'] if c['ticker']=='USDT'};self.assertEqual(keys,{'USDT|':'7','USDT|ERC20':'50','USDT|TRC20':'100'})   # khác mạng tách riêng
        self.act('crypto-place-archive',place=self.pid('Ví lạnh 1'),reason='Đã bán ví');self.err('crypto-place-archive',place=self.pid('Ví lạnh 1'),reason='x')
        self.err('crypto-balance',place=self.pid('Ví lạnh 1'),ticker='BTC',network='',bucket='HOLDING',quantity='1',date='2026-10-01',source='s')
        self.assertIsNone(self.coin('USDT|TRC20'));self.assertEqual(len(self.place('Ví lạnh 1')['history']),3)                                      # loại khỏi tổng, lịch sử còn
        self.assertFalse(any(k in str(self.view()).lower() for k in ('seed','private','mnemonic')))

    # ---- US2 -----------------------------------------------------------
    def test_exchange_buckets_do_not_double_count(self):
        self.setup();self.act('crypto-price',ticker='BTC',price='60000',date='2026-10-01',source='Binance')
        for b,q in (('HOLDING','0.2'),('MARGIN_COLLATERAL','0.1'),('OPEN_POSITION','5'),('MARGIN_DEBT','0.05')):self.bal('BingX','BTC',q,bucket=b)
        p=self.place('BingX');self.assertEqual(D_(p['asset_value']),18000)                                    # 0,3 × 60.000
        self.assertEqual(([x['quantity'] for x in p['positions']],[x['quantity'] for x in p['debts']]),(['5'],['0.05']))
        self.assertEqual(sorted(c['bucket'] for c in p['components']),['HOLDING','MARGIN_COLLATERAL'])
        self.bal('BingX','BTC','9','2026-10-05',bucket='OPEN_POSITION');self.bal('BingX','BTC','1','2026-10-05',bucket='MARGIN_DEBT')
        self.assertEqual(D_(self.place('BingX')['asset_value']),18000);self.assertEqual(D_(self.coin('BTC|')['quantity']),Decimal('0.3'))      # vị thế/nợ không đổi giá trị
        self.bal('BingX','BTC','0.4','2026-10-06',bucket='EARN_LOCKED');self.assertEqual(D_(self.place('BingX')['asset_value']),42000)

    # ---- US3 -----------------------------------------------------------
    def test_prices_value_and_weights(self):
        self.setup();self.bal('Ví lạnh 1','BTC','0.5');self.bal('Binance','ETH','10');self.bal('Binance','XYZ','1000')
        v=self.view();self.assertEqual((v['totals']['unpriced'],D_(v['totals']['value'])),(['ETH|','XYZ|','BTC|'] if False else sorted(['BTC|','ETH|','XYZ|']),0))   # chưa có giá nào
        self.assertTrue(all(c['value'] is None and c['weight'] is None for c in v['coins']))
        self.act('crypto-price',ticker='btc',price='60000',date='2026-10-01',source='Binance');self.act('crypto-price',ticker='ETH',price='2500',date='2026-10-01',source='Binance')
        v=self.view();self.assertEqual((D_(v['totals']['value']),v['totals']['unpriced']),(55000,['XYZ|']))
        self.assertEqual((D_(self.coin('BTC|')['value']),self.coin('BTC|')['weight']),(30000,'54.55'));self.assertEqual((self.coin('ETH|')['weight'],self.coin('XYZ|')['weight']),('45.45',None))
        self.assertEqual({p['name']:p['weight'] for p in v['places'] if p['status']=='ACTIVE'},{'Ví lạnh 1':'54.55','Binance':'45.45','BingX':'0.00'})
        self.act('crypto-price',ticker='BTC',price='70000',date='2026-10-05',source='Thẩm định');new=self.coin('BTC|')['price']
        self.assertEqual((new['price'],new['date']),('70000','2026-10-05'));self.assertEqual(D_(self.view()['totals']['value']),60000)
        self.act('crypto-price-void',price=new['id'],reason='Nhập nhầm');self.assertEqual(self.coin('BTC|')['price']['price'],'60000');self.assertEqual(len(self.view()['prices']),3)
        self.act('crypto-price',ticker='BTC',network='',price='0.000000000001',date='2026-10-06',source='s')
        for bad in (dict(price='0'),dict(price='-1'),dict(price='1.0000000000001'),dict(price='x'),dict(date=''),dict(source=''),dict(ticker='')):
            args=dict(ticker='BTC',price='1',date='2026-10-01',source='s');args.update(bad);self.err('crypto-price',**args)
        self.bal('Binance','BTC','0.5');self.assertEqual(D_(self.coin('BTC|')['quantity']),1)                  # cùng coin ở nhiều nơi gộp theo coin

    # ---- US4 -----------------------------------------------------------
    def test_capital_gap_label_and_no_profit_keys(self):
        self.setup();self.bal('Ví lạnh 1','BTC','0.5');self.bal('Binance','ETH','10')
        self.act('crypto-price',ticker='BTC',price='60000',date='2026-10-01',source='s');self.act('crypto-price',ticker='ETH',price='2500',date='2026-10-01',source='s')
        self.assertEqual((self.coin('BTC|')['capital'],self.coin('BTC|')['gap']),(None,None))
        self.act('crypto-capital',ticker='BTC',amount='25000',date='2026-09-15',source='Sao kê Binance')
        b=self.coin('BTC|');self.assertEqual((D_(b['gap']['amount']),b['capital']['amount']),(5000,'25000'));self.assertIn('không phải lãi/lỗ',b['gap']['label'])
        self.assertIsNone(self.coin('ETH|')['gap'])
        self.act('crypto-capital',ticker='BTC',amount='28000',date='2026-10-02',source='Cập nhật');self.assertEqual(D_(self.coin('BTC|')['gap']['amount']),2000)   # không cộng dồn
        new=self.coin('BTC|')['capital']['id'];self.act('crypto-capital-void',capital=new,reason='Sai');self.assertEqual(D_(self.coin('BTC|')['gap']['amount']),5000)
        self.act('crypto-capital',ticker='XYZ',amount='10',date='2026-10-01',source='s');self.assertIsNone(next((c for c in self.view()['coins'] if c['ticker']=='XYZ'),None))
        self.assertFalse(any(k in str(self.view()).lower() for k in ('profit','pnl',"'loss'")))
        self.err('crypto-capital',ticker='BTC',amount='0',date='2026-10-01',source='s');self.err('crypto-capital-void',capital=new,reason='lần hai')

    # ---- cross-cutting ---------------------------------------------------
    def test_read_only_isolated_and_backup(self):
        self.setup();self.bal('Ví lạnh 1','BTC','0.5');self.act('crypto-price',ticker='BTC',price='60000',date='2026-10-01',source='s')
        before={k:copy.deepcopy(self.store.state().get(k)) for k in ('accounts','transactions','profiles','snapshots','categories','realty')};events=self.store.backup()['events']
        self.view();self.assertEqual(self.store.backup()['events'],events)
        self.bal('Ví lạnh 1','ETH','1');self.assertEqual({k:self.store.state().get(k) for k in before},before)
        restore=P01Store(self.tmp.name+'/restore');restore.restore(self.store.backup(),'restore');self.assertEqual(restore.view()['crypto'],self.store.view()['crypto'])
        self.assertIn('crypto',self.store.view()['capabilities'])
