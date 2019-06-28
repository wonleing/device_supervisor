# -*- coding: utf-8 -*-
## RIZHI
import base64
import time
import hashlib
import uuid
import hmac
from base import RestHandler
from app.model import User, Corp, CorpUser, ActionLog


class MyActionLogHandler(RestHandler):
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
        sub_q = self.session.query(CorpUser.user).filter_by(corp=corp)
        q = self.session.query(ActionLog).filter(ActionLog.user.in_(sub_q))
        return q



class ActionLogHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})


    def get_query(self):
        q = self.session.query(ActionLog)

        if self.get_argument('corp', ''):
            sub_q = self.session.query(CorpUser.user).filter_by(corp=self.p.corp)
            q = q.filter(ActionLog.user.in_(sub_q))

        return q


