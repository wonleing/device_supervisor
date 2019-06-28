# -*- coding: utf-8 -*-

# gonsi shebei
import base64
import time
import hashlib
import uuid
import hmac
from base import RestHandler
from app.model import User, Corp, Device, CorpDevice,CorpUser,UserDevice

class MyCorpDevice(RestHandler):

    def permission(self):
        action = self.request.uri.split('/')
        device = self.get_argument('device', '')

        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        corp = self.get_current_session().corp
        if not corp:
            self.finish({'code': -2, 'msg': u'没有权限'})
            return

        q = self.session.query(CorpUser).filter_by(corp=corp,user=self.current_user.id, role=CorpUser.ROLE_ADMIN)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': -3, 'msg': u'只有管理员才权限'})
            return

        if action[-1] in ['create']:
            perm = self.session.query(CorpDevice.role).filter_by(corp=self.get_current_session().corp, device=device)
            if not self.session.query(perm.exists()).scalar():
                self.finish({'code': -4, 'err': u'企业下下无该设备'})
                return

            perm = perm.first()
            if perm[0][3] == '0':
                self.finish({'code': -5, 'msg': u'无设备分配权限'})
                return


    def create(self):
        corp_name = self.get_argument('corp_name','')
        device = self.get_argument('device','')
        role = self.get_argument('role','')

        if len(role) != 4:
            self.finish({'code':1,'msg':'the length of role was four '})
            return

        if not role[3] == '0':
            r = list(role)
            r[3] = '0'
            role = ''.join(r)

        corp_id = self.session.query(Corp.id).filter_by(name = corp_name).first()
        if not corp_id:
            self.finish({'code':2,'msg':'the corp_name donot exist'})
            return

        p = {
            'corp':corp_id[0],
            'device':device,
            'role':role,
            'create':time.time()
        }

        device_corp = CorpDevice(**p)
        self.session.add(device_corp)
        self.session.commit()

        self.finish({'code':0,'msg':u'设备添加成功'})

    def delete(self):
        corp = self.get_current_session().corp

        if not self.get_argument('device', ''):
            self.finish({'code': 1, 'msg': u'需要指定 device'})
            return
        user = self.session.query(CorpUser.user).filter_by(corp = corp)
        for i in user:
            print  i[0]
            self.session.query(UserDevice).filter_by(user = i[0],device = self.p.device).delete()
            self.session.commit()

        self.session.query(CorpDevice).filter_by(corp = corp,device=self.p.device).delete()
        self.session.commit()
        self.finish({'code': 0})


class CorpDeviceHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})


    def get_query(self):
        q = self.session.query(CorpDevice)
        if 'corp' in self.p: q = q.filter_by(corp=self.p.corp)
        if 'device' in self.p: q = q.filter_by(device=self.p.device)
        return q


    def delete(self):
        if not self.get_argument('corp', ''):
            self.finish({'code': 2, 'msg': u'需要指定 corp'})
            return

        if not self.get_argument('device', ''):
            self.finish({'code': 1, 'msg': u'需要指定 device'})
            return

        self.get_query().filter_by(corp=self.p.corp, device=self.p.device).delete()
        self.session.commit()
        self.finish({'code': 0})


    def create(self):
        if not self.get_argument('corp', ''):
            self.finish({'code': 2, 'msg': u'需要指定 corp'})
            return

        if not self.get_argument('device', ''):
            self.finish({'code': 1, 'msg': u'需要指定 device'})
            return

        permit = self.get_argument('permit','')
        if not permit or len(permit) != 4 :
            self.finish({'code': 3, 'msg': u'需要指定设备权限且长度为4'})
            return

        q = self.get_query().filter_by(corp=self.p.corp).filter_by(device=self.p.device)
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 4, 'msg': u'关系已存在'})
            return

        p = dict(
            corp=self.p.corp,
            device=self.p.device,
            create=time.time(),
            role = permit
        )

        corp_device = CorpDevice(**p)
        self.session.add(corp_device)
        self.session.commit()
        self.finish({'code': 0,'msg':u'添加成功'})

    def update_device_permit(self):
        if not self.get_argument('corp', ''):
            self.finish({'code': 1, 'msg': u'需要指定 corp'})
            return

        if not self.get_argument('device', ''):
            self.finish({'code': 2, 'msg': u'需要指定 device'})
            return

        permit = self.get_argument('permit', '')
        if not permit or len(permit) != 4:
            self.finish({'code': 3, 'msg': u'需要指定设备权限且长度为4'})
            return

        p = self.session.query(CorpDevice.role).filter_by(corp=self.p.corp,device=self.p.device)\
                                                .update({'role':self.p.permit},synchronize_session=False)
        if p == 1:
            self.session.commit()
            self.finish({'code':0,'msg':u'设备权限修改成功'})
        else:
            self.finish({'code':4,'msg':u'修改失败，该公司无该设备'})

    def get_device_permit(self):

        if not self.get_argument('corp', ''):
            self.finish({'code': 3, 'msg': u'需要指定 corp'})
            return

        page,per_page = self.get_page_and_per_page()
        q = self.get_query()

        count = q.count()
        q = q.limit(per_page).offset((page - 1) * per_page)

        data = []
        for q in q:
            p = {
                'corp': q.corp,
                'role': q.role,
                'device_id':q.device,
                'device_name':q.device_obj.name,
            }
            data.append(p)
        self.finish({'code':0,'count': count,'page': page,'perPage': per_page,'data':data})