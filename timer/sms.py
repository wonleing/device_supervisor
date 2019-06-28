# -*- coding: utf-8 -*-

'把 sms 记录调用服务推送出去'

import sys, os

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

import time
import random
import logging
from tornado.ioloop import IOLoop
from app.model import Sms
from app.config import DBSession, LocalLog, CONF
from app.service.luosimao import LuoSiMao

logger = logging.getLogger('app.timer.push')


class Timer(object):

    def __init__(self):
        self.session = DBSession

    def fail(self):
        '超过10分钟的算失败'

        now = int(time.time())
        self.session.query(Sms).filter_by(status=Sms.STATUS_NORMAL).filter(Sms.create <= (now - 60 * 10)).update({'status': Sms.STATUS_FAIL, 'last': now}, synchronize_session=False)
        self.session.commit()

    def send(self, sms):
        return LuoSiMao().send(sms.target, sms.content).sync()

    def send_warn(self,sms):
        return LuoSiMao().send_warn(sms.target,sms.device,sms.content).sync()


    def do(self):
        all_sms = self.session.query(Sms).filter_by(status=Sms.STATUS_NORMAL).all()
        now = int(time.time())
        for s in all_sms:
            try:
                if s.type == 'warn':
                    res = self.send_warn(s)
                else:
                    res = self.send(s)
            except:
                self.session.query(Sms).filter_by(id=s.id).update({'last': now}, synchronize_session=False)
                self.session.commit()
                logger.error('SEND ERROR', exc_info=True)
            else:
                if res['error'] == 0:
                    self.session.query(Sms).filter_by(id=s.id).update({'status': Sms.STATUS_COMPLETE, 'last': now}, synchronize_session=False)
                else:
                    self.session.query(Sms).filter_by(id=s.id).update({'last': now}, synchronize_session=False)

                self.session.commit()


    def run(self):
        logger.info('turn')
        self.session.commit()
        self.session.query('1').all()
        try:
            self.fail()
            self.do()
        except:
            logger.error('ERROR', exc_info=True)
        IOLoop().current().add_timeout(IOLoop().current().time() + random.randint(5, 10), self.run)
        self.session.commit()



if __name__ == '__main__':
    Timer().run()
    if CONF.getboolean('log:filelog', 'enable'): LocalLog.start()
    IOLoop().current().start()
