# -*- coding: utf-8 -*-

from base import RestHandler
from app.model import User, Device
from app.model import UserDevice


class UserDeviceHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})


    def get_query(self):
        q = self.session.query(UserDevice)
        if 'user' in self.p: q = q.filter_by(user=self.p.user)
        return q

    def get_option_query(self):
        user = self.get_argument('user', '')
        q = self.session.query(UserDevice.user, UserDevice.device).filter_by(user=user).order_by(-UserDevice.device)
        return q


    def create(self):
        if not self.get_argument('user', ''):
            self.finish({'code': 1, 'msg': u'需要指定user'})
            return

        if not self.get_argument('device', ''):
            self.finish({'code': 2, 'msg': u'需要指定device'})
            return

        role = self.get_argument('role', '')
        print (len(role))
        if not role or len(role) != 4:
            self.finish({'code':4,'msg':'the length of role must be four'})
            return

        q = self.get_query().filter_by(user=self.p.user, device=self.p.device)
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'关系已存在'})
            return

        self.session.add(UserDevice(user=self.p.user, device=self.p.device, role = role))
        self.session.commit()
        self.finish({'code': 0})

    def option(self):
        page, per_page = self.get_page_and_per_page()
        is_count = self.get_argument('isCount', '1') == '1'
        q = self.list_filter(self.get_option_query())
        count = q.count() if is_count else 0
        q = q.limit(per_page).offset((page - 1) * per_page)
        obj = [{'user': name, 'device_id': id} for (name,id) in q]

        p = {
            'count': count,
            'page': page,
            'perPage': per_page,
            'isCount': is_count,
            'itemList': obj
        }
        self.finish({'code': 0, 'data': p})

    def delete(self):
        if not self.get_argument('user', ''):
            self.finish({'code': 1, 'msg': u'需要指定user'})
            return

        if not self.get_argument('device', ''):
            self.finish({'code': 2, 'msg': u'需要指定device'})
            return

        self.get_query().filter_by(user=self.p.user, device=self.p.device).delete()
        self.session.commit()
        self.finish({'code': 0})

