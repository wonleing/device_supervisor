# -*- coding: utf-8 -*-

import time
from base import BaseHandler
from app.lib.captcha import captcha
from app.model import Session


class CaptchaHandler(BaseHandler):
    def get(self):
        char, buff = captcha.gen()
        self.set_header('content-type', 'image/jpeg')
        self.write(buff.read())
        del buff

        session = self.util_get_session()
        self.session.query(Session).filter_by(id=session.id)\
                    .update({'code': char, 'code_create': time.time()},
                            synchronize_session=False)
        self.session.commit()
        self.finish()

