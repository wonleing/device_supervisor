# -*- coding: utf-8 -*-
 
import base64
import hmac
import hashlib
import uuid
import time

from base import RestHandler
from app.model import User
from app.model import Passport,Session
from app.model.corp import CorpUser,Corp
from app.config import CONF

COOKIE_NAME = CONF.get('general', 'cookie_name')


class MeHandler(RestHandler):
    u'当前用户'

    def permission(self):
        u'登录用户'

        if not self.current_user:
            self.send_error(403)

    def get_query(self):
        return self.session.query(User).filter_by(id=self.current_user.id)

    def get_option_query(self):
        return self.session.query(User.id, User.name).filter_by(id=self.current_user.id)

    def read(self):
        q = self.get_query()
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 2, 'msg': '指定 id 的内容不存在'})
            return

        obj = q.first()
        self.finish({'code': 0, 'data': obj.dict()})

    def update_password(self):
        old_password = self.get_argument('old_password', '')
        new_password = self.get_argument('new_password', '')

        if not old_password:
            self.finish({'code': 3, 'msg': u'旧密码不能为空'})
            return

        if not new_password:
            self.finish({'code': 4, 'msg': u'新密码不能为空'})
            return

        passport = self.session.query(Passport).filter_by(user=self.current_user.id, type=Passport.TYPE_NORMAL).first()
        if not passport:
            self.finish({'code': 1, 'msg': u'当前用户还没有普通账号'})
            return

        if hmac.new(passport.password[:16].encode('utf8'), old_password.encode('utf8'), hashlib.sha256).hexdigest() != passport.password[16:]:
            self.finish({'code': 2, 'msg': u'旧密码错误'})
            return

        key = base64.urlsafe_b64encode(uuid.uuid4().hex)[:16]
        ps = key + hmac.new(key, new_password, hashlib.sha256).hexdigest()
        self.session.query(Passport).filter_by(id=passport.id).update({'password': ps}, synchronize_session=False)
        self.session.commit()
        self.util_logout()
        self.finish({'code': 0, 'msg': u'修改密码成功, 需要重新登录'})


    def update(self):
        userid = self.current_user['id']
        name = self.get_argument('name',None)
        avatar = self.get_argument('avatar', None)
        sex = self.get_argument('sex', None)
        corp_mobile = self.get_argument('mobile', None)
        address = self.get_argument('address', None)
        department = self.get_argument('department', None)
        position = self.get_argument('position', None)
        rid = self.get_argument('rid', None)
        createtime = time.time()

        p = {
            'name' : name,
            'avatar': avatar,
            'sex': sex,
            'mobile': corp_mobile,
            'address': address,
            'department': department,
            'position': position,
            'create': createtime,
            'rid':rid
        }
        #只更新要修改的内容
        dict = {}
        for k in p:
            if p[k]: dict[k] = p[k]

        try:
            self.session.query(User).filter_by(id = userid).update(dict)
            self.session.commit()
            self.finish({'code': 0, 'success': True})
        except Exception as e:
            self.finish({'code': 1, 'fail': '{}'.format(e)})

    def query(self):
        userid = self.current_user['id']
        try:
            data = self.session.query(User).filter_by(id = userid).first()
            data = data.dict()
            corp_id = self.session.query(CorpUser.corp).filter_by(user=data['id']).first()
            if corp_id:
                corp = self.session.query(Corp.name).filter_by(id=corp_id[0]).first()
                data['corp'] = corp[0]
                self.finish({'code': 0, 'data': data})
            else:
                data['corp'] = ''
                self.finish({'code': 0, 'data': data })
        except Exception as e:
            self.finish({'code': 1, 'fail': '{}'.format(e)})

    def mobile_bind(self):
        mobile = self.get_argument('mobile', '')
        code = self.get_argument('code', '')


        if not mobile:
            self.finish({'code': 2, 'msg': u'手机号不能为空'})

        if not code:
            self.finish({'code': 3, 'msg': u'验证码不能为空'})

        mob = self.session.query(User.id).filter_by(mobile=mobile).first()
        if mob:
            self.finish({'code': 4, 'msg': u'手机号已绑定'})
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

        if session.code != code and session.code_mobile != mobile:
            ok = False

        session.code = ''
        session.code_create = 0
        self.session.add(session)
        self.session.commit()

        if ok:
            self.session.query(User.mobile).filter_by(id=self.current_user.id).update({"mobile":mobile},synchronize_session=False)
            self.finish({'code': 0,'msg':u'绑定成功'})
        else:
            self.finish({'code': 1, 'msg': u'验证码错误'})

    def last_login_time(self):
        id = self.current_user.id
        last_login_time = self.session.query(Passport.login_time).filter_by(user=id).first()

        self.session.query(Passport).filter_by(user=id).update({'login_time':time.time()})
        self.finish({'code': 0, 'data': {'last_login_time':last_login_time}})

    def create(self):
        p = {
            'type': User.TYPE_NORMAL,
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

