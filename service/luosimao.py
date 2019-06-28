 # -*- coding: utf-8 -*-


from base64 import b64encode
from base import BaseService
from app.model import Device

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '../..')

from app.config import CONF,DBSession
KEY = CONF.get('luosimao', 'key')

class LuoSiMao(BaseService):
    method = 'post'
    url = 'https://sms-api.luosimao.com'
    base = '/v1'
    key = KEY
    session = DBSession


    def gen_request(self):
        self.headers['Authorization'] = 'Basic ' + b64encode('api:key-%s' % self.key)
        return super(LuoSiMao, self).gen_request()

    def send(self, to, data):
        self.path = '/send.json'
        self.p = {
            'mobile': to,
            'message': u'尊敬的用户:您的校验码:%s，工作人员不会索取,请勿泄露。【思科德】' % data,
        }
        self.p['message'] = self.p['message'].encode('utf8')
        return self

    def send_warn(self, to, device_id, data):
        self.path = '/send.json'
        device = self.session.query(Device).filter_by(id = device_id).first()
        self.p = {
            'mobile': to,
            'message': u'尊敬的用户,您的ID为:%s,CPU_ID为:%s,设备名为:%s的设备发生%s,请您及时处理！详情请登录用户端查看。【思科德】' % (device_id, device.cpu_id,device.name,data),
        }
        self.p['message'] = self.p['message'].encode('utf8')
        return self


if __name__ == '__main__':
    #print LuoSiMao().send_reg_code('13699190145', '12343').sync()
    print LuoSiMao().send_warn('13699190145', '123', u'温度过高').sync()

