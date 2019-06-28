# -*- coding: utf-8 -*-

import uuid
import hashlib
import hmac
import base64
import time
from base import RestHandler
from app.model import User, Passport,Session
from app.model import CorpUser


class UserHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})

    def get_query(self):
        q = self.session.query(User).filter_by(status=User.STATUS_NORMAL)
        return q


    def list_filter(self, q):

        id = self.get_argument('id', '')
        if id:
            q = q.filter(User.id == id)


        name = self.get_argument('name', '')
        if name:
            q = q.filter(User.name.ilike('%' + name + '%'))

        mobile = self.get_argument('mobile', '')
        if mobile:
            q = q.filter(User.mobile.ilike('%' + mobile + '%'))

        username = self.get_argument('username', '')
        if username:
            sub_q = self.session.query(Passport.user).filter_by(username=username, type=Passport.TYPE_NORMAL)
            q = q.filter(User.id.in_(sub_q))

        return q

    def get_option_query(self):
        q = self.session.query(User.id, User.name).filter_by(status=User.STATUS_NORMAL).order_by(-User.id)
        return q

    def create(self):
        p = {
            'type': self.get_argument_enum('type', [User.TYPE_NORMAL, User.TYPE_ADMIN], User.TYPE_NORMAL),
            'name': self.get_argument('name', ''),
            'password': self.get_argument('password', ''),
            'username': self.get_argument('username', ''),
        }

        if not p['password']:
            self.finish({'code': 1, 'msg': u'密码不能为空'})
            return

        if not p['username']:
            self.finish({'code': 2, 'msg': u'用户名不能为空'})
            return

        q = self.session.query(Passport).filter_by(username=p['username'])
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'用户名已存在'})
            return

        user = User(type=p['type'], name=p['name'], create=time.time())
        self.session.add(user)
        self.session.flush()

        key = base64.urlsafe_b64encode(uuid.uuid4().hex)[:16]
        ps = key + hmac.new(key, p['password'], hashlib.sha256).hexdigest()

        passport = Passport(user=user.id, username=p['username'], password=ps, create=time.time())
        self.session.add(passport)
        self.session.commit()

        self.finish({'code': 0, 'data': user.dict()})


    def update(self):
        if not self.get_argument('user', ''):
            self.finish({'code': 1, 'msg': u'user不能为空'})
            return

        q = self.get_query().filter_by(id=self.p.user)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 2,'msg':u'无该用户'})
            return

        p = {
            'name': self.get_argument('name', ''),
            'type': self.get_argument_enum('type', [User.TYPE_ADMIN,User.TYPE_NORMAL],None),
            'avatar': self.get_argument('avatar', ''),
            'mobile': self.get_argument('mobile', ''),
            'email': self.get_argument('email', ''),
            'address': self.get_argument('address', ''),
            'position': self.get_argument('position', ''),
            'department': self.get_argument('department', ''),
            'sex': self.get_argument('sex', ''),
            'rid':self.get_argument('rid', '')
        }
        data = {}
        for k in p:
            if p[k]: data[k] = p[k]
        try:
            q.update(data,synchronize_session=False)
            self.session.commit()
            self.finish({'code': 0,'msg':u'修改成功'})
        except Exception as e:
            self.finish({'code': 3, 'msg': u'修改失败'})


    def delete(self):
        if not self.get_argument('id', None):
            self.finish({'code': 1, 'msg': u'id 不能为空'})
            return

        user = self.get_query().filter_by(id=self.p.id).first()
        self.session.query(Passport).filter_by(user=user.id).delete()
        self.session.query(CorpUser).filter_by(user=user.id).delete()
        self.get_query().filter_by(id=user.id).update({'status': User.STATUS_DELETE},
                                                       synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})


    def reset(self):
        password = self.get_argument('password', '')
        id = self.get_argument('id', '')

        if not password:
            self.finish({'code': 1, 'msg': u'密码不能为空'})
            return

        if not id:
            self.finish({'code': 2, 'msg': u'缺少id'})
            return

        key = base64.urlsafe_b64encode(uuid.uuid4().hex)[:16]
        ps = key + hmac.new(key, password, hashlib.sha256).hexdigest()
        self.session.query(Passport).filter_by(user=id).update({'password': ps}, synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})

    def user_corp(self):
        user = self.get_argument('user','')

        if not user:
            self.finish({'code': -1, 'msg': u'user不能为空'})
            return

        user_corp = self.session.query(CorpUser).filter_by(user =user)
        if not self.session.query(user_corp.exists()).scalar():
            self.finish({'code': -2, 'msg': u'无所属企业'})
            return

        q = user_corp.first()
        corp = q.corp_obj

        data = dict(
            id = corp.id,
            name = corp.name,
            contacts = corp.contacts
        )
        self.finish({'code':0,'data':data})
