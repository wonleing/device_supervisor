# -*- coding: utf-8 -*-


import os, sys, imp

CURRENT_PATH = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(CURRENT_PATH, '..')))

import tornado.web
import tornado.httpserver
import tornado.ioloop
from app.config import CONF, LocalLog
from app.url import Handlers
from app.lib.log import log_function as _log_function

class Application(tornado.web.Application):
    def __init__(self, handlers):
        settings = dict(
            cookie_secret = CONF.get('general', 'key'),
            xsrf_cookies = CONF.getboolean('general', 'xsrf_cookies'),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            template_path = os.path.join(os.path.dirname(__file__), "template"),
            log_function = _log_function,
            debug = CONF.getboolean('general', 'debug'),
        )
        super(Application, self).__init__(handlers, '', None, **settings)

class HTTPServer(tornado.httpserver.HTTPServer):
    def __init__(self, app):
        super(HTTPServer, self).__init__(app, xheaders=True)

def main():
    from tornado.options import options
    application = Application(Handlers)
    server = HTTPServer(application)
    server.listen(options.port)
    if CONF.getboolean('log:filelog', 'enable'): LocalLog.start()
    print 'SERVER IS STARTING ON %s ...' % options.port
    tornado.ioloop.IOLoop().current().start()

if __name__ == '__main__':
    main()
