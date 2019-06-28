# -*- coding: utf-8 -*-

import hmac
from hashlib import sha1, md5
from urllib import urlencode
from email.utils import formatdate
from base import BaseService
from tornado.httpclient import HTTPClient, HTTPRequest, AsyncHTTPClient
import json

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '../..')
import time
import base64
from app.config import CONF
import datetime
BUCKET = CONF.get('upyun', 'bucket')
DIR = CONF.get('upyun', 'dir')
OPERATOR = CONF.get('upyun', 'operator')
PASSWORD = CONF.get('upyun', 'password')


class UpyunService(BaseService):

    url = 'http://v1.api.upyun.com'
    base = '/' + BUCKET
    # dir = DIR
    operator = OPERATOR
    password = PASSWORD
    json = False
    raw = False

    def sign(self,name,dir):
        self.method = 'post'
        self.path = '/{}/{}'.format(dir, name)
        method = self.method.upper()
        path = self.base + self.path
        date = formatdate(timeval=None, localtime=False, usegmt=True)
        a = int(time.time())+1800
        info = json.dumps({"bucket": "sqdapp-image", "save-key": "/{}/".format(dir) + str(name), "expiration": a, "date": date})
        p = base64.b64encode(info).strip()

        password = self.password
        s = '&'.join([method, path, date,p])

        s = hmac.new(password, s, sha1).digest()
        s = s.encode('base64').strip()
        return s,p


