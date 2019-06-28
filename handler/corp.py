# -*- coding: utf-8 -*-

import base64
import time
import hashlib
import uuid
import hmac
from base import RestHandler
from app.model import User, Corp, CorpUser, Passport, CorpUser, CorpDevice,Device


class MyCorpHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        corp = self.get_current_session().corp
        if not corp:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        q = self.session.query(CorpUser).filter_by(corp=corp,
                                                   user=self.current_user.id,
                                                   role=CorpUser.ROLE_ADMIN)

        if not self.session.query(q.exists()).scalar():
            self.finish({'code': -1, 'msg': u'只有管理员才权限'})
            return

    def get_query(self):
        corp = self.get_current_session().corp
        q = self.session.query(Corp).filter_by(status=Corp.STATUS_NORMAL, id=corp)
        return q

    def read(self):
        q = self.get_query()
        obj = q.first()
        self.finish({'code': 0, 'data': obj.dict()})

    def update(self):
        p = {
            'name': self.get_argument('name', ''),
            'contacts': self.get_argument('contacts', ''),
            'tel': self.get_argument('tel', ''),
        }
        data = {}
        for k in p:
            if p[k]: data[k] = p[k]

        if not data:
            self.finish({'code': 1, 'msg': 'input canot be null'})
            return

        self.get_query().update(data)
        self.session.commit()
        self.finish({'code': 0})



class CorpHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})

    def add_device(self):
        device = self.session.query(Device)
        corp = self.session.query(Corp).filter_by(name = '北京思科德').first()
        for i in device:
            q = self.session.query(CorpDevice).filter(CorpDevice.corp == corp.id,CorpDevice.device == i.id)
            if not self.session.query(q.exists()).scalar():
                self.session.add(CorpDevice(corp=corp.id, device=i.id, role='1111'))
                self.session.commit()
        self.finish({'code':0})

    def delete_device(self):
        device = self.session.query(Device)
        corp = self.session.query(Corp).filter_by(name = '北京思科德').first()
        for i in device:
            if i.status == "delete":
                q = self.session.query(CorpDevice).filter(CorpDevice.corp == corp.id,CorpDevice.device == i.id).first()
                self.session.query(CorpDevice).filter_by(id = q.id).delete()
                self.session.commit()
        self.finish({'code':0})


    def get_query(self):
        q = self.session.query(Corp).filter_by(status=Corp.STATUS_NORMAL)
        return q

    def get_option_query(self):
        query = self.get_argument('q', '')
        q = self.session.query(Corp.id, Corp.name).filter_by(status=Corp.STATUS_NORMAL)
        if query:
            q = q.filter(Corp.name.ilike('%' + query + '%'))
        q = q.order_by(-Corp.id)
        return q

    def list_filter(self, q):

        id = self.get_argument('id', '')
        if id:
            q = q.filter(Corp.id == id)


        name = self.get_argument('name', '')
        if name:
            q = q.filter(Corp.name.ilike('%' + name + '%'))

        return q

    def create(self):
        p = {
            'name': self.get_argument('name', ''),
            'username': self.get_argument('username', ''),
            'password': self.get_argument('password', ''),
            'contacts': self.get_argument('contacts', ''),
            'tel': self.get_argument('tel', ''),
        }

        if not p['name']:
            self.finish({'code': 1, 'msg': u'名字不能为空'})
            return

        if not p['username']:
            self.finish({'code': 2, 'msg': u'用户名不能为空'})
            return

        if not p['password']:
            self.finish({'code': 3, 'msg': u'密码不能为空'})
            return

        q = self.session.query(Passport).filter_by(username=p['username'])
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 4, 'msg': u'此用户名已存在'})
            return

        name = self.session.query(Corp.name).filter_by(name=p['name'])
        if self.session.query(name.exists()).scalar():
            self.finish({'code': 5, 'msg': u'此企业名已存在'})
            return

        user = User(name=p['username'], create=time.time())
        self.session.add(user)
        self.session.flush()

        key = base64.urlsafe_b64encode(uuid.uuid4().hex)[:16]
        ps = key + hmac.new(key, p['password'], hashlib.sha256).hexdigest()
        passport = Passport(user=user.id, username=p['username'], password=ps, create=time.time())
        self.session.add(passport)
        self.session.flush()

        corp = Corp(name=p['name'], create=time.time(), contacts=p['contacts'], tel=p['tel'])
        self.session.add(corp)
        self.session.flush()

        self.session.add(CorpUser(corp=corp.id, user=user.id, role=CorpUser.ROLE_ADMIN))
        self.session.commit()
        self.finish({'code': 0, 'data': corp.dict()})


    def delete(self):
        if not self.get_argument('id', ''):
            self.finish({'code': 1, 'msg': u'id不能为空'})
            return

        self.get_query().filter_by(id=self.p.id).update({'status': Corp.STATUS_DELETE},
                                                         synchronize_session=False)
        self.session.query(CorpUser).filter_by(corp=self.p.id).delete()
        self.session.query(CorpDevice).filter_by(corp=self.p.id).delete()
        self.session.commit()
        self.finish({'code': 0})


    def update(self):
        if not self.get_argument('id', ''):
            self.finish({'code': 1, 'msg': u'id不能为空'})
            return

        p = {
            'name': self.get_argument('name', ''),
            'contacts': self.get_argument('contacts', ''),
            'tel': self.get_argument('tel', ''),
        }
        data = {}
        for k in p:
            if p[k]: data[k] = p[k]

        self.get_query().filter_by(id=self.p.id).update(data)
        self.session.commit()
        self.finish({'code': 0})


