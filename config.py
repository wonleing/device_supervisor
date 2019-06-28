# -*- coding: utf-8 -*-

# 配置文件

import os, imp
cdir = os.path.dirname(__file__)
CONF = imp.load_source('parse_config', os.path.join( cdir, 'lib', 'parse_config.py'),).parse(os.path.join(cdir, 'config.conf'))

# 参数

import tornado.options
from tornado.options import define, options
define("port", default=8888, help=u"指定启动端口", type=int)
tornado.options.parse_command_line()


# 数据库连接

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.pool import AssertionPool

#DBEngine = create_engine('postgresql://', creator=Conn())
p = {
    'drivername': 'mysql',
    'host': CONF.get('database', 'host'),
    'port': CONF.get('database', 'port'),
    'username': CONF.get('database', 'user'),
    'password': CONF.get('database', 'pass'),
    'database': CONF.get('database', 'name'),
    'query': {'charset': 'utf8', 'use_unicode': 1},
}
s = URL(**p)
DBEngine = create_engine(s, poolclass=AssertionPool, pool_recycle=600)
DBSession = sessionmaker(bind=DBEngine)()


# 日志

import logging, sys
from logging import Formatter
from logging import StreamHandler
from logging.handlers import SysLogHandler
from timer.log import Log

logger = logging.getLogger('app')
logger.propagate = False
logger.setLevel(10)



if CONF.getboolean('log:stdout', 'enable'):
    stream_hd = StreamHandler()
    stream_hd.setFormatter(Formatter(CONF.get('log:stdout', 'format'), '%Y-%m-%d %H:%M:%S'))
    stream_hd.setLevel(CONF.getint('log:stdout', 'level'))
    logger.addHandler(stream_hd)

    #Tornado自己的日志
    logging.getLogger('tornado').propagate = False
    access_log = logging.getLogger("tornado.access"); access_log.addHandler(stream_hd)
    app_log = logging.getLogger("tornado.application"); app_log.addHandler(stream_hd)
    gen_log = logging.getLogger("tornado.general"); gen_log.addHandler(stream_hd)

    #Sqlalchey的日志
    if CONF.getboolean('log:stdout', 'sql'):
        logging.getLogger('sqlalchemy').propagate = False
        engine_log = logging.getLogger('sqlalchemy.engine')
        engine_log.setLevel(logging.INFO)
        engine_log.addHandler(stream_hd)


if CONF.getboolean('log:filelog', 'enable'):
    #LocalLog = Log(CONF.get('log:filelog', 'dir'), options.port)
    LocalLog = Log()
    local_hd = StreamHandler(LocalLog)
    local_hd.setFormatter(Formatter(CONF.get('log:stdout', 'format'), '%Y-%m-%d %H:%M:%S'))
    local_hd.setLevel(CONF.getint('log:filelog', 'level'))
    logger.addHandler(local_hd)
    #LocalLog.start()



#JSON化
import json
from decimal import Decimal
from datetime import date
class MyEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, Decimal):
            return obj.to_eng_string()

        if isinstance(obj, date):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)

tornado.escape.json_encode = lambda *args, **kargs: json.dumps(*args, cls=MyEncoder, **kargs)
