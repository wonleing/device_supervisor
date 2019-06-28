# -*- coding: utf-8 -*-


import time
import datetime
import json
import requests

from base import RestHandler,BaseHandler
from app.service.luosimao import LuoSiMao
from app.model.device import Device,DeviceWarnRelation
from app.model.user import User,UserDevice

class NewWarnMessageHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})

    def post(self, action):

        # body = self.get_argument('data','')
        # if not body:
        #     self.finish({'code': 1,'msg':'not body'})
        # print body
        # body = json.loads(body)
        p = {
            'cpu_id':  self.get_argument('cpuid',''),
            'code':  self.get_argument('code',''),
            'content': json.loads(self.get_argument('warn','')),
            'time': self.get_argument('time',''),
            'create': int(time.time()),
        }
        lis = []
        for name,value in p['content'].items():
            if value['stu'] == 0:
                self.finish({'code': 0})
                return
            stu = value['stu']
            perceatage = value['perceatage']
            str1 = "select {} from field_alias where cpu_id = :cpu_id".format(name)
            if not p['cpu_id']:
                self.finish({'code':1,'msg':'the cpu_id is missing'})
                return
            if not p['time']:
                p['time'] = p['create']

            if int(p['code']) == 0:
                sql = 'update device set status = :status where cpu_id = :cpu_id'
                self.session.execute(sql,{'status':'normal','cpu_id':p['cpu_id']})
                sql = 'update warn set status = :status,`create` = :create where cpu_id = :cpu_id'
                self.session.execute(sql, {'status':'posed','create':p['create'],'cpu_id':p['cpu_id']})
                self.session.commit()
                self.finish({'code': 0})
                return

            else:
                sql_name = self.session.execute('select name from device where cpu_id = :cpu_id', {'cpu_id': p['cpu_id']}).fetchone()
                if sql_name:
                    sql_type = self.session.execute(str1, {'cpu_id': p['cpu_id']}).fetchone()
                    if sql_type:
                        if not sql_type[0]:
                           continue
                        if name not in sql_type:
                            self.finish({'code': 1})
                            return
                        sql_name = sql_name[0].encode('utf-8')
                        sql_type_name = sql_type[0].split("|")[1].encode('utf-8')
                        if int(stu) == 1:
                            statu = '低'
                        elif int(stu) == 2:
                            statu = '高'
                        else:
                            continue
                        # content = '{}的{}过{}，百分比为{}%'.format(sql_name,sql_type_name,statu,perceatage)
                        content = self.status_tontent(name).format(sql_name,sql_type_name,statu,perceatage)
                        lis.append(content)
                        sql = 'update device set status = :status where cpu_id = :cpu_id'
                        self.session.execute(sql,{'status':'warning','cpu_id':p['cpu_id']})
                        p['content'] = content
                        sql = 'insert into warn (`cpu_id`, `code`, `content`, `time`, `create`) values (:cpu_id, :code, :content, :time, :create)'
                        self.session.execute(sql, p)
                        self.session.commit()
                    else:
                        self.finish({'code': 1,'msg':u'not sql_type'})
                        return
                else:
                    self.finish({'code': 1, 'msg': u'not sql_name'})
                    return
        tontents = ','.join(lis)
        cpu_id = p['cpu_id']
        # self.send_sms(cpu_id,tontents)
        # print cpu_id,tontents
        self.finish({'code': 0,"msg":"sucess","data":{"cpu_id":cpu_id,"tontents":tontents}})
        return

    def status_tontent(self,name):
        if name == 'height1':
            return '{}的{}过{}，百分比为{}%'
        elif name == 'pressure1':
            return '{}的{}过{}，当前压力为{}'
        else:
            return '{}的{}过{}，当数值为{}'


    def send_sms(self,cpu_id,tontents): #调用短信接口
        device = self.session.query(Device.id).filter_by(cpu_id = cpu_id).first()
        devices = self.session.query(UserDevice.user).filter_by(device = device[0]).first()
        mobile = self.session.query(User.mobile).filter_by(id=devices[0]).first()
        if not mobile:
            self.finish({'code':1})
        luosimao = LuoSiMao()
        tontents = tontents.decode('utf-8')
        luosimao.send_warn(mobile[0],device[0],tontents).sync()


class NewWarnHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})

    def post(self,action):
        # 查询设备关系，调用阿里云接口函数
        cpu_id = self.get_argument('cpuid', '')
        if not cpu_id:
            self.finish({'code': '1', 'msg': 'not cpuid'})
            return
        relation_warn = self.session.query(
            DeviceWarnRelation.relation_warn_1,
            DeviceWarnRelation.relation_warn_2,
            DeviceWarnRelation.relation_warn_3,
            DeviceWarnRelation.relation_warn_4,
            DeviceWarnRelation.relation_warn_5,
        ).filter_by(cpu_id=cpu_id, ).first()
        self.session.commit()
        if relation_warn == "" or relation_warn == None:
            self.finish({'code': '1', 'msg': 'not rellation_warn'})
            return
        data = []
        for cpu_id in relation_warn:
            if cpu_id == None or cpu_id == "":
                break
            productkey, device_name = self.session.query(Device.productkey, Device.device_name).filter_by(
                cpu_id=cpu_id).first()
            if productkey == None or productkey == "" or device_name == None or device_name == "":
                self.finish({'code': 1, u'msg': 'productkey or device_name is none'})
                return
            self.session.commit()
            res = {
                'productkey': productkey,
                'remarks': 'warn',
                'Qos': '1',
                'devicename': device_name,
                'topicfullname': '/' + productkey + '/' + device_name + '/update',
                'message': 'warn'
            }
            data.append(res)
        self.finish({'code':0,'msg':'sucess','data':list_dict_duplicate_removal(data)})

class WarnCloseHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})

    def post(self,action):
        # 查询设备关系，调用阿里云接口函数
        cpu_id = self.get_argument('cpuid', '')
        if not cpu_id:
            self.finish({'code': '1', 'msg': 'not cpuid'})
            return
        relation_warn = self.session.query(
            DeviceWarnRelation.relation_warn_1,
            DeviceWarnRelation.relation_warn_2,
            DeviceWarnRelation.relation_warn_3,
            DeviceWarnRelation.relation_warn_4,
            DeviceWarnRelation.relation_warn_5,
        ).filter_by(cpu_id=cpu_id, ).first()
        self.session.commit()
        if relation_warn == "" or relation_warn == None:
            self.finish({'code': '1', 'msg': 'not rellation_warn'})
            return
        data = []
        for cpu_id in relation_warn:
            if cpu_id == None or cpu_id == "":
                break
            productkey, device_name = self.session.query(Device.productkey, Device.device_name).filter_by(
                cpu_id=cpu_id).first()
            if productkey == None or productkey == "" or device_name == None or device_name == "":
                self.finish({'code': 1, u'msg': 'productkey or device_name is none'})
                return
            self.session.commit()
            device_name = 'SQD-CONTR' + device_name
            res = {
                'productkey': productkey,
                'remarks': 'warn',
                'Qos': '1',
                'devicename': device_name,
                'topicfullname': '/' + productkey + '/' + device_name + '/update',
                'message': 'command:{valve1:"open", valve2:"open", valve3:"open",};'
            }
            data.append(res)
        self.finish({'code':0,'msg':'sucess','data':list_dict_duplicate_removal(data)})

def list_dict_duplicate_removal(sel):
    data_list = sel
    run_function = lambda x, y: x if y in x else x + [y]
    return reduce(run_function, [[], ] + data_list)