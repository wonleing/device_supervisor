# -*- coding: utf-8 -*-

import time
import random
import datetime
import json

from base import RestHandler
from app.model import Device,DeviceAttribute,Telecontrol,User
from app.service.aliyuniot import ALiMessageService
from app.model.aliyuniot import ALiProduct

class MyTelecontrolHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if not self.get_current_session().corp:
            self.finish({'code': -2, 'msg': u'没有权限'})
            return

    def get_query(self):
        q = self.session.query(Telecontrol)
        return q


    def list_filter(self, q):

        # 支持名字过滤
        id = self.get_argument('device_id', '')
        if id:
            q = q.filter(Telecontrol.device_id == id)

        # 支持cpu_id过滤
        cpu_id = self.get_argument('cpu_id', '')
        if cpu_id:
            q = q.filter(Telecontrol.cpu_id == cpu_id)

        status = self.get_argument('status','')
        if status:
            q = q.filter(Telecontrol.status == status)

        return q


    def device_pub(self, device, message, id, Qos):
        command = message[:-1]
        message = "command:" + command + ",};"

        dev_q = self.session.query(Device).filter_by(id=device).first()

        productkey = dev_q.productkey
        dev_name = dev_q.device_name

        field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=productkey).first()
        devicename = ('SQD-' + field_alias[0].upper() + dev_name).encode('utf-8')

        topicfullname = '/' + productkey + '/' + devicename + '/update'

        result_json = ''
        try:
            result_json = ALiMessageService().pub(productkey, topicfullname, message, Qos).sync()
            if result_json:
                if result_json['Success']:
                    self.session.query(Telecontrol).filter_by(id=id).update({'time': time.time(), 'status': 'send'},
                                                                            synchronize_session=False)
                    self.session.commit()
                    return {'code': 0, 'msg': u'下发成功'}

                else:
                    return {'code': -3, 'msg': u'下发失败'}
        except Exception as err:
            return {'code': -4, 'msg': u'下发失败'}




    def create(self):
        device_id = self.get_argument('device',None)
        command = self.get_argument('command',None)

        if not device_id:
            self.finish({'code': -1, 'msg': u'device_id 不能为空'})
            return

        if not command:
            self.finish({'code': -2, 'msg': u'command 不能为空'})
            return

        command = eval(command)

        q = self.session.query(Telecontrol)\
            .filter(Telecontrol.device_id==device_id,Telecontrol.status.in_([Telecontrol.STATUS_NORMAL, Telecontrol.STATUS_FAIL,Telecontrol.STATUS_SEND]))\
            .order_by(-Telecontrol.create)

        pub = {}
        if self.session.query(q.exists()).scalar():
            data = q.first()
            data1 = eval(data.command)
            command_keys = [o for o in command.keys()]
            data_keys = [o for o in data1.keys()]
            all_keys = [o for o in command.keys()]
            all_keys.extend(data_keys)
            new_keys = set(all_keys)

            for keys in new_keys:
                if keys in command_keys and keys in data_keys:
                    pub[keys] = command[keys]

                elif keys in command_keys:
                    pub[keys] = command[keys]

                else:
                    pub[keys] = data1[keys]
            pub = json.dumps(pub)
            self.session.query(Telecontrol).filter_by(id =data.id).update({'command':str(pub),'status':'normal'},synchronize_session=False)
            self.session.commit()

            msg = self.device_pub(device_id, str(command), data.id, 1)
            self.finish(msg)

        else:
            cpu_id = self.session.query(Device.cpu_id).filter_by(id = device_id).first()
            pub = {
                'device_id':device_id,
                'cpu_id':cpu_id[0],
                'command':str(command),
                'create':time.time()
            }
            obj =Telecontrol(**pub)
            self.session.add(obj)
            self.session.commit()

            msg = self.device_pub(device_id,str(command),obj.id,1)
            self.finish(msg)


class TelecontrolHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})

    def get_query(self):
        q = self.session.query(Telecontrol)
        return q


    def list_filter(self, q):

        # 支持名字过滤
        id = self.get_argument('device_id', '')
        if id:
            q = q.filter(Telecontrol.device_id == id)

        # 支持cpu_id过滤
        cpu_id = self.get_argument('cpu_id', '')
        if cpu_id:
            q = q.filter(Telecontrol.cpu_id == cpu_id)

        status = self.get_argument('status','')
        if status:
            q = q.filter(Telecontrol.status == status)

        return q

    def device_pub(self, device, message, id, Qos):
        command = message[:-1]
        message = "command:" + command + ",};"

        dev_q = self.session.query(Device).filter_by(id=device).first()

        productkey = dev_q.productkey
        dev_name = dev_q.device_name

        field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=productkey).first()
        devicename = ('SQD-' + field_alias[0].upper() + dev_name).encode('utf-8')

        topicfullname = '/' + productkey + '/' + devicename + '/update'

        result_json = ''
        try:
            result_json = ALiMessageService().pub(productkey, topicfullname, message, Qos).sync()
            if result_json:
                if result_json['Success']:
                    self.session.query(Telecontrol).filter_by(id=id).update({'time': time.time(), 'status': 'send'},
                                                                            synchronize_session=False)
                    self.session.commit()
                    return {'code': 0, 'msg': u'下发成功'}

                else:
                    return {'code': -3, 'msg': u'下发失败'}
        except Exception as err:
            return {'code': -4, 'msg': u'下发失败'}


    def create(self):
        device_id = self.get_argument('device',None)
        command = self.get_argument('command',None)

        if not device_id:
            self.finish({'code': -1, 'msg': u'device_id 不能为空'})
            return

        if not command:
            self.finish({'code': -2, 'msg': u'command 不能为空'})
            return

        command = eval(command)

        q = self.session.query(Telecontrol)\
            .filter(Telecontrol.device_id==device_id,Telecontrol.status.in_([Telecontrol.STATUS_NORMAL, Telecontrol.STATUS_FAIL,Telecontrol.STATUS_SEND]))\
            .order_by(-Telecontrol.create)

        pub = {}
        if self.session.query(q.exists()).scalar():
            data = q.first()
            data1 = eval(data.command)
            command_keys = [o for o in command.keys()]
            data_keys = [o for o in data1.keys()]
            all_keys = [o for o in command.keys()]
            all_keys.extend(data_keys)
            new_keys = set(all_keys)

            for keys in new_keys:
                if keys in command_keys and keys in data_keys:
                    pub[keys] = command[keys]

                elif keys in command_keys:
                    pub[keys] = command[keys]

                else:
                    pub[keys] = data1[keys]
            pub = json.dumps(pub)
            self.session.query(Telecontrol).filter_by(id =data.id).update({'command':str(pub),'status':'normal'},synchronize_session=False)
            self.session.commit()

            msg = self.device_pub(device_id, str(command), data.id, 1)
            self.finish(msg)

        else:
            cpu_id = self.session.query(Device.cpu_id).filter_by(id = device_id).first()
            pub = {
                'device_id':device_id,
                'cpu_id':cpu_id[0],
                'command':str(command),
                'create':time.time()
            }
            obj =Telecontrol(**pub)
            self.session.add(obj)
            self.session.commit()

            msg = self.device_pub(device_id,str(command),obj.id,1)
            self.finish(msg)



