#-*-coding:utf-8-*-
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '../..')

from base import BaseService
from app.config import CONF
URL = CONF.get('agent','url')

class MailService(BaseService):
    url = URL
    method = 'post'
    base = '/sendmail'

    def send(self,receivers,content,files,subject = ''):
        self.path = '/send'
        self.p = {
            'content' : content,
            'receivers' : receivers,
            'files' : files,
            'subject':subject
        }
        return self
