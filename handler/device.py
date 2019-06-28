# -*- coding: utf-8 -*-

import time
import random
import datetime
import re
import sys
from base import RestHandler
from app.model import Device, User, CorpDevice, Corp, FieldAlias, DeviceRule, Rule, CorpUser, UserDevice, \
    DeviceAttribute, Supply, SupplyPrint, DeviceAppendix
from app.service.aliyuniot import ALiDeviceService, ALiMessageService
from app.model.aliyuniot import ALiProduct
from app.model.aliyuniot import ProductAttribute


class MyDeviceHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if not self.get_current_session().corp:   #gongsiyuangong
            self.finish({'code': -3, 'msg': u'没有权限'})
            return
        action = self.request.uri.split('/')

        if action[-1] in ["set_attribute","update","update_attribute","delete_attribute"]:
            corp = self.get_current_session().corp
            q = self.session.query(CorpUser).filter_by(corp=corp,
                                                       user=self.current_user.id,
                                                       role=CorpUser.ROLE_ADMIN)

            if not self.session.query(q.exists()).scalar():
                self.finish({'code': -2, 'msg': u'只有企业管理员才权限'})
                return

    def get_query(self):

        corp = self.get_current_session().corp
        q = self.session.query(CorpUser).filter_by(corp=corp,
                                                   user=self.current_user.id,
                                                   role=CorpUser.ROLE_ADMIN)

        if self.session.query(q.exists()).scalar():
            # admin
            sub = self.session.query(CorpDevice.device).filter_by(corp=self.get_current_session().corp)
        else:
            # normal
            sub = self.session.query(UserDevice.device).filter_by(user=self.current_user.id)

        q = self.session.query(Device).filter(Device.id.in_(sub),
                                              Device.status.in_([Device.STATUS_WARNING, Device.STATUS_NORMAL]))
        return q

    def update(self):
        id = self.get_argument('id', '')

        if not id:
            self.finish({'code': 1, 'msg': u'id不能为空'})
            return
        try:
            id = int(id)
        except:
            self.finish({'code': 2, 'msg': u'id格式错误'})
            return

        q = self.get_query().filter(Device.id == id)

        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'设备不存在此id'})
            return

        p = {
            'name': self.get_argument('name', None)
        }

        if p['name']:
            q.update(p, synchronize_session=False)
            self.session.commit()
        self.finish({'code': 0})

    def set_attribute(self):
        '创建属性'
        p = {
            'cpu_id': self.get_argument('cpu_id', ''),
            'code': self.get_argument('code', ''),
            'name': self.get_argument('name', ''),
            'value': self.get_argument('value', ''),
            'user': self.get_argument('user', 1),
            'type': self.get_argument('type', DeviceAttribute.TYPE_CONF),
        }

        if not p['cpu_id']:
            self.finish({'code': 1, 'msg': u'cpu_id 不能为空'})
            return

        if not p['code']:
            self.finish({'code': 2, 'msg': u'code 不能为空'})
            return

        q = self.session.query(DeviceAttribute).filter_by(cpu_id=p['cpu_id'], code=p['code'])
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'属性已创建'})
            return
        else:
            self.session.add(DeviceAttribute(**p))
            self.session.commit()
            self.finish({'code': 0})

    def update_attribute(self):

        cpu_id = self.get_argument('cpu_id', '')
        data = self.get_argument('data', '')
        key_list = ['name', 'value', 'user', 'type']

        if not cpu_id:
            self.finish({'code': 1, 'msg': u'cpu_id 不能为空'})
            return

        if not data:
            self.finish({'code': 2, 'msg': u'data 不能为空'})
            return

        try:
            data = eval(data)
        except:
            self.finish({'code': 3, 'msg': u'data 数据格式错误'})
            return

        message = {}
        attribute_data = [{'cpu_id': cpu_id}]
        if type(data) == dict:
            a = []
            a.append(data)
            data = a

        for i in data:
            p = {}
            if 'code' not in i.keys():
                self.finish({'code': 4, 'msg': u'code不能为空'})
                return

            if 'value' in i.keys():
                message[i['code']] = i['value']

            for j in key_list:
                if j in i.keys():
                    p[j] = i[j]

            if 'type' in p.keys():
                if p['type'] not in [DeviceAttribute.TYPE_CONF, DeviceAttribute.TYPE_CONT]:
                    self.finish({'code': 5, 'msg': u'输入的type类型错误'})
                    return
            code = i['code']

            q = self.session.query(DeviceAttribute).filter(DeviceAttribute.cpu_id == cpu_id,
                                                           DeviceAttribute.code == code)

            if not self.session.query(q.exists()).scalar():
                self.finish({'code': 6, 'msg': u'该设备不存在此code:%s' % code})
                return

            if q.first().user != 1:
                self.finish({'code': 7, 'msg': u'此code：%s不可修改' % code})
                return

            if not p:
                self.finish({'code': 8, 'msg': u'请输入正确的属性修改字段'})
                return

            p['code'] = code
            q.update(p, synchronize_session=False)
            self.session.commit()
            attribute_data.append(p)

        if message:
            device = self.session.query(Device).filter_by(cpu_id=cpu_id).first()
            productkey = device.productkey
            dev_name = device.device_name
            field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=productkey).first()
            devicename = ('SQD-' + field_alias[0].upper() + dev_name)
            topicfullname = '/' + productkey + '/' + devicename + '/update'
            message = 'renew:%s' % message

            result_json = ALiMessageService().pub(productkey, topicfullname, message, Qos=1).sync()
            if result_json['Success']:
                self.finish({'code': 0, 'msg': u'设备属性配置成功，发送到aliyun成功', 'data': attribute_data})
                return
            else:
                self.finish({'code': 9, 'msg': u'设备属性配置成功，发送到aliyun 失败'})
                return

        self.finish({'code': 0, 'msg': u'本地设备属性配置成功', 'data': attribute_data})

    def delete_attribute(self):
        '删除一个属性'

        cpu_id = self.get_argument('cpu_id', '')
        code = self.get_argument('code', '')

        if not cpu_id:
            self.finish({'code': 1, 'msg': u'cpu_id 不能为空'})
            return
        if not code:
            self.finish({'code': 2, 'msg': u'code 不能为空'})
            return
        self.session.query(DeviceAttribute).filter_by(cpu_id=cpu_id, code=code).delete(synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})

    def list_filter(self, q):

        # 支持名字过滤
        name = self.get_argument('name', '')
        if name:
            q = q.filter(Device.name.ilike('%' + name + '%'))

        # 支持cpu_id过滤
        cpu_id = self.get_argument('cpu_id', '')
        if cpu_id:
            q = q.filter(Device.cpu_id == cpu_id)

        # 支持 id 过滤
        id = self.get_argument('id', '')
        if id:
            q = q.filter(Device.id == id)

        status = self.get_argument('status', '')
        if status:
            q = q.filter(Device.status == status)

        return q

    def get_option_query(self):
        sub = self.session.query(CorpDevice.device).filter_by(corp=self.get_current_session().corp)
        q = self.session.query(Device.id, Device.name) \
            .filter(Device.status == Device.STATUS_NORMAL,
                    Device.id.in_(sub)).order_by(-Device.id)
        return q

    def field_alias(self):
        cpu_id = self.get_argument('cpu_id', '')
        if not cpu_id:
            self.finish({'code': 1, 'msg': u'cpu_id 不能为空'})
            return

        q = self.session.query(FieldAlias).filter_by(cpu_id=cpu_id)
        if not self.session.query(q.exists()).scalar():
            obj = FieldAlias(cpu_id=cpu_id)
            self.session.add(obj)
            self.session.commit()
        else:
            obj = q.first()

        map = obj.dict()
        del map['id']

        self.finish({'code': 0, 'data': {'map': map}})

    def get_rule(self):
        '获取规则'

        id = self.get_argument('id', '')
        q = self.get_query()
        q = q.filter(Device.id == id)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 1, 'msg': u'错误的id'})
            return

        q = self.session.query(DeviceRule.rule).filter_by(device=id)
        obj = self.session.query(Rule).filter(Rule.id.in_(q))
        data = [x.dict() for x in obj.all()]
        self.finish({'code': 0, 'data': data})

    def status(self):
        productkey = self.get_argument('productkey', None)
        deviceid = self.get_argument('device_id', None)

        field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=productkey)
        if not self.session.query(field_alias.exists()).scalar():
            self.finish({'code': 0, 'err': u'产品别名未设置'})
        else:

            field_alias = field_alias.first()
            q = self.get_query().filter(Device.id == deviceid).first()
            devicename = ('SQD-' + field_alias[0].upper() + q.device_name).encode('utf-8')

            addr = sys._getframe().f_code.co_name
            result_json = ALiDeviceService().process_data(productkey, devicename, addr).sync()
            if result_json['Success'] == False:
                self.finish({'code': 1, 'data': result_json})
                return
            self.finish({'code': 0, 'data': result_json})

    def status_statistics(self):
        q = self.get_query()
        n_unactive, n_online, n_disable, n_offline,n_noexists= 0,0,0,0,0
        for i in q:
            field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=i.productkey)
            if self.session.query(field_alias.exists()).scalar():
                field_alias = field_alias.first()
                devicename = ('SQD-' + field_alias[0].upper() + i.device_name).encode('utf-8')
                print(devicename)
                print (i.productkey)
                result_json = ALiDeviceService().process_data(i.productkey, devicename, 'status').sync()
                if result_json['Success'] == False:
                    n_noexists += 1
                else:
                    if result_json['Data']['Status'] == "UNACTIVE":
                        n_unactive += 1
                    elif result_json['Data']['Status'] == "DISABLE":
                        n_disable += 1
                    elif result_json['Data']['Status'] == "OFFLINE":
                        n_offline += 1
                    else:
                        n_online += 1
        self.finish({'code':0,'data':{'n_unactive':n_unactive,'n_disable':n_disable,
                                      'n_offline':n_offline,'n_online':n_online,'n_noexists':n_noexists}})


    def query_device_corp(self):
        device = self.get_argument('device', '')

        q = self.get_query().filter_by(id=device)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 1, 'msg': u'用户无该设备'})
            return

        if not device:
            self.finish({'code': 1, 'msg': u'device不能为空'})
            return

        p = self.session.query(CorpDevice).filter_by(corp=self.get_current_session().corp, device=device)
        if not self.session.query(p.exists()).scalar():
            self.finish({'code': 2, 'err': u'该设备无所属企业'})
            return

        q = self.session.query(CorpDevice).filter_by(device=device)
        data = []
        for i in q:
            d = {
                'device': i.device,
                'role': i.role,
                'corp_name': i.corp_obj.name,
                'corp_id': i.corp_obj.id,
            }
            data.append(d)

        self.finish({'code': 0, 'data': data})

    def get_attribute_list(self):
        '获取属性列表'

        cpu_id = self.get_argument('cpu_id', '')
        code = self.get_argument('code', '')

        if not cpu_id:
            self.finish({'code': 1, 'msg': u'cpu_id 不能为空'})
            return

        q = self.session.query(DeviceAttribute).filter_by(cpu_id=cpu_id)

        if code:
            code_list = [x.strip() for x in filter(None, code.split(','))]
            q = q.filter(DeviceAttribute.code.in_(code_list))

        device_attr = [o.dict() for o in q]

        info = {
            "device_attr": device_attr,
        }

        self.finish({'code': 0, 'data': info})

    def timeout_remind(self):
        cpu_id = self.get_argument('cpu_id','')
        q = self.get_query()
        if cpu_id:
            q = q.filter(Device.cpu_id == cpu_id)
        data = {}
        for i in q:
            create = self.session.query(DeviceAttribute.value).filter(DeviceAttribute.cpu_id ==i.cpu_id,
                                                                      DeviceAttribute.code == "create").first()
            valid = self.session.query(DeviceAttribute.value).filter(DeviceAttribute.cpu_id == i.cpu_id,
                                                                     DeviceAttribute.code == "valid").first()
            advance = self.session.query(DeviceAttribute.value).filter(DeviceAttribute.cpu_id == i.cpu_id,
                                                                     DeviceAttribute.code == "advance").first()
            if not create or not valid:
                continue
            v_time = int(re.match(r'^\d+',valid[0]).group())

            day = re.search(ur'\u5929+',valid[0])
            month = re.search(ur'\u6708+', valid[0])
            year = re.search(ur'\u5e74+', valid[0])

            if day:
                valid = v_time*24*3600
            if month:
                valid = v_time * 24 * 3600*30
            if year:
                valid = v_time *365*24*3600
            ctime = create[0].encode('utf-8')
            cyear = int(ctime.split('.')[0])
            cmonth = '%02d' % int(ctime.split('.')[1])
            cday = '%02d' % int(ctime.split('.')[-1])
            ctime = '%s-%s-%s' % (cyear,cmonth,cday)
            create_time = time.strptime(ctime, '%Y-%m-%d')
            create_time = time.mktime(create_time)
            remain_days = int(create_time) + valid - int(time.time())

            if advance:
                advance = int(advance[0])*24*3600
            else:
                advance = 30*24*3600

            if remain_days<advance:
                data[i.name] = round(float(remain_days)/float(24*3600))
        count = len(data)
        self.finish({'code':0,'itemlist':data,'count':count})





    def supply_recode(self):
        q = self.session.query(Supply)
        dev = self.get_query()
        q = q.filter(Supply.cpu_id.in_([i.cpu_id for i in dev]))

        cpu_id = self.get_argument('cpu_id', '')
        if cpu_id:
            q = q.filter(Supply.cpu_id == cpu_id)

        page, per_page = self.get_page_and_per_page()

        medium = self.get_argument('medium', '')
        if medium:
            q = q.filter(Supply.medium.ilike('%' + medium + '%'))

        id = self.get_argument('id', '')
        if id:
            q = q.filter(Supply.id == id)

        bt = self.get_argument('bt', '')
        if bt:
            q = q.filter(Supply.create>=bt)

        et = self.get_argument('et', '')
        if et:
            q = q.filter(Supply.create <= et)

        q = q.order_by(Supply.create.desc())
        limit = self.get_argument('limit', '')
        if limit:
            q = q.limit(int(limit))
            count = q.count()
            obj = [o.dict() for o in q]
            obj = obj[(page - 1) * per_page:page * per_page]
        else:
            count = q.count()
            q = q.limit(per_page).offset((page - 1) * per_page)
            obj = [o.dict(self.list_defer()) for o in q]
        for i in obj:
            device = self.session.query(Device).filter_by(cpu_id = i['cpu_id']).first()
            i['devicename'] = device.name


        p = {
            'count': count,
            'page': page,
            'perPage': per_page,
            'itemList': obj
        }
        self.finish({'code': 0, 'data': p})

    def supply_print(self):
        q = self.session.query(SupplyPrint)
        dev = self.get_query()
        q = q.filter(SupplyPrint.cpu_id.in_([i.cpu_id for i in dev]))
        cpu_id = self.get_argument('cpu_id', '')
        if cpu_id:
            q = q.filter(SupplyPrint.cpu_id == cpu_id)

        page, per_page = self.get_page_and_per_page()

        supply = self.get_argument('supply', '')
        if supply:
            q = q.filter(SupplyPrint.supply == supply)

        medium = self.get_argument('medium', '')
        if medium:
            q = q.filter(SupplyPrint.medium.ilike('%' + medium + '%'))

        supplier = self.get_argument('supplier', '')
        if supplier:
            q = q.filter(SupplyPrint.supplier.ilike('%' + supplier + '%'))

        operator = self.get_argument('operator', '')
        if operator:
            q = q.filter(SupplyPrint.operator.ilike('%' + operator + '%'))

        q = q.order_by(SupplyPrint.create.desc())

        limit = self.get_argument('limit', '')
        if limit:
            q = q.limit(int(limit))
            count = q.count()
            obj = [o.dict() for o in q]
            obj = obj[(page - 1) * per_page:page * per_page]
        else:
            count = q.count()
            q = q.limit(per_page).offset((page - 1) * per_page)
            obj = [o.dict(self.list_defer()) for o in q]

        p = {
            'count': count,
            'page': page,
            'perPage': per_page,
            'itemList': obj
        }
        self.finish({'code': 0, 'data': p})

    def add_supply(self):
        p = {
            "cpu_id": self.get_argument('cpuid', ''),
            "serial_number": self.get_argument('serial_number', ''),
            "medium": self.get_argument('medium', ''),
            "before": self.get_argument('before', ''),
            "after": self.get_argument('after', ''),
            "adjust": self.get_argument('adjust', 0),
            "create": self.get_argument('create', int(time.time()))
        }

        if not p["before"]:
            self.finish({'code': 1, 'msg': 'the before is missing'})
            return

        if not p["after"]:
            self.finish({'code': 2, 'msg': 'the after is missing'})
            return

        if not p["medium"]:
            self.finish({'code': 3, 'msg': 'the medium is missing'})
            return

        if not p["cpu_id"]:
            self.finish({'code': 4, 'msg': 'the cpu_id is missing'})
            return

        add = float(p["after"]) - float(p["before"]) + float(p["adjust"])
        p["add"] = add
        supply = Supply(**p)
        self.session.add(supply)
        self.session.commit()
        supplyid = supply.id
        self.finish({'code': 0, 'supplyid': supplyid})

    def add_supply_print(self):
        p = {
            "adjust": self.get_argument('adjust', 0),
            "unit_price": self.get_argument('unit_price', ''),
            "operator": self.get_argument('operator', ''),
            "supplier": self.get_argument('supplier', ''),
            "supply": self.get_argument('supply', ''),
            "end_user": self.get_argument('end_user', ''),
            "create": self.get_argument('create', int(time.time()))
        }

        if not p["unit_price"]:
            self.finish({"code": 1, "msg": "the unit_price is missing"})
            return

        if not p["operator"]:
            self.finish({"code": 2, "msg": "the operator is missing"})
            return

        if not p["end_user"]:
            self.finish({"code": 3, "msg": "the end_user is missing"})
            return

        if not p["supply"]:
            self.finish({"code": 4, "msg": "the supply is missing"})
            return

        if not p["supplier"]:
            self.finish({"code": 5, "msg": "the supplier is missing"})
            return

        q = self.session.query(Supply).filter_by(id=p["supply"]).first()
        add = q.add
        add = float(p["adjust"]) + float(add)
        total_cost = float(p["unit_price"]) * add
        total_cost = round(total_cost, 2)
        p["add"] = add
        p["total_cost"] = total_cost
        p["before"] = q.before
        p["after"] = q.after
        p["cpu_id"] = q.cpu_id
        p["medium"] = q.medium
        p["serial_number"] = q.serial_number
        supply_print = SupplyPrint(**p)
        self.session.add(supply_print)
        self.session.commit()
        self.finish({'code': 0})


class MyDeviceApendixHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if not self.get_current_session().corp:
            self.finish({'code': -3, 'msg': u'没有权限'})
            return
        action = self.request.uri.split('/')

        if action[-1] in ["set_attribute"]:
            corp = self.get_current_session().corp
            q = self.session.query(CorpUser).filter_by(corp=corp,
                                                       user=self.current_user.id,
                                                       role=CorpUser.ROLE_ADMIN)

            if not self.session.query(q.exists()).scalar():
                self.finish({'code': -2, 'msg': u'只有企业管理员才权限'})
                return

    def get_query(self):

        corp = self.get_current_session().corp
        q = self.session.query(CorpUser).filter_by(corp=corp,
                                                   user=self.current_user.id,
                                                   role=CorpUser.ROLE_ADMIN)

        if self.session.query(q.exists()).scalar():
            # admin
            sub = self.session.query(CorpDevice.device).filter_by(corp=self.get_current_session().corp)
        else:
            # normal
            sub = self.session.query(UserDevice.device).filter_by(user=self.current_user.id)

        sub = self.session.query(Device.name).filter(Device.id.in_(sub),
                                                       Device.status.in_([Device.STATUS_WARNING, Device.STATUS_NORMAL]))

        q = self.session.query(DeviceAppendix).filter(DeviceAppendix.device_name.in_(sub))
        return q

    def get_device_query(self):
        corp = self.get_current_session().corp
        q = self.session.query(CorpUser).filter_by(corp=corp,
                                                   user=self.current_user.id,
                                                   role=CorpUser.ROLE_ADMIN)

        if self.session.query(q.exists()).scalar():
            # admin
            sub = self.session.query(CorpDevice.device).filter_by(corp=self.get_current_session().corp)
        else:
            # normal
            sub = self.session.query(UserDevice.device).filter_by(user=self.current_user.id)

        sub = self.session.query(Device).filter(Device.id.in_(sub),
                                                     Device.status.in_([Device.STATUS_WARNING, Device.STATUS_NORMAL]))
        return sub

    def list_filter(self, q):

        # 支持名字过滤
        serial_number = self.get_argument('serial_number', '')
        if serial_number:
            q = q.filter(DeviceAppendix.serial_number == serial_number)

        # 支持cpu_id过滤
        device_name = self.get_argument('device_name', '')
        if device_name:
            q = q.filter(DeviceAppendix.device_name == device_name)

        # 支持 id 过滤
        id = self.get_argument('id', '')
        if id:
            q = q.filter(DeviceAppendix.id == id)

        type = self.get_argument('type', '')
        if type:
            q = q.filter(DeviceAppendix.type == type)

        marker = self.get_argument('marker', '')
        if marker:
            q = q.filter(DeviceAppendix.marker == marker)

        advance = self.get_argument('advance','')
        if advance:
            q = q.filter(DeviceAppendix.end_time<DeviceAppendix.advance)
        return q

    def create(self):
        '创建设备附件'
        p = {
            'device_name': self.get_argument('device_name', ''),
            'serial_number': self.get_argument('serial_number', ''),
            'location': self.get_argument('location', ''),
            'range': self.get_argument('range', ''),
            'type': self.get_argument('type', ''),
            'manufacturer': self.get_argument('manufacturer', ''),
            'start_time': self.get_argument('start_time', 0),
            'last_check': int(self.get_argument('last_check', time.time())),
            'check_cycle': int(self.get_argument('check_cycle', 0)),
            'remarks': self.get_argument('remarks', ''),
            'create': self.get_argument('create', int(time.time())),
            'marker': self.get_argument('marker', ''),
            'advance': self.get_argument('advance',30),
            'update': int(time.time())
        }

        q = self.session.query(Device).filter_by(name = p['device_name']).first()
        if not q:
            self.finish({'code': 1, 'msg': u'当前账户不存在此设备'})
            return

        q = self.get_device_query().filter(Device.name == p['device_name']).first()
        if not q:
            self.finish({'code': 1, 'msg': u'当前账户不存在此设备'})
            return

        end_time = p['last_check'] + p['check_cycle']*24*3600-int(time.time())
        p['end_time'] = round(float(end_time)/float(24*3600))

        if not p['location']:
            self.finish({'code': 2, 'msg': u'location 不能为空'})
            return

        if not p['type']:
            self.finish({'code': 3, 'msg': u'type 不能为空'})
            return

        q = self.session.query(DeviceAppendix).filter_by(cpu_id=p['cpu_id'], type=p['type'])
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 4, 'msg': u'该设备附件已创建'})
            return
        else:
            self.session.add(DeviceAppendix(**p))
            self.session.commit()
            self.finish({'code': 0})

    def get_cpu_id(self):
        q = self.session.query(Device).filter(Device.status != Device.STATUS_DELETE).all()
        a = [i.cpu_id for i in q]
        self.finish({'code':0,'data':a})


    def update(self):
        id = self.get_argument('id', '')
        if not id:
            self.finish({'code': 1, 'msg': 'the id is missing'})
            return
        q = self.get_query().filter(DeviceAppendix.id == id)
        obj = q.first()
        map = obj.dict()
        print map

        if 'type' in self.p:
            appenix = self.session.query(DeviceAppendix).filter(DeviceAppendix.cpu_id == map['cpu_id'],DeviceAppendix.type == self.p.type,DeviceAppendix.id!=id)
            if self.session.query(appenix.exists()).scalar():
                self.finish({'code':2,'msg':'the appendix type has been exists'})
                return

        data = {}
        for k in map.keys():
            if (k in self.p) and (k not in ['id','device_name','create','end_time']):
                data[k] = self.p[k]

        var = {}
        for k in ['last_check','check_cycle']:
            if k in data.keys():
                var[k] = data[k]
            else:
                var[k] = map[k]

        end_time = int(var['last_check']) + int(var['check_cycle']) * 24 * 3600 - int(time.time())
        end_time = round(float(end_time)/float(24*3600))
        data['end_time'] = end_time
        data['update'] = int(time.time())
        q.update(data,synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})



    def delete(self):
        '删除附件'
        id = self.get_argument('id', '')
        self.session.query(DeviceAppendix).filter_by(id = id).delete()
        self.session.commit()
        self.finish({'code': 0, 'data': u'ok'})



class DeviceHandler(RestHandler):
    def is_post_method(self, action):
        return action in {'create', 'update', 'delete', 'field_alias_update', 'set_attribute', 'delete_attribute'}

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})

    def get_query(self):
        q = self.session.query(Device).filter(Device.status.in_([Device.STATUS_NORMAL, Device.STATUS_WARNING]))
        return q

    def list_filter(self, q):

        # 支持按企业过滤
        corp = self.get_argument('corp', '')
        if corp:
            sub = self.session.query(CorpDevice.device).filter_by(corp=corp)
            q = q.filter(Device.id.in_(sub))

        # 支持名字过滤
        name = self.get_argument('name', '')
        if name:
            q = q.filter(Device.name.ilike('%' + name + '%'))

        # 支持cpu_id过滤
        cpu_id = self.get_argument('cpu_id', '')
        if cpu_id:
            q = q.filter(Device.cpu_id == cpu_id)

        # 支持 id 过滤
        id = self.get_argument('id', '')
        if id:
            q = q.filter(Device.id == id)

        productkey = self.get_argument('productkey', '')
        if productkey:
            q = q.filter(Device.productkey == productkey)

        user = self.get_argument('user', '')
        if user:
            sub = self.session.query(UserDevice.device).filter_by(user=user)
            q = q.filter(Device.id.in_(sub))

        status = self.get_argument('status', '')
        if status:
            q = q.filter(Device.status == status)
        return q

    def get_option_query(self):
        q = self.session.query(Device.id, Device.name).filter(
            Device.status.in_([Device.STATUS_NORMAL, Device.STATUS_WARNING])).order_by(-Device.id)
        return q

    def create(self):
        p = {
            'cpu_id': self.get_argument('cpu_id', ''),
            'name': self.get_argument('name', ''),
            'create': time.time(),
            'corp': self.get_argument('corp', ''),
            'type': self.get_argument('type', 'normal'),
            'productkey': self.get_argument('productkey', ''),
            'device_name': self.get_argument('device_name', ''),
            'role': self.get_argument('role', '')
        }
        if not p['cpu_id']:
            self.finish({'code': 1, 'msg': u'cpu_id不能为空'})
            return

        if not p['name']:
            self.finish({'code': 2, 'msg': u'name不能为空'})
            return

        if not p['productkey']:
            self.finish({'code': 3, 'msg': u'产品不能为空'})
            return

        if not p['device_name']:
            self.finish({'code': 4, 'msg': u'设备名不能为空'})
            return

        ver = self.session.query(Device).filter_by(device_name=p['device_name'], productkey=p['productkey'])
        if self.session.query(ver.exists()).scalar():
            self.finish({'code': 5, 'msg': u'device_name重复'})
            return

        c_id = self.session.query(Device).filter_by(cpu_id=p['cpu_id'])
        if self.session.query(c_id.exists()).scalar():
            self.finish({'code': 6, 'msg': u'cpu_id重复'})
            return

        if p['corp']:
            q = self.session.query(Corp).filter_by(id=p['corp'], status=Corp.STATUS_NORMAL)
            if not self.session.query(q.exists()).scalar():
                self.finish({'code': 7, 'msg': u'错误的企业id'})
                return

            if not p['role']:
                self.finish({'code': 8, 'msg': u'role 不能为空'})
                return

        pro = self.session.query(ALiProduct).filter_by(productkey=p['productkey']).first()
        if not pro or not pro.field_alias:
            self.finish({'code': 9, 'msg': u'产品不存在或者产品别名未设置'})
            return
        else:

            device = Device(cpu_id=p['cpu_id'], name=p['name'], create=p['create'], type=p['type'],
                            productkey=p['productkey'], device_name=p['device_name'])
            self.session.add(device)
            self.session.flush()

            prod_att = self.session.query(ProductAttribute).filter_by(productkey=pro.id).all()
            for i in range(len(prod_att)):
                p_att = prod_att[i].dict()
                del p_att['id']
                del p_att['productkey']
                p_att['cpu_id'] = p['cpu_id']
                p_att['product'] = 1
                self.session.add(DeviceAttribute(**p_att))
            self.session.flush()

            if p['corp']:
                self.session.add(CorpDevice(corp=p['corp'], device=device.id, create=p['create'], role=p['role']))

            self.session.commit()

            devicename = ('SQD-' + pro.field_alias.upper() + p['device_name']).encode('utf-8')
            addr = sys._getframe().f_code.co_name
            result_json = ALiDeviceService().process_data(p['productkey'], devicename, addr).sync()

            if result_json['Success'] == False:
                self.finish({'code': 1, 'data': result_json})
                return

            self.finish({'code': 0, 'data': device.dict()})

    def delete(self):
        id = self.get_argument('id', '')
        self.session.query(CorpDevice).filter_by(device=id).delete()
        self.get_query().filter_by(status=Device.STATUS_NORMAL, id=id).update({'status': Device.STATUS_DELETE},
                                                                              synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0, 'data': u'ok'})

    def revert(self):
        cpu_id = self.get_argument('cpu_id', '')
        if not cpu_id:
            self.finish({'code': 1, 'msg': 'the cpu_id is missing'})
            return
        q = self.session.query(Device).filter(Device.cpu_id == cpu_id).update({'status': Device.STATUS_NORMAL},
                                                                              synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0, 'msg': u'ok'})

    def update(self):
        id = self.get_argument('id', '')
        if not id:
            self.finish({'code': 1, 'msg': u'id不能为空'})
            return
        try:
            id = int(id)
        except:
            self.finish({'code': 2, 'msg': u'id格式错误'})
            return

        q = self.get_query().filter(Device.status.in_([Device.STATUS_NORMAL, Device.STATUS_WARNING]))
        q = q.filter(Device.id == id)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'设备不存在此id'})
            return

        p = {
            'name': self.get_argument('name', None),
            'cpu_id': self.get_argument('cpu_id', None),
            'device_name': self.get_argument('device_name', None),
            'productkey': self.get_argument('productkey', None),
            'type': self.get_argument('type', None),
        }

        if p['cpu_id']:
            data = self.get_query().filter(Device.cpu_id == p['cpu_id'], Device.id != id)
            if self.session.query(data.exists()).scalar():
                self.finish({'code': 4, 'msg': u'设备已存在此cpu_id:%s' % p['cpu_id']})
                return
            d_att = self.session.query(DeviceAttribute).filter_by(cpu_id=q.first().cpu_id)
            d_att.update({'cpu_id': p['cpu_id']}, synchronize_session=False)
            self.session.commit()

        if p['type'] == 'normal':
            q.update({'create': time.time()}, synchronize_session=False)
            self.session.commit()

        for k in p.keys():
            if p[k] is None:
                del p[k]
        if not p:
            self.finish({'code': 5, 'msg': u'请输入有效的字段名'})
            return
        q.update(p, synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})

    def status(self):
        productkey = self.get_argument('productkey', None)
        deviceid = self.get_argument('device_id', None)

        field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=productkey)
        if not self.session.query(field_alias.exists()).scalar():
            self.finish({'code': 2, 'err': u'产品别名未设置'})
            return
        else:

            field_alias = field_alias.first()
            q = self.get_query().filter(Device.id == deviceid).first()
            if not q:
                self.finish({'code': 3, 'msg': 'th device_id doesnot exists'})
                return
            devicename = ('SQD-' + field_alias[0].upper() + q.device_name).encode('utf-8')

            addr = sys._getframe().f_code.co_name
            result_json = ALiDeviceService().process_data(productkey, devicename, addr).sync()
            if result_json['Success'] == False:
                self.finish({'code': 1, 'data': result_json})
                return
            self.finish({'code': 0, 'data': result_json})

    def choice(self, l):
        return random.choice(l)

    def randnum(self, count=1):
        c = '0123456789'
        s = ''.join([random.choice(c) for x in range(count)])
        return s

    def randpoint(self, a, b):
        return self.randnum(a) + '.' + self.randnum(b)

    def gen_test_data(self):
        id = self.get_argument('id', '')
        if not id:
            self.finish({'code': 1, 'msg': u'id不能为空'})
            return

        cpu_id = self.session.query(Device.cpu_id).filter_by(id=id).scalar()
        create = self.get_argument('create', time.time())

        try:
            create = int(create)
        except:
            create = time.time()

        data = {
            'device_id': id,
            'cpu_id': cpu_id,
            'create': create,
            'devid': 0,
            'inverter_frequency': self.randpoint(3, 4),
            'inverter_current': self.randpoint(2, 2),
            'warn': self.randnum(2),
            'lng': self.randpoint(2, 4),
            'lat': self.randpoint(2, 4),
        }

        for name, n, func in [
            ('weight', 4, lambda: self.randpoint(2, 2)),
            ('height', 4, lambda: self.randpoint(2, 2)),
            ('pressure', 8, lambda: self.randpoint(2, 2)),
            ('diff_pressure', 4, lambda: self.randpoint(2, 2)),
            ('per', 4, lambda: self.randpoint(2, 2)),
            ('voltage', 2, lambda: self.randpoint(1, 2)),
            ('temp', 12, lambda: self.randpoint(2, 2)),
            ('valve', 16, lambda: self.choice(['0', '1'])),
            ('flow', 2, lambda: self.randnum(2)),
            ('dens', 8, lambda: self.randpoint(1, 2)),
            ('vacuum', 4, lambda: self.randpoint(1, 2)),
            ('pump', 2, lambda: self.choice(['0', '1'])),
        ]:
            for i in range(1, n + 1):
                data[name + str(i)] = func()

        day = datetime.datetime.fromtimestamp(create)
        year = str(day.year)[-2:]
        month = '%02d' % day.month

        keys = data.keys()
        keys.sort()
        field = ["`%s`" % f for f in keys]
        values = [":%s" % f for f in keys]
        sql = 'insert into z_device_data_{} ({}) values ({})'.format(year + month, ','.join(field), ','.join(values))
        self.session.execute(sql, data)
        self.session.commit()

        refresh_data = 'select max(z_device_data_{}.create) from z_device_data_{} where device_id={}'.format(
            year + month, year + month, data['device_id'])
        refresh_time = self.session.execute(refresh_data).first()

        self.finish({'code': data, 'refresh_time': refresh_time[0]})

    def field_alias(self):
        cpu_id = self.get_argument('cpu_id', '')
        if not cpu_id:
            self.finish({'code': 1, 'msg': u'cpu_id 不能为空'})
            return

        q = self.session.query(FieldAlias).filter_by(cpu_id=cpu_id)
        if not self.session.query(q.exists()).scalar():
            obj = FieldAlias(cpu_id=cpu_id)
            self.session.add(obj)
            self.session.commit()
        else:
            obj = q.first()

        map = obj.dict()
        del map['id']
        del map['cpu_id']

        self.finish({'code': 0, 'data': {'map': map}})

    def field_alias_update(self):
        cpu_id = self.get_argument('cpu_id', '')
        if not cpu_id:
            self.finish({'code': 1, 'msg': u'cpu_id 不能为空'})
            return

        q = self.session.query(FieldAlias).filter_by(cpu_id=cpu_id)
        if not self.session.query(q.exists()).scalar():
            obj = FieldAlias(cpu_id=cpu_id)
            self.session.add(obj)
            self.session.commit()
        else:
            obj = q.first()

        map = obj.dict()
        data = {}

        for k in map.keys():
            if (k in self.p) and (k not in {'id': 'cpu_id'}):
                data[k] = self.p[k]

        self.session.query(FieldAlias).filter_by(cpu_id=cpu_id).update(data, synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})

    def apply_rule(self):
        '设置规则'

        id = self.get_argument('id', '')
        rule = self.get_argument('rule', '')
        rule = [x.strip() for x in filter(None, rule.split(','))]

        self.session.query(DeviceRule).filter_by(device=id).delete()
        for r in rule:
            self.session.add(DeviceRule(device=id, rule=r))
        self.session.commit()
        self.finish({'code': 0})

    def get_rule(self):
        '获取规则'

        id = self.get_argument('id', '')
        q = self.session.query(DeviceRule.rule).filter_by(device=id)
        obj = self.session.query(Rule).filter(Rule.id.in_(q))
        data = [x.dict() for x in obj.all()]
        self.finish({'code': 0, 'data': data})

    def set_attribute(self):
        '创建属性'
        p = {
            'cpu_id': self.get_argument('cpu_id', ''),
            'code': self.get_argument('code', ''),
            'name': self.get_argument('name', ''),
            'value': self.get_argument('value', ''),
            'edit': self.get_argument('edit', 0),
            'user': self.get_argument('user', 0),
            'type': self.get_argument('type', DeviceAttribute.TYPE_CONF),
        }

        if not p['cpu_id']:
            self.finish({'code': 1, 'msg': u'cpu_id 不能为空'})
            return

        if not p['code']:
            self.finish({'code': 2, 'msg': u'code 不能为空'})
            return

        q = self.session.query(DeviceAttribute).filter_by(cpu_id=p['cpu_id'], code=p['code'])
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'属性已创建'})
            return
        else:
            self.session.add(DeviceAttribute(**p))
            self.session.commit()
            self.finish({'code': 0})

    def update_attribute(self):

        cpu_id = self.get_argument('cpu_id', '')
        data = self.get_argument('data', '')
        key_list = ['name', 'value', 'user', 'type']

        if not cpu_id:
            self.finish({'code': 1, 'msg': u'cpu_id 不能为空'})
            return

        if not data:
            self.finish({'code': 2, 'msg': u'data 不能为空'})
            return

        try:
            data = eval(data)
        except:
            self.finish({'code': 3, 'msg': u'data 数据格式错误'})
            return

        message = {}
        attribute_data = [{'cpu_id': cpu_id}]
        if type(data) == dict:
            a = []
            a.append(data)
            data = a

        for i in data:
            p = {}
            if 'code' not in i.keys():
                self.finish({'code': 4, 'msg': u'code不能为空'})
                return

            if 'value' in i.keys():
                message[i['code']] = i['value']

            for j in key_list:
                if j in i.keys():
                    p[j] = i[j]

            if 'type' in p.keys():
                if p['type'] not in [DeviceAttribute.TYPE_CONF, DeviceAttribute.TYPE_CONT]:
                    self.finish({'code': 5, 'msg': u'输入的type类型错误'})
                    return
            code = i['code']

            q = self.session.query(DeviceAttribute).filter(DeviceAttribute.cpu_id == cpu_id,
                                                           DeviceAttribute.code == code)

            if not self.session.query(q.exists()).scalar():
                self.finish({'code': 6, 'msg': u'该设备不存在此code:%s' % code})
                return

            if q.first().edit != 1:
                self.finish({'code': 7, 'msg': u'此code：%s不可修改' % code})
                return

            if not p:
                self.finish({'code': 8, 'msg': u'请输入正确的属性修改字段'})
                return

            p['code'] = code
            q.update(p, synchronize_session=False)
            attribute_data.append(p)

        if message:
            device = self.session.query(Device).filter_by(cpu_id=cpu_id).first()
            productkey = device.productkey
            dev_name = device.device_name
            field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=productkey).first()
            devicename = ('SQD-' + field_alias[0].upper() + dev_name)
            topicfullname = '/' + productkey + '/' + devicename + '/update'
            message = 'renew:%s' % message

            result_json = ALiMessageService().pub(productkey, topicfullname, message, Qos=1).sync()
            if result_json['Success']:
                self.finish({'code': 0, 'msg': u'设备属性配置成功，发送到aliyun成功', 'data': attribute_data})
                return
            else:
                self.finish({'code': 9, 'msg': u'设备属性配置成功，发送到aliyun 失败'})
                return

        self.finish({'code': 0, 'msg': u'本地设备属性配置成功', 'data': attribute_data})

    def delete_attribute(self):
        '删除一个属性'

        cpu_id = self.get_argument('cpu_id', '')
        code = self.get_argument('code', '')

        if not cpu_id:
            self.finish({'code': 1, 'msg': u'cpu_id 不能为空'})
            return
        if not code:
            self.finish({'code': 1, 'msg': u'code 不能为空'})
            return
        q = self.session.query(DeviceAttribute).filter_by(cpu_id=cpu_id, code=code).delete(synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})

    def get_attribute_list(self):
        '获取属性列表'

        cpu_id = self.get_argument('cpu_id', '')
        code = self.get_argument('code', '')

        if not cpu_id:
            self.finish({'code': 1, 'msg': u'cpu_id 不能为空'})
            return

        q = self.session.query(DeviceAttribute).filter_by(cpu_id=cpu_id)

        if code:
            code_list = [x.strip() for x in filter(None, code.split(','))]
            q = q.filter(DeviceAttribute.code.in_(code_list))

        device_attr = [o.dict() for o in q]

        info = {
            "device_attr": device_attr,
        }

        self.finish({'code': 0, 'data': info})

    def supply_recode(self):
        q = self.session.query(Supply)
        cpu_id = self.get_argument('cpu_id', '')
        if cpu_id:
            q = q.filter(Supply.cpu_id == cpu_id)

        page, per_page = self.get_page_and_per_page()

        medium = self.get_argument('medium', '')
        if medium:
            q = q.filter(Supply.medium.ilike('%' + medium + '%'))

        id = self.get_argument('id', '')
        if id:
            q = q.filter(Supply.id == id)

        q = q.order_by(Supply.create.desc())
        limit = self.get_argument('limit', '')
        if limit:
            q = q.limit(int(limit))
            count = q.count()
            obj = [o.dict() for o in q]
            obj = obj[(page - 1) * per_page:page * per_page]
        else:
            count = q.count()
            q = q.limit(per_page).offset((page - 1) * per_page)
            obj = [o.dict(self.list_defer()) for o in q]

        p = {
            'count': count,
            'page': page,
            'perPage': per_page,
            'itemList': obj
        }
        self.finish({'code': 0, 'data': p})

    def supply_print(self):
        q = self.session.query(SupplyPrint)
        cpu_id = self.get_argument('cpu_id', '')
        if cpu_id:
            q = q.filter(SupplyPrint.cpu_id == cpu_id)

        page, per_page = self.get_page_and_per_page()

        supply = self.get_argument('supply', '')
        if supply:
            q = q.filter(SupplyPrint.supply == supply)

        medium = self.get_argument('medium', '')
        if medium:
            q = q.filter(SupplyPrint.medium.ilike('%' + medium + '%'))

        supplier = self.get_argument('supplier', '')
        if supplier:
            q = q.filter(SupplyPrint.supplier.ilike('%' + supplier + '%'))

        operator = self.get_argument('operator', '')
        if operator:
            q = q.filter(SupplyPrint.operator.ilike('%' + operator + '%'))

        q = q.order_by(SupplyPrint.create.desc())

        limit = self.get_argument('limit', '')
        if limit:
            q = q.limit(int(limit))
            count = q.count()
            obj = [o.dict() for o in q]
            obj = obj[(page - 1) * per_page:page * per_page]
        else:
            count = q.count()
            q = q.limit(per_page).offset((page - 1) * per_page)
            obj = [o.dict(self.list_defer()) for o in q]

        p = {
            'count': count,
            'page': page,
            'perPage': per_page,
            'itemList': obj
        }
        self.finish({'code': 0, 'data': p})

    def add_supply(self):
        p = {
            "cpu_id": self.get_argument('cpuid', ''),
            "serial_number": self.get_argument('serial_number', ''),
            "medium": self.get_argument('medium', ''),
            "before": self.get_argument('before', ''),
            "after": self.get_argument('after', ''),
            "adjust": self.get_argument('adjust', 0),
            "create": self.get_argument('create', int(time.time()))
        }

        if not p["before"]:
            self.finish({'code': 1, 'msg': 'the before is missing'})
            return

        if not p["after"]:
            self.finish({'code': 2, 'msg': 'the after is missing'})
            return

        if not p["medium"]:
            self.finish({'code': 3, 'msg': 'the medium is missing'})
            return

        if not p["cpu_id"]:
            self.finish({'code': 4, 'msg': 'the cpu_id is missing'})
            return

        add = float(p["after"]) - float(p["before"]) + float(p["adjust"])
        p["add"] = add
        supply = Supply(**p)
        self.session.add(supply)
        self.session.commit()
        self.finish({'code': 0})

    def add_supply_print(self):
        p = {
            "adjust": self.get_argument('adjust', 0),
            "unit_price": self.get_argument('unit_price', ''),
            "operator": self.get_argument('operator', ''),
            "supplier": self.get_argument('supplier', ''),
            "supply": self.get_argument('supply', ''),
            "end_user": self.get_argument('end_user', ''),
            "create": self.get_argument('create', int(time.time()))
        }

        if not p["unit_price"]:
            self.finish({"code": 1, "msg": "the unit_price is missing"})
            return

        if not p["operator"]:
            self.finish({"code": 2, "msg": "the operator is missing"})
            return

        if not p["end_user"]:
            self.finish({"code": 3, "msg": "the end_user is missing"})
            return

        if not p["supply"]:
            self.finish({"code": 4, "msg": "the supply is missing"})
            return

        if not p["supplier"]:
            self.finish({"code": 5, "msg": "the supplier is missing"})
            return

        q = self.session.query(SupplyPrint).filter_by(supply=p["supply"]).first()
        if not q:
            q = self.session.query(Supply).filter_by(id=p["supply"]).first()
            add = q.add
            add = float(p["adjust"]) + float(add)
            total_cost = float(p["unit_price"]) * add
            total_cost = round(total_cost, 2)
            p["add"] = add
            p["total_cost"] = total_cost
            p["before"] = q.before
            p["after"] = q.after
            p["cpu_id"] = q.cpu_id
            p["medium"] = q.medium
            p["serial_number"] = q.serial_number
            supply_print = SupplyPrint(**p)
            self.session.add(supply_print)
            self.session.commit()
            self.finish({'code': 0})
        else:
            self.session.query(SupplyPrint).filter_by(supply=p["supply"]).update({"create": int(time.time())})
            self.finish({'code': 0})
