# -*- coding: utf-8 -*-

import uuid
import time
from app.model import User
from app.model import Session
from app.config import CONF

COOKIE_NAME = CONF.get('general', 'cookie_name')


class UtilHandler(object):

    def util_login(self, user_id=None, corp_id=None):
        p = {
            'id': uuid.uuid4().hex,
            'user': user_id,
            'create': time.time(),
            'corp': corp_id,
        }
        self.session.query(Session).filter_by(id=p['id']).delete(synchronize_session=False)
        session = Session(**p)
        self.session.add(session)
        self.session.commit()
        self.set_secure_cookie(COOKIE_NAME, session.id, httponly=True)
        return session


    def util_logout(self):
        if not self.current_user:
            return

        self.clear_all_cookies()
        self.session.query(Session).filter_by(id=self.current_user.sid).delete(synchronize_session=False)
        self.session.commit()


    def util_get_session(self):

        if self.current_user:
            sid = self.current_user.sid
            session = self.session.query(Session).filter_by(id=sid).first()
            return session

        sid = self.get_secure_cookie(COOKIE_NAME)
        if not sid:
            return self.util_login(None)

        session = self.session.query(Session).filter_by(id=sid).first()
        if not session:
            return self.util_login(None)

        return session


    def util_wechat_login(self, user=None, user_uuid=None, session_key=None, openid=None,corp_id=None):
        p = {
            'user': user,
            'id': user_uuid,
            'create': time.time(),
            'ip': session_key + openid,
            'corp': corp_id,
        }
        self.session.query(Session).filter_by(id=p['id']).delete(synchronize_session=False)
        session = Session(**p)
        self.session.add(session)
        self.session.commit()
        self.set_secure_cookie(COOKIE_NAME, session.id, httponly=True)
        return session
