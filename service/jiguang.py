# -*- coding: utf-8 -*-

from base import BaseService
from tornado.escape import json_encode
from app.model import Device
from tornado.httpclient import HTTPClient, HTTPRequest, AsyncHTTPClient


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '../..')

from app.config import CONF,DBSession
APP_KEY = CONF.get('jiguang', 'appkey')
SECRET = CONF.get('jiguang', 'secret')


class JiguangService(BaseService):

    url = 'https://api.jpush.cn'
    base = '/v3'
    session = DBSession

    def gen_request(self):
        s = '{}:{}'.format(APP_KEY, SECRET)
        self.headers['Authorization'] = 'Basic {}'.format(s.encode('base64').strip())

        if not self.raw:
            return super(JiguangService, self).gen_request()


        url = '%s%s%s' % (self.url, self.base, self.path)
        body = self.p
        print url, self.method, self.headers, body
        req = HTTPRequest(url, method=self.method.upper(), headers=self.headers, body=body)
        return req


    def push(self, user_id_list, title, content, device_id,validate = False):
        self.path = '/push'
        if validate:
            self.path = '/push/validate'
        self.method = 'post'
        self.raw = True
        self.headers['Content-Type'] = 'application/json'

        device = self.session.query(Device).filter_by(id=device_id).first()
        p = {
            'platform': 'all',
            'audience': {
                'alias': user_id_list,
            },
            'notification': {
                'alert': u'尊敬的用户,您的ID为:%s,设备名为:%s的设备发生%s,请您及时处理！详情请登录用户端查看。【思科德】' % (device_id,device.name,content),
            } 
        }
        if user_id_list is None:
            p['audience'] = 'all'
        else:
            p['audience'] = {
               'registration_id' :user_id_list
            }


        self.p = json_encode(p)
        return self





if __name__ == '__main__':
    print JiguangService().push( [ "4314", "892", "4531" ], u'标题', u'内容', False).sync(),


