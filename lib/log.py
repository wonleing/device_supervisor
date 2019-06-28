# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger('app.visit')

def log_function(self):
    status = self.get_status()

    if status < 400:
        log_method = logger.info
    elif status < 500:
        log_method = logger.warning
    else:
        log_method = logger.error

    request_time = 1000.0 * self.request.request_time()

    rq = self.request
    h = rq.headers

    #有密码时不记录
    for f in ['password', 'old_password']:
        if f in rq.arguments:
            rq.arguments[f] = ['******']

    msg = '|'.join([getattr(self, 'uuid', '')[:8],
                    rq.remote_ip,
                    h.get('Referer', ''),
                    rq.path,
                    rq.method,
                    str(rq.arguments),
                    str(self.get_status()),
                    '%.2f' % request_time,
                    str(self.current_user.id) if self.current_user else '',
                    '$$',
                   ])

    if status < 400:
        log_method(msg)
    else:
        log_method(msg, exc_info=True)

