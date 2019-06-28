# -*- coding: utf-8 -*-

'把 warn 记录, 生成对应用户的信息和推送'

import sys, os

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

import time
import random
import logging

from tornado.ioloop import IOLoop
from app.model import Telecontrol,DeviceAttribute,Device
from app.config import DBSession, LocalLog, CONF
from app.service.aliyuniot import ALiMessageService
from app.model.aliyuniot import ALiProduct


logger = logging.getLogger('app.timer.telecont')

class Timer(object):

    def __init__(self):
        self.session = DBSession


    def device_pub(self, device,message,id,Qos):
        command = message[:-1]
        message = "command:" + command + ",};"

        dev_q = self.session.query(Device).filter_by(id=device).first()

        productkey = dev_q .productkey
        dev_name = dev_q.device_name

        field_alias = self.session.query(ALiProduct.field_alias).filter_by(productkey=productkey).first()
        devicename = ('SQD-' + field_alias[0].upper() + dev_name).encode('utf-8')

        topicfullname = '/' + productkey + '/' + devicename +'/update'

        result_json = ''
        try:
            result_json = ALiMessageService().pub(productkey, topicfullname, message, Qos).sync()
        except Exception as err:
            logger.error('agent err: {}'.format(id))

        if result_json:
            if result_json['Success']:
                self.session.query(Telecontrol).filter_by(id=id).update({'time': time.time(),'status':'send'}, synchronize_session=False)
                self.session.commit()
                logger.error('pub success, telecontrol id is {}'.format(id))
            else:
                logger.error('pub fail, telecontrol id is {}'.format(id))



    def do(self):
        obj = self.session.query(Telecontrol).filter(Telecontrol.status.in_([Telecontrol.STATUS_FAIL])).all()
        for i in obj:
            if int(time.time()) - i.time > 5*60:
                self.device_pub(i.device_id, i.command,i.id,1)
            else:
                continue

    def run(self):
        logger.info('turn')
        self.session.commit()
        self.session.query('1').all()
        try:
            self.do()
        except:
            logger.error('ERROR')
        IOLoop().current().add_timeout(IOLoop().current().time() + random.randint(5, 10), self.run)
        self.session.commit()


if __name__ == '__main__':
    Timer().run()
    if CONF.getboolean('log:filelog', 'enable'): LocalLog.start()
    IOLoop().current().start()

