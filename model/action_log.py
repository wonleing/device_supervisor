# -*- coding: utf-8 -*-

from base import BaseModel
from tornado.escape import json_decode
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy



class ActionLog(BaseModel):
    '活动日志'

    __tablename__ = 'action_log'


    TYPE_NONE = 'none'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    create = Column(BigInteger, server_default='0', nullable=False, index=True)
    user = Column(BigInteger, ForeignKey('user.id'), nullable=False, index=True)

    type = Column(String(64), server_default='none', nullable=False, index=True)
    target = Column(Text, default='', nullable=False)
    content = Column(Text, default='', nullable=False)

    user_obj = relationship('User', lazy='joined')


    def extra_attribute(self, obj):
        obj['user_name'] = self.user_obj.name
        obj['desc'] = ''

        path = obj.get('type', None)
        if not path:
            return obj

        arguments = obj.get('target', None)
        if not arguments:
            return obj

        path = path.replace('/api', '')
        
        p = path.split('/')

        action = ''
        resource = ''

        if len(p) == 3:
            action = p[2]
            resource = p[1]

        if len(p) == 2:
            action = p[1]

        if not action and not resource:
            return obj


        action_name = {
            'login': u'登录',
            'logout': u'退出',
            'captcha': u'获取验证码',
            'admin': u'打开管理界面',

            'create': u'创建',
            'delete': u'删除',
            'update': u'修改',
            'read': u'读取',
            'list': u'读取列表',
            'option': u'获取选项',
        }

        resource_name = {
            '': '',
            'me': u'我的信息',
            'session': u'会话',
            'user': u'用户',
            'corp': u'企业',
            'corp-user': u'企业下的用户',
            'device': u'设备',
            'corp-device': u'企业下的设备',
            'system': u'系统',
            'action-log': u'活动日志',
            'my-corp': u'自己的企业',
            'my-corp-user': u'自己的企业下的用户',
            'my-device': u'自己的设备',
            'my-action-log': u'自己的活动日志',
        }

        pre = u'{} 了 {}'.format(action_name.get(action, action), resource_name.get(resource, resource))
        post = []
        try:
            arguments = json_decode(arguments)
        except:
            arguments = {}

        keys = arguments.keys()
        keys.sort()
        for k in keys:
            post.append(u'{}: {}'.format(k, arguments[k]))

        obj['desc'] = u'{}\n{}'.format(pre, '\n'.join(post))

