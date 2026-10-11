"""Entirely fictional family-office dataset for an isolated product trial."""


def seed():
    return {
        'mode': 'SYNTHETIC', 'schema': 'pcms-product-1', 'as_of': '2026-09-28',
        'opening_date': '2026-07-01', 'owner': 'Dũng · vai trò thử nghiệm',
        'rates': {'VND': '0.00004', 'USDT': '1', 'USD': '1'},
        'rate_note': 'Tỷ giá giả lập cố định: 25.000 VND = 1 USDT; 1 USD = 1 USDT. Không phải giá thị trường.',
        'policy': {'single_asset_limit': '35', 'cash_floor': '20000', 'crypto_limit': '35',
                   'property_shock': '-15', 'business_shock': '-30', 'stock_shock': '-30', 'crypto_shock': '-50'},
        'accounts': [
            {'id': 'bank-main', 'name': 'Ngân hàng · Chi tiêu', 'currency': 'VND', 'pool': 'OPERATING', 'opening': '280000000'},
            {'id': 'bank-reserve', 'name': 'Ngân hàng · Dự phòng', 'currency': 'VND', 'pool': 'RESERVE', 'opening': '520000000'},
            {'id': 'broker-cash', 'name': 'Chứng khoán · Tiền chờ', 'currency': 'VND', 'pool': 'INVESTMENT', 'opening': '150000000'},
            {'id': 'crypto-cash', 'name': 'Ví USDT · Đầu tư', 'currency': 'USDT', 'pool': 'INVESTMENT', 'opening': '65000'},
            {'id': 'trading', 'name': 'Trading · Tách biệt', 'currency': 'USDT', 'pool': 'TRADING', 'opening': '12000'},
        ],
        'assets': [
            {'id': 'apt', 'name': 'Căn hộ Riverside', 'class': 'PROPERTY', 'currency': 'VND', 'quantity': '1',
             'price': '4800000000', 'ownership': '1', 'liquid': False, 'pool': 'INVESTMENT',
             'detail': {'area': 'Thành phố mẫu', 'rent': '24000000', 'occupancy': '100', 'cost': '4000000', 'purchase': '3800000000'}},
            {'id': 'land', 'name': 'Đất vườn · Đồng sở hữu', 'class': 'PROPERTY', 'currency': 'VND', 'quantity': '1',
             'price': '3200000000', 'ownership': '0.5', 'liquid': False, 'pool': 'INVESTMENT',
             'detail': {'area': 'Khu vực mẫu', 'rent': '0', 'occupancy': '0', 'cost': '1000000', 'purchase': '2400000000'}},
            {'id': 'business', 'name': 'An Phát Studio', 'class': 'BUSINESS', 'currency': 'VND', 'quantity': '1',
             'price': '6000000000', 'ownership': '0.6', 'liquid': False, 'pool': 'INVESTMENT',
             'detail': {'basis': 'EQUITY', 'revenue': '450000000', 'opex': '320000000', 'cash': '800000000', 'debt': '500000000', 'capex': '30000000', 'distribution': '30000000'}},
            {'id': 'fpt', 'name': 'FPT · cổ phiếu mẫu', 'class': 'STOCK', 'currency': 'VND', 'quantity': '1800',
             'price': '120000', 'ownership': '1', 'liquid': True, 'pool': 'INVESTMENT', 'detail': {'custody': 'Broker demo'}},
            {'id': 'vnm', 'name': 'VNM · cổ phiếu mẫu', 'class': 'STOCK', 'currency': 'VND', 'quantity': '2200',
             'price': '65000', 'ownership': '1', 'liquid': True, 'pool': 'INVESTMENT', 'detail': {'custody': 'Broker demo'}},
            {'id': 'btc', 'name': 'Bitcoin', 'class': 'CRYPTO', 'currency': 'USDT', 'quantity': '1.2',
             'price': '62000', 'ownership': '1', 'liquid': True, 'pool': 'INVESTMENT', 'detail': {'custody': 'Ví lạnh demo'}},
            {'id': 'eth', 'name': 'Ethereum', 'class': 'CRYPTO', 'currency': 'USDT', 'quantity': '20',
             'price': '2600', 'ownership': '1', 'liquid': True, 'pool': 'INVESTMENT', 'detail': {'custody': 'Ví lạnh demo'}},
            {'id': 'trx', 'name': 'TRON', 'class': 'CRYPTO', 'currency': 'USDT', 'quantity': '500000',
             'price': '0.3', 'ownership': '1', 'liquid': True, 'pool': 'INVESTMENT', 'detail': {'custody': 'Sàn demo'}},
        ],
        'liabilities': [
            {'id': 'mortgage', 'name': 'Vay mua Riverside', 'currency': 'VND', 'opening': '1600000000',
             'asset_id': 'apt', 'annual_rate': '8.5', 'due': '2026-10-05', 'next_payment': '18000000'},
            {'id': 'personal-loan', 'name': 'Vay cá nhân', 'currency': 'VND', 'opening': '180000000',
             'asset_id': None, 'annual_rate': '10', 'due': '2026-10-10', 'next_payment': '15000000'},
        ],
        'transactions': [
            {'id': f'seed-{month}-{idx}', 'date': f'2026-{month:02d}-{day:02d}', 'kind': kind,
             'account': 'bank-main', 'amount': amount, 'currency': 'VND', 'description': desc,
             'source': 'Dữ liệu giả lập', 'direction': 1, **extra}
            for month in (7, 8, 9)
            for idx, (day, kind, amount, desc, extra) in enumerate([
                (2, 'income', '85000000', 'Lương / thu nhập cá nhân', {}),
                (4, 'income', '24000000', 'Tiền thuê Riverside', {'asset': 'apt'}),
                (6, 'income', '30000000', 'Phân phối từ An Phát Studio', {'asset': 'business'}),
                (8, 'expense', '28000000', 'Sinh hoạt gia đình', {}),
                (10, 'expense', '4000000', 'Vận hành căn hộ', {'asset': 'apt'}),
                (12, 'expense', '12000000', 'Lãi vay bất động sản', {'liability': 'mortgage'}),
                (15, 'repay', '15000000', 'Trả gốc vay cá nhân', {'liability': 'personal-loan'}),
                (18, 'transfer', '20000000', 'Bổ sung quỹ dự phòng', {'to_account': 'bank-reserve'}),
            ])
        ],
        'valuations': [], 'decisions': [], 'reconciliations': [], 'snapshots': [],
        'imports': [], 'corrections': [], 'audit': [],
    }
