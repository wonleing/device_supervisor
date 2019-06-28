# -*- coding: utf-8 -*-


import time
import uuid
import hmac
import hashlib
from base import BaseHandler, COOKIE_NAME, CONF
from app.model import User
from app.model import Session
from app.model import Passport
from app.model import CorpUser


class LoginHandler(BaseHandler):

    def post(self):
        if self.current_user:
            self.util_logout()

        username = self.get_argument('username', '')
        password = self.get_argument('password', '')
        code = self.get_argument('code', '')
        platform = self.get_argument('platform', 'true')

        if platform == 'true':
            if not CONF.getboolean('general', 'debug'):
                if not code:
                    self.finish({'code': 2, 'msg': u'验证码错误'})
                    return
                if not self.check_captcha(code):
                    self.finish({'code': 2, 'msg': u'验证码错误'})
                    return

        passport = self.session.query(Passport).filter_by(username=username).first()

        if not passport:
            self.finish({'code': 1, 'msg': u'用户名或密码错误'})
            return

        if hmac.new(passport.password[:16].encode('utf8'), password.encode('utf8'), hashlib.sha256).hexdigest() != passport.password[16:]:
            self.finish({'code': 1, 'msg': u'用户名或密码错误'})
            return

        q = self.session.query(User).filter_by(id=passport.user, status=User.STATUS_NORMAL)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'用户状态异常'})
            return

        user = q.first()
        corp = None
        if user.type not in [User.TYPE_ADMIN]:
            corp_user = self.session.query(CorpUser).filter_by(user=user.id, status=CorpUser.STATUS_NORMAL).first()
            if corp_user:
                corp = corp_user.corp

        self.util_login(user_id=passport.user, corp_id=corp)
        self.session.query(Passport).filter_by(user=passport.id).update({'login_time': time.time()},synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0, 'data': {'id': passport.user}})


class LogoutHandler(BaseHandler):
    def post(self):
        return self.get()
    def get(self):
        redirect = self.get_argument('redirect', '')

        if not self.current_user:
            if redirect: self.redirect(redirect)
            else: self.finish({'code': 0})
            return

        self.util_logout()

        if redirect: self.redirect(redirect)
        else: self.finish({'code': 0})


