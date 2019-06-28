# -*- coding: utf-8 -*-
import re
import random
import time
import uuid

from base import RestHandler
from app.model.user import User
from app.model.session import Session
from app.service.mail import MailService

from app.config import CONF

COOKIE_NAME = CONF.get('general', 'cookie_name')


class MailHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})

    def gene_text(self):
        number = 6
        source = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        return ''.join(random.sample(source, number))

    def sendmail(self,receivers,content,subject=''):
        if self.request.files.get('file',None):
            files = self.request.files['file']
            files = files[0]
        else:
            files = None
        str = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
        if not re.match(str, receivers):
            self.finish({'code': 1, 'data': u'邮箱格式错误'})
        try:
            test = MailService()
            # res = test.send(content,receiver,file,subject).sync()
            res = test.send(receivers, content, files, subject).sync()
            return res
        except:
            return {'code':1,'msg':'send failed'}


    def send_email_code(self):
        receivers =self.get_argument('email','')
        subject = self.get_argument('subject','')
        if not receivers:
            self.finish({'code': 1, 'msg': u'邮箱不能为空'})
            return

        code = self.gene_text()
        content = u'您的验证码为：'+code

        res = self.sendmail(receivers,content,subject)

        if res['code']==0:
            session = self.util_get_session()
            self.session.query(Session).filter_by(id=session.id) \
                .update({'code': code, 'code_create': time.time(), 'email': receivers},
                        synchronize_session=False)
            self.session.commit()
            self.finish({'code': 0,'msg':'send sucess'})
        else:
            self.finish({'code': 2, 'msg': res})


    def send_email_msg(self):
        content = self.get_argument('content', '')
        receivers = self.get_argument('email', '')
        subject = self.get_argument('subject','')

        if not content:
            self.finish({'code':1,'msg':u'发送内容不能为空'})

        if not receivers:
            self.finish({'code':2,'msg':u'请填写邮箱'})
        try:
            res = self.sendmail(receivers,content,subject)
            self.finish({'code':0,'msg':'send sucess'})
        except:
            self.finish({'code':3,'msg':'send failed'})

    def email_bind(self):
        code = self.get_argument('code', '')
        email = self.get_argument('email','')

        if not code:
            self.finish({'code': 1, 'msg': u'验证码不能为空'})
            return

        if not email:
            self.finish({'code': 2, 'msg': u'邮箱不能为空'})
            return

        user = self.session.query(User.id).filter_by(email=email).first()
        if user:
            self.finish({'code': 3, 'msg': u'邮箱已绑定'})
            return

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

        if session.code != code and session.email != email:
            ok = False

        session.code = ''
        session.code_create = 0
        self.session.add(session)
        self.session.commit()
        print(email)

        if ok:
            self.session.query(User.email).filter_by(id=self.current_user.id).update({"email": email},
                                                                                      synchronize_session=False)
            self.finish({'code': 0, 'msg': u'绑定成功'})
        else:
            self.finish({'code': 1, 'msg': u'验证码错误或者连接超时'})

    def email_verify(self):
        code = self.get_argument('code','')
        email = self.get_argument('email','')

        if not code:
            self.finish({'code': 1, 'msg': u'验证码不能为空'})
            return

        if not email:
            self.finish({'code': 2, 'msg': u'邮箱不能为空'})
            return
        sid = self.get_secure_cookie(COOKIE_NAME)
        if not sid:
            return False

        try:
            session = self.session.query(Session).filter_by(id=sid).first()
        except:
            return False

        user = self.session.query(User).filter(User.email == email,User.id == session.user).first()
        if not user:
            self.finish({'code':3,'msg':u'该邮箱未绑定'})
            return

        now = int(time.time())
        ok = True

        if not session.code:
            ok = False

        if abs(session.code_create - now) > 60 * 5:
            ok = False

        if session.code != code and session.email != email:
            ok = False

        session.code = ''
        session.code_create = 0
        self.session.add(session)
        self.session.commit()
        if ok:
            self.finish({'code':0,'msg':u'验证成功'})
        else:
            self.finish({'code':4,'msg':u'验证失败'})









































