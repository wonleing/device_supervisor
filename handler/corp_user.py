# -*- coding: utf-8 -*-

import base64
import time
import hashlib
import uuid
import hmac
from base import RestHandler
from app.model import CorpUser, User, Passport, Corp


class MyCorpUserHandler(RestHandler):

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

    def list_filter(self, q):
        if self.p.get('user', ''):
            q = q.filter_by(user=self.p.user)

        if self.p.get('status', ''):
            q = q.filter_by(status=self.p.status)

        return q


    def get_query(self):
        q = self.session.query(CorpUser).filter_by(corp=self.get_current_session().corp)
        return q

    def get_option_query(self):
        q = self.session.query(CorpUser.id, User.name).join(User, CorpUser.user == User.id)\
                .filter(CorpUser.corp == self.get_current_session().corp)
        return q


    def create(self):
        p = {
            'name': self.get_argument('name', ''),
            'password': self.get_argument('password', ''),
            'username': self.get_argument('username', ''),
            'role': self.get_argument('role', CorpUser.ROLE_NORMAL),
            'mobile': self.get_argument('mobile', ''),
            'address': self.get_argument('address', ''),
        }

        if p['role'] not in CorpUser.ROLE_MAP:
            self.finish({'code': 4, 'msg': u'角色错误'})
            return

        if not p['password']:
            self.finish({'code': 1, 'msg': u'密码不能为空'})
            return

        if not p['username']:
            self.finish({'code': 2, 'msg': u'用户名不能为空'})
            return

        q = self.session.query(Passport).filter_by(username=p['username'], type=Passport.TYPE_NORMAL)
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'用户名已存在'})
            return

        user = User(name=p['name'], create=int(time.time()), mobile=p['mobile'], address=p['address'])
        self.session.add(user)
        self.session.flush()

        key = base64.urlsafe_b64encode(uuid.uuid4().hex)[:16]
        ps = key + hmac.new(key, p['password'], hashlib.sha256).hexdigest()

        passport = Passport(user=user.id, username=p['username'], password=ps, create=int(time.time()))
        self.session.add(passport)

        corp_user = CorpUser(corp=self.get_current_session().corp, user=user.id, create=int(time.time()), role=p['role'])
        self.session.add(corp_user)
        self.session.flush()

        self.session.commit()

        self.finish({'code': 0, 'data': {'id': corp_user.id, 'user_obj': user.dict()}})


    def update(self):
        user = self.get_argument('user', '')
        if not user:
            self.finish({'code': 1, 'msg': u'user_id不能为空'})
            return

        q = self.get_query().filter_by(user=user)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 2, 'msg': u'公司下无该用户'})
            return

        p = {
            'name': self.get_argument('name', ''),
            'avatar': self.get_argument('avatar', ''),
            'mobile': self.get_argument('mobile', ''),
            'email': self.get_argument('email', ''),
            'address': self.get_argument('address', ''),
            'position': self.get_argument('position', ''),
            'department': self.get_argument('department', ''),
            'sex': self.get_argument('sex', ''),
            'rid': self.get_argument('rid', ''),
            'role': self.get_argument_enum('role', [CorpUser.ROLE_ADMIN, CorpUser.ROLE_NORMAL], None),
        }
        data = ''
        if p['role']:
            d = {'role':p['role']}
            del p['role']
            try:
                self.get_query().filter_by(user=user).update(d, synchronize_session=False)
                self.session.commit()
                data = {'code': 0, 'msg': u'修改成功'}

            except Exception as a:
                data = {'code': 1, 'msg': u'修改失败'}
        edit_data = {}
        for k,v in p.items():
            if v:
                edit_data[k] = v

        if edit_data:
            try:
                self.session.query(User).filter_by(id=user).update(edit_data,synchronize_session=False)
                self.session.commit()
                data = {'code': 0, 'msg': u'修改成功'}
            except Exception as a:
                data = {'code': 2, 'msg': u'修改失败'}

        if data == '':
            data = {'code': 3, 'msg': u'无任何更改'}
        self.finish(data)


    def delete(self):
        if (not self.get_argument('user', '')) and (not self.get_argument('id', '')):
            self.finish({'code': 1, 'msg': u'需要指定 id 或者用户 id'})
            return

        if self.get_argument('id', ''):
            self.get_query().filter_by(corp=self.get_current_session().corp, id=self.p.id).update({'status': CorpUser.STATUS_DELETE}, synchronize_session=False)
        else:
            self.get_query().filter_by(corp=self.get_current_session().corp, user=self.p.user).update({'status': CorpUser.STATUS_DELETE}, synchronize_session=False)

        self.session.commit()
        self.finish({'code': 0})


    def revert(self):

        if (not self.get_argument('user', '')) and (not self.get_argument('id', '')):
            self.finish({'code': 1, 'msg': u'需要指定 id 或者用户 id'})
            return

        if self.get_argument('id', ''):
            self.get_query().filter_by(corp=self.get_current_session().corp, id=self.p.id).update({'status': CorpUser.STATUS_NORMAL}, synchronize_session=False)
        else:
            self.get_query().filter_by(corp=self.get_current_session().corp, user=self.p.user).update({'status': CorpUser.STATUS_NORMAL}, synchronize_session=False)

        self.session.commit()
        self.finish({'code': 0})




class CorpUserHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})

    def check(self):
        if not self.get_argument('corp', ''):
            self.finish({'code': -2, 'msg': u'corp参数不能为空'})
            return

        q = self.session.query(Corp).filter_by(id=self.p.corp, status=Corp.STATUS_NORMAL)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': -3, 'msg': u'不正确的 corp 参数'})
            return

    def get_query(self):
        q = self.session.query(CorpUser).filter_by(corp=self.p.corp)
        return q


    def list_filter(self, q):
        if self.p.get('user', ''):
            q = q.filter_by(user=self.p.user)

        if self.p.get('status', ''):
            q = q.filter_by(status=self.p.status)

        return q


    def get_option_query(self):
        q = self.session.query(CorpUser.id, User.name).join(User, CorpUser.user == User.id)\
                .filter(CorpUser.corp == self.p.corp).order_by(-CorpUser.id)
        return q

    def create(self):
        p = {
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

        q = self.session.query(Passport).filter_by(username=p['username'], type=Passport.TYPE_NORMAL)
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'用户名已存在'})
            return
        cur_time = int(time.time())
        user = User(name=p['name'], create=cur_time)
        self.session.add(user)
        self.session.flush()

        key = base64.urlsafe_b64encode(uuid.uuid4().hex)[:16]
        ps = key + hmac.new(key, p['password'], hashlib.sha256).hexdigest()

        passport = Passport(user=user.id, username=p['username'], password=ps, create=cur_time)
        self.session.add(passport)

        corp_user = CorpUser(corp=self.p.corp, user=user.id, create=cur_time)
        self.session.add(corp_user)
        self.session.flush()

        self.session.commit()

        self.finish({'code': 0, 'data': {'id': corp_user.id, 'user_obj': user.dict()}})


    def delete(self):
        if (not self.get_argument('user', '')) and (not self.get_argument('id', '')):
            self.finish({'code': 1, 'msg': u'需要指定 id 或者用户 id'})
            return

        if self.get_argument('id', ''):
            self.get_query().filter_by(corp=self.p.corp, id=self.p.id).update({'status': CorpUser.STATUS_DELETE}, synchronize_session=False)
        else:
            self.get_query().filter_by(corp=self.p.corp, user=self.p.user).update({'status': CorpUser.STATUS_DELETE}, synchronize_session=False)

        self.session.commit()
        self.finish({'code': 0})


    def revert(self):

        if (not self.get_argument('user', '')) and (not self.get_argument('id', '')):
            self.finish({'code': 1, 'msg': u'需要指定 id 或者用户 id'})
            return


        if self.get_argument('id', ''):
            self.get_query().filter_by(corp=self.p.corp, id=self.p.id).update({'status': CorpUser.STATUS_NORMAL}, synchronize_session=False)
        else:
            self.get_query().filter_by(corp=self.p.corp, user=self.p.user).update({'status': CorpUser.STATUS_NORMAL}, synchronize_session=False)

        self.session.commit()
        self.finish({'code': 0})


