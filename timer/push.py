# -*- coding: utf-8 -*-

'把 push 记录调用服务推送出去'

import sys, os

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

import time
import random
import logging
from tornado.ioloop import IOLoop
from app.model import Push,User
from app.config import DBSession, LocalLog, CONF
from app.service.jiguang import JiguangService

logger = logging.getLogger('app.timer.push')


class Timer(object):

    def __init__(self):
        self.session = DBSession

    def fail(self):
        '超过10分钟的算失败'

        now = int(time.time())
        self.session.query(Push).filter_by(status=Push.STATUS_NORMAL).filter(Push.create <= (now - 60 * 10)).update({'status': Push.STATUS_FAIL, 'last': now}, synchronize_session=False)
        self.session.commit()

    def push(self, push):
        if push.target.split(','):
            JiguangService().push(push.target.split(','), push.title, push.content, push.device).sync()

    def do(self):
        all_push = self.session.query(Push).filter_by(status=Push.STATUS_NORMAL).all()
        now = int(time.time())
        for p in all_push:
            try:
                self.push(p)
            except:
                self.session.query(Push).filter_by(id=p.id).update({'last': now}, synchronize_session=False)
                self.session.commit()
                logger.error('PUSH ERROR', exc_info=True)
            else:
                self.session.query(Push).filter_by(id=p.id).update({'status': Push.STATUS_COMPLETE, 'last': now}, synchronize_session=False)
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
