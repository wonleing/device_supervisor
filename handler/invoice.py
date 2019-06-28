#-*-coding:utf-8-*-
from base import RestHandler
import time
from app.model.personal import Invoice
from app.model.user import User
from app.model.corp import CorpUser,Corp

class MyInvoiceHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return
        corp = self.get_current_session().corp
        if not corp:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return
        action= self.request.uri.split('/')
        if action[-1] in ['create','update']:
            q = self.session.query(CorpUser).filter_by(corp=corp,
                                                   user=self.current_user.id,
                                                   role=CorpUser.ROLE_ADMIN)
            if not self.session.query(q.exists()).scalar():
                 self.finish({'code': -1, 'msg': u'只有管理员才权限'})
                 return

    def get_query(self):
        q = self.session.query(Invoice)
        return q

    def create(self):
        id = self.current_user.id
        corp_id = self.session.query(CorpUser.corp).filter_by(user=id).first()
        corp = self.session.query(Corp.name).filter_by(id = corp_id[0]).first()

        tax_number = self.get_argument('taxnumber',None)
        register_address = self.get_argument('address',None)
        telephone = self.get_argument('telephone',None)
        bank_name = self.get_argument('bankname',None)
        bank_number = self.get_argument('banknumber',None)
        createtime = time.time()

        p = {
            'taxnumber' : tax_number,
            'register_address' : register_address,
            'telephone' : telephone,
            'bankname' : bank_name,
            'banknumber' : bank_number,
            'time' : createtime,
        }

        p['corpname'] = corp[0]

        q = self.session.query(Invoice).filter_by(corpname = p['corpname']).first()
        if q:
            self.finish({'code':1,'msg':u'该公司已经创建了发票'})
            return

        if not tax_number:
            self.finish({'code':2,'msg':'the tax_number canot be null'})
            return

        if not register_address:
            self.finish({'code': 3,'msg':'the register_address canot be null'})
            return

        if not telephone:
            self.finish({'code': 4, 'msg':'the telephone canot be null'})
            return

        if not bank_name:
            self.finish({'code': 5, 'msg':'the bank_name canot be null'})
            return

        if not bank_number:
            self.finish({'code': 6, 'msg':'the bank_number canot be null'})
            return
        try:
            invoice = Invoice(**p)
            self.session.add(invoice)
            self.session.commit()
            self.finish({'code': 0, 'Sucess': True})
        except:
            self.finish({'code': 7, 'err': 'create failed'})

    def query(self):
        userid = self.current_user['id']
        corp_id = self.session.query(CorpUser.corp).filter_by(user=userid).first()
        corp = self.session.query(Corp.name).filter_by(id = corp_id[0]).first()
        message = self.session.query(Invoice).filter_by(corpname = corp[0]).first()
        if message:
            self.finish({'code':0,'data':message.dict()})
        else:
            self.finish({'code':1,'data':u'该公司未开通发票业务'})


    def update(self):
        id = self.current_user.id
        corp_id = self.session.query(CorpUser.corp).filter_by(user=id).first()
        corp = self.session.query(Corp.name).filter_by(id=corp_id[0]).first()
        p = {
            'taxnumber': self.get_argument('taxnumber',None),
            'register_address': self.get_argument('address',None),
            'telephone': self.get_argument('telephone',None),
            'bankname': self.get_argument('bankname',None),
            'banknumber': self.get_argument('banknumber',None),
            'time': self.get_argument('time',None),
        }
        data = {}
        for k in p:
            if p[k] : data[k] = p[k]
        if not data:
            self.finish({'code':2,'msg':u'请输入至少一个更新参数'})
            return
        try :
            self.session.query(Invoice).filter_by(corpname = corp[0]).update(data)
            self.finish({'code': 0, 'Sucess': True})
        except Exception as e:
            self.finish({'code': 1, 'err': '{}'.format(e)})

class InvoiceHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})

    def get_query(self):
        q = self.session.query(Invoice)
        return q

    def list_filter(self,q):
        q = q.order_by(Invoice.time.desc())
        id = self.get_argument('id','')
        if id:
            sub_id = [x.strip() for x in filter(None, id.split(','))]
            data = self.session.query(Corp.name).filter(Corp.id.in_(sub_id)).all()
            corp_name = [o[0] for o in data]
            q = q.filter(Invoice.corpname.in_(corp_name))

        name = self.get_argument('name','')
        if name:
            q = q.filter(Invoice.corpname.ilike('%' + name + '%'))

        taxnumber = self.get_argument('taxnumber','')
        if taxnumber:
            q = q.filter(Invoice.taxnumber == taxnumber)

        register_address = self.get_argument('register_address','')
        if register_address:
            q = q.filter(Invoice.register_address == register_address)

        telephone = self.get_argument('telephone','')
        if telephone:
            q = q.filter(Invoice.telephone == telephone)

        banknumber = self.get_argument('banknumber','')
        if banknumber:
            q = q.filter(Invoice.banknumber == banknumber)

        return q



    def delete(self):
        id = self.get_argument('id', None)
        if not id:
            self.finish({'code':1,'msg':'the id is missing'})
            return
        try:
            self.session.query(Invoice).filter_by(id=id).delete()
            self.session.commit()
            self.finish({'code': 0, 'success': True})
        except Exception as e:
            self.finish({'code': 2, 'data': u'数据delete失败'})

    def update(self):
       id = self.get_argument('id','')
       if not id:
           self.finish({'code': 1, 'msg': 'the id is missing!'})
           return

       p = {
            'taxnumber': self.get_argument('taxnumber', None),
            'register_address': self.get_argument('address', None),
            'telephone': self.get_argument('telephone', None),
            'bankname': self.get_argument('bankname', None),
            'banknumber': self.get_argument('banknumber', None),
            'time': self.get_argument('time',None)
        }
       data = {}
       for k in p:
           if p[k]: data[k] = p[k]
       if not data:
           self.finish({'code':2,'msg':u'请至少输入一个更新内容'})
           return

       try:
           self.session.query(Invoice).filter_by(id=id).update(data)
           self.finish({'code': 0, 'Sucess': True})
       except Exception as e:
           self.finish({'code': 1, 'err': '{}'.format(e)})





