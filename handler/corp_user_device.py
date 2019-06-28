# -*- coding: utf-8 -*-

from base import RestHandler
from app.model import User, Device, Corp
from app.model import UserDevice
from app.model import CorpUser, CorpDevice


class MyCorpUserDeviceHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        corp = self.get_current_session().corp
        if not corp:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        q = self.session.query(CorpUser).filter_by(corp=corp, user=self.current_user.id, role=CorpUser.ROLE_ADMIN)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': -1, 'msg': u'只有管理员才有权限'})
            return

    def get_query(self):
        q = self.session.query(UserDevice)
        corp = self.get_current_session().corp
        user_q = self.session.query(CorpUser.user).filter_by(corp=corp)
        device_q = self.session.query(CorpDevice.device).filter_by(corp=corp)
        q = q.filter(UserDevice.user.in_(user_q), UserDevice.device.in_(device_q))
        if 'user' in self.p: q = q.filter_by(user=self.p.user)
        return q


    def create(self):
        if not self.get_argument('user', ''):
            self.finish({'code': 1, 'msg': u'需要指定user'})
            return

        if not self.get_argument('device', ''):
            self.finish({'code': 2, 'msg': u'需要指定device'})
            return

        corp = self.get_current_session().corp
        user_q = self.session.query(CorpUser.user).filter_by(corp=corp, user=self.p.user)
        
        if not self.session.query(user_q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'错误的user'})
            return

        device_q = self.session.query(CorpDevice.device).filter_by(corp=corp, device=self.p.device)
        if not self.session.query(device_q.exists()).scalar():
            self.finish({'code': 4, 'msg': u'错误的device'})
            return

        if not self.get_argument('permit', ''):
            self.finish({'code': 2, 'msg': u'需要指定 设备权限'})
            return

        q = self.get_query().filter_by(user=self.p.user, device=self.p.device)
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 5, 'msg': u'关系已存在'})
            return

        self.session.add(UserDevice(user=self.p.user, device=self.p.device,role=self.p.permit))
        self.session.commit()
        self.finish({'code': 0,'msg':u'添加成功'})

    def delete(self):
        if not self.get_argument('user', ''):
            self.finish({'code': 1, 'msg': u'需要指定user'})
            return

        if not self.get_argument('device', ''):
            self.finish({'code': 2, 'msg': u'需要指定device'})
            return

        corp = self.get_current_session().corp
        user_q = self.session.query(CorpUser.user).filter_by(corp=corp, user=self.p.user)
        
        if not self.session.query(user_q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'错误的user'})
            return

        device_q = self.session.query(CorpDevice.device).filter_by(corp=corp, device=self.p.device)
        if not self.session.query(device_q.exists()).scalar():
            self.finish({'code': 4, 'msg': u'错误的device'})
            return

        self.get_query().filter_by(user=self.p.user, device=self.p.device).delete(synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})

    def update_user_role(self):
        if not self.get_argument('user', ''):
            self.finish({'code': 1, 'msg': u'需要指定user'})
            return

        if not self.get_argument('device', ''):
            self.finish({'code': 2, 'msg': u'需要指定device'})
            return

        corp = self.get_current_session().corp

        user_q = self.session.query(CorpUser.user).filter_by(corp=corp, user=self.p.user)
        if not self.session.query(user_q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'错误的user'})
            return

        device_q = self.session.query(CorpDevice.device).filter_by(corp=corp, device=self.p.device)
        if not self.session.query(device_q.exists()).scalar():
            self.finish({'code': 4, 'msg': u'错误的device'})
            return

        if not self.get_argument('role',''):
            self.finish({'code':5,'msg':u'需要指定用户权限'})
            return

        self.get_query().filter_by(user=self.p.user,device=self.p.device).update({'role':self.p.role},synchronize_session=False)
        self.finish({'code': 0,'msg':u'修改成功'})

