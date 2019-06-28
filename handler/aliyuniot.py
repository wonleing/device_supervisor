# -*- coding: utf-8 -*-
import base64
import sys
import time
from base import RestHandler
from app.model.topic_history import TopicLog
from app.model import ALiProduct,ProductAttribute,Device,DeviceAttribute
from app.model import User
from app.service.aliyuniot import ALiProductService,ALiDeviceService,ALiTopicService,ALiMessageService,ALiShadowService,ALiRouteService


# 产品管理相关
class ALiProductHandler(RestHandler):

    def permission(self):
        u'登录用户'
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return
        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})

    # 调用该接口新建产品
    def create(self):
        name = self.get_argument('name', None).encode('utf-8')
        field_alias = self.get_argument('field_alias', '')
        desc = self.get_argument('desc', '').encode('utf-8')

        if not field_alias:
            self.finish({'code':0,'msg':u'field_alias不能为空'})

        result_json = ALiProductService().create(name).sync()

        if result_json['Success']:
            p = {
                'name': name,
                'field_alias': field_alias,
                'productkey': result_json['ProductInfo']['ProductKey'],
                'create': time.time()
            }
            try:
                product = ALiProduct(**p)
                self.session.add(product)
                self.session.commit()
                self.finish({'code': 0, 'data': result_json})
            except Exception as e:
                self.finish({'code': 2, 'err': e})
        else:
            self.finish({'code': 1, 'data':result_json})


    # 调用该接口修改指定产品的信息
    def update(self):
        productkey = self.get_argument('productkey', None)
        productname = self.get_argument('productname', None)
        productdesc = self.get_argument('productdesc','')

        result_json = ALiProductService().update(productkey,productname,productdesc).sync()

        if result_json['Success']:
            self.finish({'code': 0, 'data': result_json})
        else:
            self.finish({'code': 1, 'data':result_json})

    # 调用该接口查询指定产品的详细信息
    def query(self):
        productkey = self.get_argument('productkey', None)

        result_json = ALiProductService().query(productkey).sync()

        if result_json['Success']:
            self.finish({'code': 0, 'data': result_json})
        else:
            self.finish({'code': 1, 'data':result_json})

    # 调用该接口查看所有产品列表
    def list(self):
        currentpage = self.get_argument('currentpage', 1)
        pagesize = self.get_argument('pagesize', 15)

        result_json = ALiProductService().list(currentpage,pagesize).sync()

        field = self.session.query(ALiProduct.productkey,ALiProduct.field_alias,ALiProduct.id).all()
        if result_json['Success']:
            alias_list = []
            for i in field:
                alias = {}
                alias['ProductKey']=i[0]
                alias['FieldAlias']=i[1]
                alias['id']=i[2]
                alias_list.append(alias)

            b = result_json['Data']['List']['ProductInfo']
            o = []
            for i in b:
                a = i['ProductKey']
                for k in alias_list:
                    e = k['ProductKey']
                    if a == e:
                        i['FieldAlias'] = k['FieldAlias']
                        i['id'] = k['id']
                o.append(i)
            result_json['Data']['List']['ProductInfo'] = o
            self.finish({'code': 0,'data': result_json,})
        else:
            self.finish({'code': 0, 'data': result_json, })

    def set_attribute(self):
        '设置产品属性'
        p = dict(
        productkey = self.get_argument('productkey', ''),
        code = self.get_argument('code', ''),
        name = self.get_argument('name', ''),
        value = self.get_argument('value', ''),
        edit = self.get_argument('edit', 0),
        type = self.get_argument('type',ProductAttribute.TYPE_CONF),
        )

        if not p['productkey']:
            self.finish({'code': 1, 'msg': u'productkey 不能为空'})
            return

        if not p['code']:
            self.finish({'code': 2, 'msg': u'code 不能为空'})
            return

        q = self.session.query(ProductAttribute).filter_by(productkey=p['productkey'], code=p['code'])
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'属性已创建'})
            return
        else:
            pro_att = ProductAttribute(**p)
            self.session.add(pro_att)
        self.session.flush()

        pk = self.session.query(ALiProduct.productkey).filter_by(id=p['productkey'])
        pro_device = self.session.query(Device.cpu_id).filter_by(productkey = pk).all()

        del p['productkey']
        for i in pro_device:


            d_att = self.session.query(DeviceAttribute).filter_by(code=p['code'],cpu_id=i[0])
            p['product'] = 1
            if self.session.query(d_att.exists()).scalar():
                data = {}
                data['cpu_id'] =None
                for k in p:
                    if p[k]: data[k] = p[k]
                del data['cpu_id']

                if p['edit'] == 1:
                    del data['value']
                    data['user']=0
                    d_att.update(data,synchronize_session=False)
                else:
                    data['user']=0
                    d_att.update(data, synchronize_session=False)
            else:
                p['cpu_id'] = i[0]
                self.session.add(DeviceAttribute(**p))

        self.session.commit()

        self.finish({'code': 0})

    def update_attribute(self):
        p = dict(
            productkey=self.get_argument('productkey', ''),
            code=self.get_argument('code', ''),
            name=self.get_argument('name', ''),
            value=self.get_argument('value', ''),
            edit=self.get_argument('edit', None),
            type=self.get_argument_enum('type',[ProductAttribute.TYPE_CONF,ProductAttribute.TYPE_CONT],None)
        )

        if not p['productkey']:
            self.finish({'code': 1, 'msg': u'productkey 不能为空'})
            return

        if not p['code']:
            self.finish({'code': 2, 'msg': u'code 不能为空'})
            return

        q = self.session.query(ProductAttribute).filter_by(productkey=p['productkey'],code = p['code'])
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 3,'msg':u'无该属性'})
            return

        data = {}
        for k in p:
            if p[k]: data[k] = p[k]

        try:
            q.update(data, synchronize_session=False)

            pk = self.session.query(ALiProduct.productkey).filter_by(id=p['productkey'])
            pro_device = self.session.query(Device.cpu_id).filter_by(productkey=pk).all()

            del data['productkey']
            if data['edit'] == '0':
                data['user'] = 0
            else:
                del data['value']

            for i in pro_device:
                self.session.query(DeviceAttribute).filter_by(product=1, code=p['code'], cpu_id=i[0]).update(data, synchronize_session=False)

            self.session.commit()
            self.finish({'code': 0, 'msg': u'修改成功'})
        except Exception as e:
            self.finish({'code': 0, 'msg': u'修改失败'})

    def delete_attribute(self):
        '删除一个属性'
        productkey = self.get_argument('productkey', '')
        code = self.get_argument('code', '')

        if not productkey:
            self.finish({'code': 1, 'msg': u'productkey不能为空'})
            return
        if not code:
            self.finish({'code': 1, 'msg': u'code 不能为空'})
            return

        q = self.session.query(ProductAttribute).filter_by(productkey=productkey, code=code).delete(
            synchronize_session=False)

        pk = self.session.query(ALiProduct.productkey).filter_by(id=productkey)
        pro_device = self.session.query(Device.cpu_id).filter_by(productkey=pk).all()

        for i in pro_device:
            d_att = self.session.query(DeviceAttribute).filter_by(product=1, code=code, cpu_id=i[0]).delete(
            synchronize_session=False)

        self.session.commit()
        self.finish({'code': 0})


    def get_attribute_list(self):
        '获取属性列表'

        productkey = self.get_argument('productkey', '')
        code = self.get_argument('code', '')

        if not productkey:
            self.finish({'code': 1, 'msg': u'productkey 不能为空'})
            return

        q = self.session.query(ProductAttribute).filter_by(productkey=productkey)
        if code:
            q = q.filter_by(code=code)

        q = q.order_by(ProductAttribute.code).all()
        data = [o.dict() for o in q]

        self.finish({'code': 0, 'data': data})

# 设备管理相关
class ALiDeviceHandler(RestHandler):

    def permission(self):
        u'登录用户'
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

    def parse_response(self, res):
        if res['Success']:
            self.finish({'code': 0, 'data': res})
        else:
            self.finish({'code': 1, 'data':res})

    # 用该接口在指定产品下注册设备
    def create(self):
        productkey = self.get_argument('productkey', None)
        devicename = self.get_argument('devicename', None)

        addr = sys._getframe().f_code.co_name
        result_json = ALiDeviceService().process_data(productkey, devicename,addr).sync()
        self.parse_response(result_json)


    # 调用该接口查询指定设备的详细信息
    def query(self):
        productkey = self.get_argument('productkey', None)
        device_id = self.get_argument('device_id', None)
        addr = sys._getframe().f_code.co_name


        field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=productkey).first()
        if not field_alias:
            self.finish({'code':1,'msg':u'无该aliyun产品或者产品别名未设置'})
            return
        dev_name = self.session.query(Device.device_name).filter_by(id=device_id).first()
        if not dev_name:
            self.finish({'code':2,'msg':u'无该设备'})
            return

        devicename = ('SQD-%s%s' % (field_alias[0].upper(), dev_name[0])).encode('utf-8')
        result_json = ALiDeviceService().process_data(productkey, devicename,addr).sync()
        self.parse_response(result_json)

    # 用该接口查询指定产品下的所有设备列表
    def list(self):
        productkey = self.get_argument('productkey', None)

        addr = sys._getframe().f_code.co_name
        result_json = ALiDeviceService().process_data(productkey,'',addr).sync()
        self.parse_response(result_json)

    # 调用该接口删除指定设备。
    def delete(self):
        productkey = self.get_argument('productkey', None)
        devicename = self.get_argument('devicename', None)

        addr = sys._getframe().f_code.co_name
        result_json = ALiDeviceService().process_data(productkey, devicename,addr).sync()
        self.parse_response(result_json)

    # 调用该接口查看指定设备的运行状态
    def status(self):
        productkey = self.get_argument('productkey', None)
        devicename = self.get_argument('devicename', None)
        addr = sys._getframe().f_code.co_name

        result_json = ALiDeviceService().process_data(productkey, devicename,addr).sync()
        self.parse_response(result_json)

    # 调用该接口批量查看同一产品下指定设备的运行状态。
    def batch_status(self):
        productkey = self.get_argument('productkey', None)
        devicename = self.get_argument('devicename', None)
        addr = sys._getframe().f_code.co_name

        result_json = ALiDeviceService().process_data(productkey, devicename,addr).sync()
        self.parse_response(result_json)

    # 调用该接口禁用指定设备
    def disable(self):
        productkey = self.get_argument('productkey', None)
        device_id = self.get_argument('device_id', None)
        addr = sys._getframe().f_code.co_name

        field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=productkey).first()
        if not field_alias:
            self.finish({'code':1,'msg':u'该aliyun产品不存在或者别名未设置'})
            return
        dev_name = self.session.query(Device.device_name).filter_by(id=device_id).first()
        if not dev_name:
            self.finish({'code':2,'msg':u'该设备不存在'})
            return

        devicename = ('SQD-%s%s' %(field_alias[0].upper(),dev_name[0])).encode('utf-8')
        result_json = ALiDeviceService().process_data(productkey, devicename,addr).sync()
        self.parse_response(result_json)

    # 调用该接口解除指定设备的禁用状态，即启用被禁用的设备。
    def enable(self):
        productkey = self.get_argument('productkey', None)
        device_id = self.get_argument('device_id', None)
        addr = sys._getframe().f_code.co_name

        field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=productkey).first()
        if not field_alias:
            self.finish({'code': 2, 'msg': u'该aliyun产品不存在或者别名未设置'})
            return

        dev_name = self.session.query(Device.device_name).filter_by(id=device_id).first()
        if not dev_name:
            self.finish({'code': 3, 'msg': u'该设备不存在'})
            return

        devicename = ('SQD-%s%s' % (field_alias[0].upper(), dev_name[0])).encode('utf-8')
        result_json = ALiDeviceService().process_data(productkey, devicename,addr).sync()
        self.parse_response(result_json)

    # 调用该接口查询指定产品下的设备统计数据。
    def statis_data(self):
        productkey = self.get_argument('productkey', None)
        addr = sys._getframe().f_code.co_name

        result_json = ALiDeviceService().process_data(productkey,'',addr).sync()
        self.parse_response(result_json)

# topic管理相关
class ALiTopicHandler(RestHandler):
    def permission(self):
        u'登录用户'
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

    def parse_response(self, res):
        if res['Success']:
            self.finish({'code': 0, 'data': res})
        else:
            self.finish({'code': 1, 'data': res})

    # 调用该接口为指定产品创建产品Topic类
    def create(self):
        productkey = self.get_argument('productkey', None)
        topicshortname = self.get_argument('topicshortname', None)
        operation = self.get_argument('operation', None)

        result_json = ALiTopicService().create(productkey,topicshortname,operation).sync()
        self.parse_response(result_json)

    # 调用该接口修改指定的产品Topic类。
    def update(self):
        topicid = self.get_argument('topicid', None)
        topicshortname = self.get_argument('topicshortname', None)
        operation = self.get_argument('operation', None)

        result_json = ALiTopicService().update(topicid, topicshortname, operation).sync()
        self.parse_response(result_json)

    # 调用该接口查询指定产品的Topic类
    def query(self):
        productkey = self.get_argument('productkey', None)

        device_id = self.get_argument('device_id', None)

        result_json = ALiTopicService().query(productkey).sync()

        if device_id:
            field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=productkey).first()
            if field_alias:
                dev_name = self.session.query(Device.device_name).filter_by(id=device_id).first()
                devicename = ('SQD-%s%s' %(field_alias[0].upper(),dev_name[0])).encode('utf-8')
                result_json['Data']['devicename'] = devicename
                self.session.commit()

        self.parse_response(result_json)


    # 调用该接口删除指定的Topic类
    def delete(self):
        topicid = self.get_argument('topicid', None)

        result_json = ALiTopicService().delete(topicid).sync()
        self.parse_response(result_json)

# topic 与 消息路由关系相关
class ALiRouteHandler(RestHandler):
    def permission(self):
        u'登录用户'
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

    def parse_response(self, res):
        if res['Success']:
            self.finish({'code': 0, 'data': res})
        else:
            self.finish({'code': 1, 'data': res})

    # 调用该接口新建Topic间的消息路由关系
    def create(self):
        SrcTopic = self.get_argument('srctopic', None)
        DstTopics = self.get_argument('dsttopics', None)
        DstTopicsList=DstTopics.split(',')

        result_json = ALiRouteService().create(SrcTopic, DstTopicsList).sync()
        self.parse_response(result_json)

    # 调用该接口删除指定的Topic路由关系
    def delete(self):
        SrcTopic = self.get_argument('srctopic', None)
        DstTopics = self.get_argument('dsttopics', None)
        DstTopicsList=DstTopics.split(',')

        result_json = ALiRouteService().delete(SrcTopic, DstTopicsList).sync()
        self.parse_response(result_json)

    # 调用该接口查询向指定Topic订阅消息的目标Topic，即指定Topic的路由表。该接口只支持查询用户的Topic。
    def query(self):
        Topic = self.get_argument('topic', None)

        result_json = ALiRouteService().query(Topic).sync()
        self.parse_response(result_json)

    # 调用该接口查询指定Topic订阅的源Topic，即反向路由表。
    def query_reve(self):
        Topic = self.get_argument('topic', None)

        result_json = ALiRouteService().query_reve(Topic).sync()
        self.parse_response(result_json)

# 通信相关
class ALiMessageHandler(RestHandler):
    def permission(self):
        u'登录用户'
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

    # 调用该接口向指定Topic发布消息   返回格式
    def pub(self):
        productkey = self.get_argument('productkey', None)
        topicfullname = self.get_argument('topicfullname', None)
        message = self.get_argument('message', None)
        remarks = self.get_argument('remarks', None)
        devicename = self.get_argument('devicename', None)
        Qos = self.get_argument('Qos', 0)

        result_json = ALiMessageService().pub(productkey, topicfullname, message,Qos).sync()

        if result_json['Success']:
            self.TopicMessageRecord(message, topicfullname, remarks, productkey, devicename)
            self.finish({'code': 0, 'data': result_json})
        else:
            self.finish({'code': 1, 'data': result_json})

    # 调用该接口向指定产品对应的所有Topic发布广播消息。
    def broadcast(self):
        productkey = self.get_argument('productkey', None)

        result_json = ALiMessageService().broadcast(productkey).sync()

        if result_json['Success']:
            self.finish({'code': 0, 'data': result_json})
        else:
            self.finish({'code': 1, 'data':result_json})

    # 调用该接口向指定设备发送请求消息，并同步返回响应
    def rrpc(self):
        productkey = self.get_argument('productkey', None)
        devicename = self.get_argument('deviceName', None)

        result_json = ALiMessageService().rrpc(productkey,devicename).sync()

        if result_json['Success']:
            self.finish({'code': 0, 'data': result_json})
        else:
            self.finish({'code': 1, 'data':result_json})

    def TopicMessageRecord(self,message,topic,remarks,productkey,devicename):
        name = self.session.query(User.name).filter_by(id = self.current_user.id)
        q= self.session.query(TopicLog.messagecount,TopicLog.name).filter_by(topic=topic).all()

        if q:
            messagecount=[q[i].messagecount for i in range(len(q))]
            maxcount=max(messagecount)
            MessageCount = maxcount + 1
        else:
            MessageCount = 1

        p={
            'name' : name,
            'remarks' : remarks,
            'message' : message,
            'messagecount' : MessageCount,
            'topic': topic,
            'productkey' : productkey,
            'updatetime' : time.time(),
            'devicename' : devicename ,
        }

        try :
            topiclog = TopicLog(**p)
            self.session.add(topiclog)
            self.session.commit()
            # self.finish({'code':0,'success':True})
        except Exception as e:
            self.finish({'code': 2, 'err':u'数据写入失败'})


    def list(self):
        devicename = self.get_argument('devicename', None)
        page, per_page = self.get_page_and_per_page()
        q = self.session.query(TopicLog).filter_by(devicename=devicename)
        count = q.count()
        try:
            obj = [o.dict(self.list_defer()) for o in q]
        except:
            self.finish({'code': -2, 'msg': u'出现了错误，可能是排序参数给的不完整'})
            return

        topic_list = []
        for i in obj:
            topic_list.append(i['topic'])
        topic = list(set(topic_list))
        topiccount = {}
        for i in topic:
            q = self.session.query(TopicLog).filter_by(topic=i)
            topiccount[i] = q.count()

        q = q.limit(per_page).offset((page - 1) * per_page)
        obj = [o.dict(self.list_defer()) for o in q]
        p = {
            'count': count,
            'page': page,
            'perPage': per_page,
            'itemList': obj,
            'topiccount': topiccount
        }
        self.finish({'code': 0, 'data': p})


#影子设备#####
class ALiShadowHandler(RestHandler):

    def permission(self):
        u'登录用户'
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

    #调用该接口查询指定设备的影子信息。
    def query(self):
        productkey = self.get_argument('productkey', None)
        devicename = self.get_argument('devicename', None)

        result_json = ALiShadowService().query(productkey,devicename).sync()

        if result_json['Success']:
            # result_json['ShadowMessage'] = json.loads(result_json['ShadowMessage'])
            self.finish({'code': 0, 'data': result_json})
        else:
            self.finish({'code': 1, 'data':result_json})

# 调用该接口修改指定设备的影子信息
    def update(self):
        productkey = self.get_argument('productkey', None)
        devicename = self.get_argument('devicename', None)
        shadow_message = self.get_argument('shadowmessage', None)

        shadow_message = {
            "method":"update",
            "version": 3,
            "state":{
                "desired":{"window":"open","temperature":25},
                "reported":{"id":"3333"}
                    },
                        }

        result_json = ALiShadowService().update(productkey, devicename, shadow_message).sync()

        if result_json['Success']:
            self.finish({'code': 0, 'data': result_json})
        else:
            self.finish({'code': 1, 'data':result_json})
