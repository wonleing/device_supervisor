# -*- coding: utf-8 -*-

'把 warn 记录, 生成对应用户的信息和推送'

import sys, os

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

import time
import random
import logging
from tornado.ioloop import IOLoop
from app.model import Message, UserMessage, UserDevice, Warn, Device, Push, Sms, User, CorpDevice, CorpUser
from app.config import DBSession, LocalLog, CONF

logger = logging.getLogger('app.timer.warn')

class Timer(object):

    def get_last(self):
        obj = self.session.query(Message).filter_by(type = Message.TYPE_WARN).order_by(-Message.create).first()
        if not obj: return 0
        return obj.create

    def __init__(self):
        self.session = DBSession

    def do(self):
        self.last = self.get_last()
        obj_list = self.session.query(Warn).filter(Warn.create > self.last).order_by(-Warn.create).all()
        for warn in obj_list:
            #先查对应设备的id及人
            if not warn.cpu_id:
                logger.error('no cpu_id, warn id is {}'.format(warn.id))
                continue

            device_id = self.session.query(Device.id).filter_by(cpu_id = warn.cpu_id).scalar()
            if not device_id:
                logger.error('no device map, warn id is {}, cpu_id is {}'.format(warn.id, warn.cpu_id))
                continue

            user_list = self.session.query(UserDevice.user).filter_by(device = device_id).all()
            user_list = [x[0] for x in user_list]
            if not user_list:
                corp_list = self.session.query(CorpDevice.corp).filter_by(device = device_id)
                user_list = self.session.query(CorpUser.user).filter(CorpUser.corp.in_(corp_list),
                                                                CorpUser.role == 'admin').all()
                user_list = [x[0] for x in user_list]


                if not user_list:
                    logger.error('no user map, warn id is {}, cpu_id is {}'.format(warn.id, warn.cpu_id))
                    continue

            user_mobile_map = self.session.query(User.id, User.mobile).filter(User.id.in_(user_list)).all()
            user_mobile_map = dict(user_mobile_map)

            user_regist_id = self.session.query(User.rid).filter(User.id.in_(user_list)).all()
            user_regist_id = [x[0] for x in user_regist_id]
            user_regist_id = [x for x in user_regist_id if x]


            message = Message(type = Message.TYPE_WARN, create=warn.create, title=u'报警消息', content=warn.content)
            push = Push(create=warn.create, title=u'报警消息',device=device_id,content=warn.content, target=','.join(str(x) for x in user_regist_id))
            self.session.add(message)
            self.session.add(push)
            self.session.flush()
            logger.info('add push, push id is {}'.format(push.id))
            for u in user_list:
                um = UserMessage(user=u, message=message.id, update=time.time())
                self.session.add(um)
                self.session.flush()
                logger.info('add user message, warn id is {}, cpu_id is {}, message id is {}, user message id is {}'.format(warn.id, warn.cpu_id, message.id, um.id))

                mobile = user_mobile_map.get(u, '')
                if mobile:
                    sms = Sms(create=time.time(), content=warn.content, target=mobile,device=device_id, type='warn')
                    self.session.add(sms)
                    self.session.flush()
                    logger.info('add sms, warn id is {}, cpu_id is {}, sms id is {}'.format(warn.id, warn.cpu_id, sms.id))

            self.session.commit()


    def run(self):
        logger.info('turn')
        self.session.commit()
        self.session.query('1').all()
        try:
            self.do()
        except:
            logger.error('ERROR', exc_info=True)
        IOLoop().current().add_timeout(IOLoop().current().time() + random.randint(5, 10), self.run)
        self.session.commit()


if __name__ == '__main__':
    Timer().run()
    if CONF.getboolean('log:filelog', 'enable'): LocalLog.start()
    IOLoop().current().start()

