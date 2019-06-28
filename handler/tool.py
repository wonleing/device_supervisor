# -*- coding: utf-8 -*-

import uuid
import tornado.web
import tornado.gen
from base import BaseHandler,RestHandler
from app.model import Passport
from app.service.upyun import UpyunService
from app.config import CONF
BUCKET = CONF.get('upyun', 'bucket')
DIR = CONF.get('upyun', 'dir')
DOMAIN = CONF.get('upyun', 'domain')


class ToolHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

    def send_sign(self):
        name = self.get_argument('name','')
        dir = self.get_argument('dir', '')
        result = UpyunService().sign(name,dir)
        p=dict(
            Authorization = result[0],
            p = result[1],
        )
        self.finish({'code':0,'data':p})




