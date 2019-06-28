# -*- coding: utf-8 -*-

import time
import random
import uuid
from base import BaseHandler,RestHandler
from app.service.luosimao import LuoSiMao
from app.model import Session,User
from app.config import CONF

COOKIE_NAME = CONF.get('general', 'cookie_name')



class SendMobileCode(BaseHandler):

    def gene_text(self):
        number = 6
        source = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        return ''.join(random.sample(source, number))

    def post(self):
        mobile = self.get_argument('mobile','')

        if not mobile:
            self.finish({'code': 1, 'msg': u'手机号不能为空'})
            return

        code = self.gene_text()
        data = LuoSiMao().send(mobile,code).sync()

        if data['msg'] == 'ok':
            session = self.util_get_session()
            self.session.query(Session).filter_by(id=session.id) \
                .update({'code': code, 'code_create': time.time(),'code_mobile':mobile},
                        synchronize_session=False)
            self.session.commit()
            self.finish({'code': 0})
        else:
            self.finish({'code':3,'data':data})


class MobileVerify(RestHandler):
    def permission(self):
        pass

    def mobile_verify(self):
        code = self.get_argument('code','')
        mobile = self.get_argument('mobile','')
        sid = self.get_secure_cookie(COOKIE_NAME)
        if not sid:
            return False

        try:
            session = self.session.query(Session).filter_by(id=sid).first()
        except:
            return False

        now = int(time.time())
        ok = True

        if not session.code:
            ok = False

        if abs(session.code_create - now) > 60 * 5:
            ok = False

        if session.code != code and session.code_mobile != mobile:
            ok = False

        session.code = ''
        session.code_create = 0
        self.session.add(session)
        self.session.commit()
        if not ok:
            self.finish({'code':1,'msg':'Verification failure !'})
        else:
            self.finish({'code':0,'msg':'Verification success !'})
