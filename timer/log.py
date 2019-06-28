# -*- coding: utf-8 -*-

'日志处理'

import os
import datetime
import logging
import tornado.ioloop
from collections import deque

logger = logging.getLogger('app.locallog')
logfile = "/var/log/sqd_timer.log"
class Log(object):

    def __init__(self):
        self.cache = deque()
        self.count = 0

    def dump(self):
        '把cache中的内容写入文件'

        if not self.count:
            #logger.debug('dump 0 msgs')
            self.il.add_timeout(self.il.time() + 10, self.dump)
            return
        with open(logfile, 'a') as f:
            [f.write(self.cache.popleft()) for i in xrange(self.count)]


        logger.debug('dump %s msgs' % self.count)
        self.count = 0
        self.il.add_timeout(self.il.time() + 10, self.dump)


    def write(self, s):
        '为logging提供的接口'

        self.count += 1
        self.cache.append(s)


    def start(self):
        self.il = tornado.ioloop.IOLoop.current()
        self.dump()
