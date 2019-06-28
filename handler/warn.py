# -*- coding: utf-8 -*-
 
import time
from base import RestHandler
from app.model import User,Device,UserDevice,CorpUser,CorpDevice
from app.model.warn import Warn,WarnContrast

class MyWarnHandler(RestHandler ):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        corp = self.get_current_session().corp
        if not corp:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

    def get_query(self):

        corp = self.get_current_session().corp
        q = self.session.query(CorpUser).filter_by(corp=corp,
                                                   user=self.current_user.id,
                                                   role=CorpUser.ROLE_ADMIN)

        if self.session.query(q.exists()).scalar():
            sub = self.session.query(CorpDevice.device).filter_by(corp=self.get_current_session().corp)
        else:
            sub = self.session.query(UserDevice.device).filter_by(user=self.current_user.id)
        return sub

    def send_warn(self):
        b_time = self.get_argument('b_time','')
        e_time = self.get_argument('e_time', '')
        page, per_page = self.get_page_and_per_page()
        sub = self.get_query()
        data = []
        count = 0
        cpu_id_list = self.session.query(Device.cpu_id).filter(Device.id.in_(sub))
        cpu_id = self.get_argument('cpu_id','')
        cpu_id = [x.strip() for x in filter(None, cpu_id.split(','))]
        if cpu_id:
            cpu_id_list = cpu_id_list.filter(Device.cpu_id.in_(cpu_id))

        for i in cpu_id_list:
            warn_id = self.session.query(Warn.id).filter(Warn.cpu_id == i[0],Warn.status.in_([Warn.STATUS_POSED]))
            if b_time:
                warn_id = warn_id.filter(Warn.time >= b_time)
            if e_time:
                warn_id = warn_id.filter(Warn.time <= e_time)
            warn_id = warn_id.order_by(Warn.time.desc()).all()

            q = self.session.query(Device).filter_by(cpu_id=i[0]).first()
            device_name = q.name
            if warn_id:
                for temp in warn_id:
                    warn_dict = {}
                    msg = self.session.query(Warn).filter_by(id=temp[0]).first().dict()
                    if int(msg['code']):
                        count += 1
                        warn_dict['cpu_id'] = i[0]
                        warn_dict['id'] = msg['id']
                        warn_dict['code'] = msg['code']
                        warn_dict['content'] = msg['content']
                        warn_dict['time'] = msg['time']
                        warn_dict['status'] = msg['status']
                        warn_dict['name'] = device_name

                        warn_dict['warn_contrast']= msg['warn_contrast_obj']['content']
                        data.append(warn_dict)

        data = data[(page - 1) * per_page:page * per_page]
        self.finish({'code': 0, 'warn_msg': data, 'count': count})


    def warn_display(self):
        page, per_page = self.get_page_and_per_page()
        sub = self.get_query()
        cpu_id_list = self.session.query(Device.cpu_id).filter(Device.id.in_(sub), Device.status.in_([Device.STATUS_WARNING]))

        cpu_id = self.get_argument('cpu_id', '')
        cpu_id = [x.strip() for x in filter(None, cpu_id.split(','))]
        if cpu_id:
            cpu_id_list = cpu_id_list.filter(Device.cpu_id.in_(cpu_id))

        count = 0
        obj = []
        for i in cpu_id_list:
            warn_dict ={}
            q = self.session.query(Device).filter_by(cpu_id=i[0]).first()
            device_name = q.name
            q  = self.session.query(Warn).filter(Warn.cpu_id == i[0],Warn.status.in_([Warn.STATUS_NORMAL]))
            if q:
                count += q.count()
                for o in q:
                    warn = o.dict()
                    warn_dict['cpu_id'] = i[0]
                    warn_dict['id'] = warn['id']
                    warn_dict['code'] = warn['code']
                    warn_dict['content'] = warn['content']
                    warn_dict['time'] = warn['time']
                    warn_dict['status'] = warn['status']
                    warn_dict['name'] = device_name
                    warn_dict['warn_contrast'] = warn['warn_contrast_obj']['content']
                    obj.append(warn_dict)

        obj = obj[(page - 1) * per_page:page * per_page]
        self.finish({'code': 0, 'count': count, 'itemList': obj})

class WarnHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})

    def get_query(self):

        q = self.session.query(Warn)
        return q


    def list_filter(self, q):

        # 支持名字过滤
        cpu_id = self.get_argument('cpu_id', '')
        b_time = self.get_argument('b_time', '')
        e_time = self.get_argument('e_time', '')
        status = self.get_argument('status', '')
        if cpu_id:
            cpu_id = [x.strip() for x in filter(None, cpu_id.split(','))]
            q = q.filter(Warn.cpu_id.in_(cpu_id))
        if b_time:
            q = q.filter(Warn.create >= b_time)
        if e_time:
            q = q.filter(Warn.create <= e_time)
        if status:
            q = q.filter(Warn.status == status)
        q = q.order_by(-Warn.create)
        return q



    def send_warn(self):
        u_id = self.get_argument('user_id','')
        status = self.get_argument('status','')
        warn = self.session.query(Warn)

        if not u_id:
            self.finish({'code':1,'msg':u'the user_id is missing'})
            return
        u_id = int(u_id)

        if status:
            warn = warn.filter(Warn.status == status)


        q = self.session.query(UserDevice.device).filter_by(user=u_id).all()
        data = []
        count = 0
        for i in q:
            cpuid = self.session.query(Device.cpu_id).filter_by(id=i[0]).first()
            warn = warn.filter(Warn.cpu_id == cpuid[0]).all()
            device = self.session.query(Device).filter_by(cpu_id=cpuid[0]).first()
            device_name = device.name
            if warn:
                count += len(warn)
                for temp in warn:
                    warn_dict = {}
                    msg = self.session.query(Warn).filter_by(id=temp.id).first().dict()
                    warn_dict['cpu_id'] = i[0]
                    warn_dict['code'] = msg['code']
                    warn_dict['content'] = msg['content']
                    warn_dict['time'] = msg['time']
                    warn_dict['status'] = msg['status']
                    warn_dict['name'] = device_name
                    warn_dict['warn_contrast'] = msg['warn_contrast_obj']['content']
                    data.append(warn_dict)
        self.finish({'code': 0, 'warn_msg': data,'count':count})

class WarnContrastHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

    def get_query(self):
        q = self.session.query(WarnContrast)
        return q

    def list_filter(self,q):
        #支持code过滤
        code = self.get_argument('code','')
        if code:
            q = q.filter(WarnContrast.code == code)

        id = self.get_argument('id', '')
        if id:
            q = q.filter(WarnContrast.id == id)

        content = self.get_argument('content', '')
        if content:
            q = q.filter(WarnContrast.content == content)

        return q

    def create(self):
        code = self.get_argument('code','')
        content = self.get_argument('content','')
        if not code:
            self.finish({'code':1,'msg':u'code不能为空'})
            return
        if not content:
            self.finish({'code':2,'msg':u'content不能为空'})
            return
        q = self.session.query(WarnContrast).filter_by(code = code).first()
        if q:
            self.finish({'code':3,'msg':u'该code已经存在'})
            return

        p = {
            'code': code,
            'content':content,
            'create':int(time.time()),
        }
        try :
            warncontrast = WarnContrast(**p)
            self.session.add(warncontrast)
            self.session.commit()
            self.finish({'code':0,'msg':u'创建成功'})
        except:
            self.finish({'code':1,'msg':u'创建失败'})

    def update(self):
        id = self.get_argument('id','')

        if not id:
            self.finish({'code':1,'msg':u'id不能为空'})
            return

        p = {
            'code':self.get_argument('code',''),
            'content': self.get_argument('content',''),
            'create' : time.time()
        }

        data = {}
        for k in p:
            if p[k]:data[k] = p[k]

        if p['code']:
            q = self.get_query().filter_by(code = p['code']).first()
            if q:
                self.finish({'code':2,'msg':u'该code已经存在'})
                return

        try:
            self.get_query().filter_by(id = id).update(p)
            self.session.commit()
            self.finish({'code': 0, 'msg': u'更新成功'})
        except:
            self.finish({'code': 1, 'msg': u'更新失败'})



    def delete(self):
        id = self.get_argument('id','')
        if not id:
            self.finish({'code':1,'msg':u'id不能为空'})
            return
        try:
            self.session.query(WarnContrast).filter_by(id = id).delete()
            self.session.commit()
            self.finish({'code': 0, 'msg': u'删除成功'})
        except:
            self.finish({'code': 2, 'msg': u'删除失败'})








