# -*- coding: utf-8 -*-

import uuid
import hashlib
import hmac
import base64
import time
from base import RestHandler
from app.model import User, Session


class SessionHandler(RestHandler):
    '当前会话状态'

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

    def get_query(self):
        q = self.session.query(Session).filter_by(id=self.current_user.sid)
        return q

    def list_defer(self):
        return ['code', 'code_create', 'code_mobile', 'id']

    def read(self):
        q = self.get_query()
        obj = q.first()
        self.finish({'code': 0, 'data': obj.dict(defer=self.list_defer())})


