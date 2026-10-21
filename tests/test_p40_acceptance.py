import unittest
import test_p18_acceptance as base

TXT="05/06/2023\tA\tFT1\t30,000,000\t\t1\n"

class P40Acceptance(base.P18Acceptance):
    """Tách danh mục/đối tượng, nghiệp vụ tạm dừng, một đường tạo, tên người, đồng bộ (spec 041). Cờ nghiệp vụ mặc định tắt."""
    def objs(self):return {o['name']:o for o in self.store.view()['objects']['rows']}
    def pid(self,name):return next(p['id'] for p in self.store.state()['profiles'] if p['name']==name)

    def test_business_paused_hidden_rejected_but_data_kept(self):
        self.store.business_enabled=True;self.act('business-migrate',confirm=True);self.assertEqual(self.store.view()['business']['loans'][0]['type'],'LOAN_LENT')
        self.store.business_enabled=False;B=self.store.view()['business'];self.assertEqual(B['enabled'],False);self.assertNotIn('loans',B);self.assertNotIn('totals',B)
        self.err('business-set',category='principal',profile=self.person,type='LOAN_LENT',effective_date='2026-09-01');self.err('business-clear',category='principal',profile=self.person,reason='x')
        e=next(x for x in self.store.state()['category_objects'] if x['profile']==self.person);self.assertEqual(e['business']['type'],'LOAN_LENT')           # dữ liệu giữ nguyên
        node=next(r for r in self.store.view()['categories']['roots'] if r['key']=='principal');o=next(x for x in node['objects'] if x['profile']==self.person)
        self.assertEqual((o['business'],o['loans']),(None,[]));k=self.objs()['Kết'];self.assertEqual(k['loans'],[]);self.assertTrue(all(c['business'] is None for c in k['categories']))
        self.store.business_enabled=True;self.assertEqual(self.store.view()['business']['loans'][0]['type'],'LOAN_LENT')                                      # bật lại: còn nguyên

    def test_every_creation_path_creates_a_typed_object_with_the_same_name_rule(self):
        self.act('category-create',name='Property',type='investment');cat=self.nodes()['Property']['id']
        self.act('object-create',name='A1',type='PERSON');self.act('category-object-add',category=cat,name='A2');self.act('object-quick-create',kind='PERSON',name='A3');self.act('object-quick-create',kind='PROPERTY',name='A4')
        self.act('profile',kind='PERSON',name='A5');self.act('profile',kind='PROPERTY',name='A6');self.act('legacy-import',category=cat,name='A7',type='PROPERTY',text=TXT);self.act('legacy-import',category=cat,name='A8',text=TXT.replace('FT1','FT2'))
        self.assertEqual({n:self.objs()[n]['kind'] for n in ('A1','A2','A3','A4','A5','A6','A7','A8')},{'A1':'PERSON','A2':'OBJECT','A3':'PERSON','A4':'PROPERTY','A5':'PERSON','A6':'PROPERTY','A7':'PROPERTY','A8':'OBJECT'})
        for name in ('a1',' A2  ','A3'):                                                                                    # mọi lối chặn tên trùng như nhau
            self.err('object-create',name=name,type='PERSON');self.err('category-object-add',category=cat,name=name);self.err('object-quick-create',kind='PERSON',name=name);self.err('object-quick-create',kind='PROPERTY',name=name);self.err('profile',kind='PERSON',name=name)
        self.err('object-create',name='Z',type='LOAN');self.err('object-create',name='Z');self.err('legacy-import',category=cat,name='Z',type='LOAN',text=TXT)
        self.assertEqual(self.store.legacy_preview(dict(category=cat,name='Mới',type='PROPERTY',text=TXT))['object']['kind'],'PROPERTY')

    def test_loan_money_shown_under_person_name_everywhere(self):
        self.act('object-quick-create',kind='LOAN',party_name='Anh',name='Khoản Anh');loan=self.pid('Khoản Anh');self.act('loan-setup',profile=loan,direction='RECEIVABLE',opening='0',confirm_zero=True,effective_date='2026-09-01',source='QA',reason='QA')
        self.classify(['X1'],[dict(category='principal',profile=loan)])
        names=[g['name'] for g in self.review()['groups']];self.assertIn('Gốc vay · Anh',names);self.assertFalse(any('Khoản ' in n for n in names))
        h=self.store.category_history(dict(category='principal'));self.assertIn('Gốc vay · Anh',[r['label'] for r in h['rows']]);self.assertFalse(any('Khoản ' in r['label'] for r in h['rows']))
        self.act('category-object-add',category='principal',profile=loan);node=next(r for r in self.store.view()['categories']['roots'] if r['key']=='principal')
        self.assertIn('Anh',[o['name'] for o in node['objects']]);self.assertFalse(any(o['name'].startswith('Khoản ') for o in node['objects']))

    def test_sync_makes_category_and_object_screens_agree_without_touching_money_or_debts(self):
        self.act('object-quick-create',kind='LOAN',party_name='Mới',name='Khoản Mới')
        self.act('category-object-add',category='principal',profile=self.l5);self.act('category-object-add',category='principal',profile=self.l10);self.act('category-object-add',category='principal',profile=self.pid('Khoản Mới'))
        iss=self.store.view()['objects']['issues'];self.assertEqual({i['code'] for i in iss},{'LOAN_AS_MEMBER','PERSON_NOT_MEMBER'})
        rep0=self.store.report(self.store.state(),self.account);debt0=self.store.debt_register(self.store.state());roots0=[r['totals'] for r in self.store.view()['categories']['roots']]
        rows={r['name']:r['action'] for r in self.store.view()['business']['migration']};self.assertEqual(rows,{'Kết':'ADD_ONLY','Mới':'ADD_ONLY'})      # không gắn loại khi nghiệp vụ tạm dừng
        self.act('business-migrate',confirm=True);self.err('business-migrate',confirm=True)
        self.assertEqual(self.store.view()['objects']['issues'],[])
        members=lambda: sorted((o['name'],o['kind']) for r in self.store.view()['categories']['roots'] if r['key']=='principal' for o in r['objects'])
        self.assertEqual(members(),[('Kết','PERSON'),('Mới','PERSON')])
        cat_people={o['name'] for r in self.store.view()['categories']['roots'] if r['key']=='principal' for o in r['objects']};obj_people={n for n,o in self.objs().items() if any(c['category']=='principal' and not c.get('via_loan') for c in o['categories'])}
        self.assertEqual(cat_people,obj_people)                                                                                  # hai màn cùng tập người
        self.assertTrue(all(not e.get('business') for e in self.store.state()['category_objects'] if e['profile']==self.person))
        self.assertEqual(self.store.report(self.store.state(),self.account),rep0);self.assertEqual(self.store.debt_register(self.store.state()),debt0);self.assertEqual([r['totals'] for r in self.store.view()['categories']['roots']],roots0)
        self.err('category-object-remove',category='principal',profile=self.person,reason='x')                                   # còn khoản vay thuộc danh mục
        self.act('classify',ids=[self.tx('X1')['id']],parts=[dict(category='principal',profile=self.l5)])                      # vẫn phân loại được

if __name__=='__main__':unittest.main()
