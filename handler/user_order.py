# -*- coding: utf-8 -*-

from base import RestHandler
from app.model import TakeOrder, CorpUser,User,DeliverOrder
import time



class MyTakeOrderHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        action = self.request.uri.split('/')
        if action[-1] in ['create','delete']:
            corp = self.get_current_session().corp
            q = self.session.query(CorpUser).filter_by(corp=corp,
                                                       user=self.current_user.id,
                                                       role=CorpUser.ROLE_ADMIN)
            if not self.session.query(q.exists()).scalar():
                self.finish({'code': -2, 'msg': u'企业管理员才有权限'})
                return

    def get_query(self):
        corp = self.get_current_session().corp
        q = self.session.query(CorpUser).filter_by(corp=corp,
                                                   user=self.current_user.id,
                                                   role=CorpUser.ROLE_ADMIN)
        if self.session.query(q.exists()).scalar():
            q = self.session.query(TakeOrder).filter_by(user=self.current_user.id)
        else:
            username = self.session.query(User.name).filter_by(id = self.current_user.id)
            q = self.session.query(TakeOrder).filter_by(contacter=username[0])
        q = q.filter(TakeOrder.status.in_(['normal','abnormal','treated']))
        return q

    def list_filter(self, q):
        q = q.order_by(TakeOrder.create.desc())

        status = self.get_argument('status', '')
        if status:
            q = q.filter(TakeOrder.status == status)

            # 支持 id 过滤
        id = self.get_argument('id', '')
        if id:
            q = q.filter(TakeOrder.id == id)

        mode = self.get_argument('mode', '')
        if mode:
            q = q.filter(TakeOrder.mode == mode)

        supplier = self.get_argument('supplier', '')
        if supplier:
            q = q.filter(TakeOrder.supplier == supplier)

        source = self.get_argument('source', '')
        if source:
            q = q.filter(TakeOrder.source == source)

        serial_number = self.get_argument('serial_number', '')
        if serial_number:
            q = q.filter(TakeOrder.serial_number == serial_number)

        contacts = self.get_argument('contacts', '')
        if contacts:
            q = q.filter(TakeOrder.contacts == contacts)

        contacter = self.get_argument('contacter', '')
        if contacter:
            q = q.filter(TakeOrder.contacter == contacter)
        return q



    def create(self):

        p = {
            'user':self.current_user.id,
            'type': self.get_argument('type', 'take'),
            'contacts':self.get_argument('contacts', ''),
            'contacter': self.get_argument('contacter', ''),
            'serial_number': self.get_argument('serial_number', ''),
            'remark': self.get_argument('remark', ''),
            'mode': self.get_argument('mode', ''),
            'supplier': self.get_argument('supplier', ''),
            'source': self.get_argument('source', ''),
            'arrive_t': self.get_argument('arrive_t', ''),
            'tractor': self.get_argument('tractor', ''),
            'trailer': self.get_argument('trailer', ''),
            'location': self.get_argument('location', ''),
            'medium': self.get_argument('medium', ''),
            'create': int(time.time())
        }

        if not self.get_argument('contacts', ''):
            self.finish({'code': 1, 'msg': u'需要指定contacts'})
            return

        if not self.get_argument('contacter', ''):
            self.finish({'code': 2, 'msg': u'需要指定contacter'})
            return

        if not self.get_argument('serial_number', ''):
            self.finish({'code': 3, 'msg': u'需要指定serial_number'})
            return

        if not self.get_argument('mode', ''):
            self.finish({'code': 4, 'msg': u'需要指定mode'})
            return

        if not self.get_argument('supplier', ''):
            self.finish({'code': 5, 'msg': u'需要指定supplier'})
            return

        if not self.get_argument('source', ''):
            self.finish({'code': 6, 'msg': u'需要指定source'})
            return

        if not self.get_argument('arrive_t', ''):
            self.finish({'code': 7, 'msg': u'需要指定arrive_t'})
            return

        if not self.get_argument('tractor', ''):
            self.finish({'code': 8, 'msg': u'需要指定tractor'})
            return

        if not self.get_argument('trailer', ''):
            self.finish({'code': 9, 'msg': u'需要指定trailer'})
            return

        if not self.get_argument('medium', ''):
            self.finish({'code': 10, 'msg': u'需要指定medium'})
            return

        q = self.session.query(TakeOrder).filter_by(user=p['user'], serial_number=p['serial_number'])
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 11, 'msg': u'提货单号已创建'})
            return
        else:
            self.session.add(TakeOrder(**p))
            self.session.commit()
            self.finish({'code': 0})

    def update(self):
        id = self.get_argument('id', '')
        if not id:
            self.finish({'code': 1, 'msg': 'the id is missing'})
            return
        q = self.get_query().filter(TakeOrder.id == id)
        obj = q.first()
        map = obj.dict()

        data = {}
        for k in map.keys():
            if (k in self.p) and (k not in ['id', 'serial_number', 'create']):
                data[k] = self.p[k]

        updater = self.session.query(User.name).filter_by(id = self.current_user.id).first()
        data['updater'] = updater[0]
        data['update'] = int(time.time())
        q.update(data, synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})

    def delete(self):
        '删除附件'
        id = self.get_argument('id', '')
        self.session.query(TakeOrder).filter_by(id = id).update({'status':'delete'})
        self.session.commit()
        self.finish({'code': 0, 'data': u'ok'})



class MyDeliverOrderHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        action = self.request.uri.split('/')
        if action[-1] in ['create','delete']:
            corp = self.get_current_session().corp
            q = self.session.query(CorpUser).filter_by(corp=corp,
                                                       user=self.current_user.id,
                                                       role=CorpUser.ROLE_ADMIN)
            if not self.session.query(q.exists()).scalar():
                self.finish({'code': -2, 'msg': u'企业管理员才有权限'})
                return

    def get_query(self):
        corp = self.get_current_session().corp
        q = self.session.query(CorpUser).filter_by(corp=corp,
                                                   user=self.current_user.id,
                                                   role=CorpUser.ROLE_ADMIN)
        if self.session.query(q.exists()).scalar():
            q = self.session.query(DeliverOrder).filter_by(user=self.current_user.id)
        else:
            username = self.session.query(User.name).filter_by(id = self.current_user.id)
            q = self.session.query(DeliverOrder).filter_by(contacter=username[0])
        q = q.filter(DeliverOrder.status.in_(['unload','dispatch','backspace','abnormal']))
        return q

    def list_filter(self, q):
        q = q.order_by(DeliverOrder.create.desc())

        status = self.get_argument('status', '')
        if status:
            q = q.filter(DeliverOrder.status == status)

            # 支持 id 过滤
        id = self.get_argument('id', '')
        if id:
            q = q.filter(DeliverOrder.id == id)

        mode = self.get_argument('mode', '')
        if mode:
            q = q.filter(DeliverOrder.mode == mode)

        station = self.get_argument('station', '')
        if station:
            q = q.filter(DeliverOrder.station == station)

        take_order = self.get_argument('take_order', '')
        if take_order:
            q = q.filter(DeliverOrder.take_order == take_order)

        serial_number = self.get_argument('serial_number', '')
        if serial_number:
            q = q.filter(DeliverOrder.serial_number == serial_number)

        customer = self.get_argument('customer', '')
        if customer:
            q = q.filter(DeliverOrder.customer == customer)

        contacter = self.get_argument('contacter', '')
        if contacter:
            q = q.filter(DeliverOrder.contacter == contacter)

        location = self.get_argument('location', '')
        if location:
            q = q.filter(DeliverOrder.location == location)

        tractor = self.get_argument('tractor', '')
        if tractor:
            q = q.filter(DeliverOrder.tractor == tractor)

        trailer = self.get_argument('trailer', '')
        if trailer:
            q = q.filter(DeliverOrder.trailer == trailer)
        return q



    def create(self):

        p = {
            'user':self.current_user.id,
            'type': self.get_argument('type', 'deliver'),
            'contacts':self.get_argument('contacts', ''),
            'contacter': self.get_argument('contacter', ''),
            'serial_number': self.get_argument('serial_number', ''),
            'remark': self.get_argument('remark', ''),
            'mode': self.get_argument('mode', ''),
            'station': self.get_argument('station', ''),
            'customer': self.get_argument('customer', ''),
            'take_order': self.get_argument('take_order', ''),
            'arrive_t': self.get_argument('arrive_t', ''),
            'tractor': self.get_argument('tractor', ''),
            'trailer': self.get_argument('trailer', ''),
            'location': self.get_argument('location', ''),
            'create': int(time.time())
        }

        if not self.get_argument('contacts', ''):
            self.finish({'code': 1, 'msg': u'需要指定contacts'})
            return

        if not self.get_argument('contacter', ''):
            self.finish({'code': 2, 'msg': u'需要指定contacter'})
            return

        if not self.get_argument('serial_number', ''):
            self.finish({'code': 3, 'msg': u'需要指定serial_number'})
            return

        if not self.get_argument('mode', ''):
            self.finish({'code': 4, 'msg': u'需要指定mode'})
            return

        if not self.get_argument('station', ''):
            self.finish({'code': 5, 'msg': u'需要指定station'})
            return

        if not self.get_argument('customer', ''):
            self.finish({'code': 6, 'msg': u'需要指定customer'})
            return

        if not self.get_argument('arrive_t', ''):
            self.finish({'code': 7, 'msg': u'需要指定arrive_t'})
            return

        if not self.get_argument('tractor', ''):
            self.finish({'code': 8, 'msg': u'需要指定tractor'})
            return

        if not self.get_argument('trailer', ''):
            self.finish({'code': 9, 'msg': u'需要指定trailer'})
            return

        if not self.get_argument('take_order', ''):
            self.finish({'code': 10, 'msg': u'需要指定take_order'})
            return

        q = self.session.query(DeliverOrder).filter_by(user=p['user'], serial_number=p['serial_number'])
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 11, 'msg': u'运货单号已创建'})
            return

        else:
            q = self.session.query(TakeOrder).filter_by(id=p['take_order']).first()
            p['press_after'] = q.press_after
            p['temp_after'] = q.temp_after
            p['after'] = q.after
            self.session.add(DeliverOrder(**p))
            self.session.commit()
            self.finish({'code': 0})

    def update(self):
        id = self.get_argument('id', '')
        if not id:
            self.finish({'code': 1, 'msg': 'the id is missing'})
            return
        q = self.get_query().filter(DeliverOrder.id == id)
        obj = q.first()
        map = obj.dict()

        data = {}
        for k in map.keys():
            if (k in self.p) and (k not in ['id', 'serial_number', 'create']):
                data[k] = self.p[k]

        if 'leave' in data.keys():
            data['add'] = float(map['after'])-float(data['leave'])

        updater = self.session.query(User.name).filter_by(id = self.current_user.id).first()
        data['updater'] = updater[0]
        data['update'] = int(time.time())
        q.update(data, synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})

    def delete(self):
        '删除附件'
        id = self.get_argument('id', '')
        self.session.query(DeliverOrder).filter_by(id = id).update({'status':'delete'})
        self.session.commit()
        self.finish({'code': 0, 'data': u'ok'})



