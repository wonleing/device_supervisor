# -*- coding: utf-8 -*-

import uuid
import hashlib
import hmac
import base64
import time
from base import RestHandler
from app.model import User, Session, System


class SystemHandler(RestHandler):
    '当前会话状态'

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

    def get_query(self):
        q = self.session.query(System)
        return q

    def delete(self):
        self.send_error(404)

    def create(self):
        self.send_error(404)

    def read(self):
        name = self.get_argument('name', '')
        if not id:
            self.finish({'code': 1, 'msg': 'name 不能为空'})
            return

        if name not in System.ALL_NAME:
            self.finish({'code': 2, 'msg': u'错误的 name 值'})
            return

        q = self.get_query().filter_by(name=name)
        obj = q.first()
        self.finish({'code': 0, 'data': obj.dict()})

    def update(self):
        name = self.get_argument('name', '')
        value = self.get_argument('value', None)

        if value is None:
            self.finish({'code': 1, 'msg': u'没有传递 value 值'})
            return

        if not name:
            self.finish({'code': 2, 'msg': u'没有传递 name 值'})
            return

        if name not in System.ALL_NAME:
            self.finish({'code': 2, 'msg': u'错误的 name 值'})
            return

        self.get_query().filter_by(name=name).update({'value': value, 'update': time.time()},
                                                     synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})





