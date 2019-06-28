# -*- coding: utf-8 -*-

import time
from base import RestHandler
from app.model import User, DevicePackageRecord,Device,ALiProduct,TopicLog,AppUpdate
from app.service.aliyuniot import ALiMessageService,FtpService
import json
class DevicePackageRecordHandler(RestHandler):
    '设备更新包的记录'

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})

    def get_query(self):
        q = self.session.query(DevicePackageRecord)
        return q

    def list_filter(self, q):

        cpu_id = self.get_argument('cpu_id', '')
        if cpu_id:
            q = q.filter_by(cpu_id=cpu_id)

        id = self.get_argument('id', '')
        if id:
            q = q.filter_by(id=id)

        version = self.get_argument('version', '')
        if version:
            q = q.filter_by(version=version)

        url = self.get_argument('url', '')
        if url:
            q = q.filter(DevicePackageRecord.url.ilike('%' + url + '%'))

        type = self.get_argument('type', '')
        if type:
            q = q.filter_by(type=type)

        return q


    def create(self):
        p = {
            'cpu_id': self.get_argument('cpu_id', ''),
            'version': self.get_argument('version', ''),
            'url': self.get_argument('url', ''),
            'size': self.get_argument('size', ''),
            'update': time.time(),
            'user': self.current_user.id,
            'type': self.get_argument('type', ''),
            'remarks': self.get_argument('remarks', ''),
        }

        if p['type'] == 'download':
            if not p['cpu_id']:
                self.finish({'code': 1, 'msg': u'cpu_id 不能为空'})
                return

        if not p['version']:
            self.finish({'code': 2, 'msg': u'version 不能为空'})
            return

        if not p['url']:
            self.finish({'code': 3, 'msg': u'url 不能为空'})
            return

        if not p['size']:
            self.finish({'code': 4, 'msg': u'size 不能为空'})
            return

        if (not p['size'].isdigit()) or int(p['size']) <= 0:
            self.finish({'code': 5, 'msg': u'size 格式错误'})
            return

        if not p['type']:
            self.finish({'code': 6, 'msg': u'type 不能为空'})
            return

        p['url'] = 'bin/'+ p['url']

        if p['type'] == 'upload':
            q = self.session.query(DevicePackageRecord.version).filter_by(version=p['version'],type='upload')
            if self.session.query(q.exists()).scalar():
                self.finish({'code': 7, 'msg': u'版本号重复'})
                return

            if not p['remarks']:
                self.finish({'code': 8, 'msg': u'remarks 不能为空'})
                return

        obj = DevicePackageRecord(**p)
        self.session.add(obj)
        self.session.commit()
        self.finish({'code': 0, 'data': obj.dict()})

    def device_update(self):
        version = self.get_argument('version','')
        device_id = self.get_argument('device_id','')
        if not device_id:
            self.finish({'code':2,'msg':'the device_id is missing'})
            return

        if not version:
            self.finish({'code': 3, 'msg': 'the version is missing'})
            return

        try:
            p = self.session.query(Device).filter_by(id = device_id).first()
            field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=p.productkey).first()
            dev_name = self.session.query(Device.device_name).filter_by(id=device_id).first()
        except:
            self.finish({'code':4,'msg':'the device_id doesnot exists or donot in ALiProduct'})
            return

        devicename = ('SQD-' + field_alias[0].upper() + dev_name[0]).encode('utf-8')
        topicfullname = '/'+ p.productkey +'/' + devicename + '/update'

        q = self.session.query(DevicePackageRecord).filter_by(version=version,type='upload').first()

        if not q:
            self.finish({'code':4,'msg':u'该版本不存在'})
            return

        message = 'updatebin:1,file:' + q.url + ',' + 'version:' + version + ';'

        result_json = ALiMessageService().pub(p.productkey, topicfullname, message, Qos=1).sync()

        if result_json['Success']:
            data = {
                'cpu_id': p.cpu_id,
                'version': version,
                'url': q.url,
                'size': q.size,
                'update': time.time(),
                'user': self.current_user.id,
                'type': 'download'
            }
            obj = DevicePackageRecord(**data)
            self.session.add(obj)
            self.session.commit()
            remarks = ''
            self.TopicMessageRecord(message,topicfullname ,remarks,p.productkey ,devicename)

            self.finish({'code': 0, 'data': result_json})
        else:
            self.finish({'code': 1, 'data': result_json})

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
            'message' : json.dumps(message),
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
        except Exception as e:
            self.finish({'code': 2, 'err':u'数据写入失败'})

    def file_upload(self):
        fileinfo = self.request.files.get("file",None)
        file_name = self.get_argument('file_name','')

        if not fileinfo:
            self.finish({'code': 1, 'msg': u'上传文件不能为空'})
            return

        if not file_name:
            self.finish({'code': 2, 'msg': u'文件名不能为空'})
            return

        fileinfo = self.request.files["file"][0]
        url = '/bin/'+file_name
        q = self.session.query(DevicePackageRecord).filter_by(url=url,type='upload')
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'文件名重复'})
            return

        test = FtpService()
        result = test.upload(fileinfo,file_name).sync()
        if result['code'] == 0:
            self.finish({'code': 0,'msg':u'上传成功'})
        else:
            self.finish({'code': 0,'msg':u'上传失败'})

class AppUpgradeHandler(RestHandler):
    def permission(self):
        action = self.request.uri.split('/')
        if action[-1] != 'check_update':
            if not self.current_user:
                self.finish({'code': -1, 'msg': u'没有权限'})
                return

            if self.current_user.type not in [User.TYPE_ADMIN]:
                self.finish({'code': -1, 'msg': u'没有权限'})
                return

    def get_query(self):
        q = self.session.query(AppUpdate)
        return q

    def list_filter(self, q):
        version = self.get_argument('version', '')
        if version:
            q = q.filter_by(version = version)

        id = self.get_argument('id', '')
        if id:
            q = q.filter_by(id = id)

        url = self.get_argument('url', '')
        if url:
            q = q.filter_by(url = url)

        name = self.get_argument('name','')
        if name:
            q = q.filter(name = name)

        return q.order_by(AppUpdate.time.desc())

    def app_upload(self):

        name = self.get_argument('name', '')
        comment = self.get_argument('comment','')
        userid = self.current_user.id
        version = self.get_argument('version','')
        size = self.get_argument('size',0)
        url = self.get_argument('url','')
        if not name:
            self.finish({'code': 1, 'msg': u'版本名称不能为空'})
            return

        if not version:
            self.finish({'code':2,'msg':u'版本号不能为空'})
            return

        if not url:
            self.finish({'code':3,'msg':u'路径不能为空'})
            return

        if not comment:
            self.finish({'code':4,'msg':u'备注不能为空'})
            return


        p = {
            'version':version,
            'time':time.time(),
            'comment':comment,
            'updater':userid,
            'size':size,
            'url':url,
            'name': name
        }

        appupdate = AppUpdate(**p)
        self.session.add(appupdate)
        self.session.commit()
        self.finish({'code':0,'msg':appupdate.dict()})

    def check_update(self):
        name = self.get_argument('name','')
        cur_version = self.get_argument('version','')
        if not cur_version:
            self.finish({'code':3,'msg':u'版本号不能为空'})
            return

        if not name:
            self.finish({'code':2,'msg':u'版本名称不能为空'})
            return

        newest_version = self.session.query(AppUpdate).filter_by(name = name).order_by(AppUpdate.time.desc()).first()

        if newest_version:
            if cur_version == newest_version.version:
                self.finish({'code': 1, 'msg': u'当前已经是最新版本'})
            else:
                self.finish({'code': 0, 'data': newest_version.dict()})
        else:
            self.finish({'code': 1, 'msg': u'当前已经是最新版本'})

    def update(self):
        id = self.get_argument('id','')
        if not id:
            self.finish({'code':1,'msg':u'id不能为空'})
            return
        p = {
            'version': self.get_argument('version',''),
            'time': time.time(),
            'comment': self.get_argument('comment',''),
            'updater': self.get_argument('updater',''),
            'size': self.get_argument('size',''),
            'url': self.get_argument('url',''),
            'name': self.get_argument('name','')
        }

        for k in p.keys():
            if not p[k]:del p[k]
        try:
            self.get_query().filter_by(id = id).update(p)
            self.finish({'code': 0, 'msg': u'更新成功','data':p})
        except:
            self.finish({'code':1,'msg':u'更新失败'})





