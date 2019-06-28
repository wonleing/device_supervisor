# -*- coding: UTF-8 -*-

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '../..')

from app.config import CONF
URL = CONF.get('agent','url')  + '/aliot'
FTPURL = CONF.get('agent','url')


from base import BaseService


class ALiProductService(BaseService):
    method = 'post'
    url = URL
    base = '/product'

    def create(self,name):
        self.path = '/create'
        self.p = {
            'name': name,
        }
        return self

    def update(self, productkey, productname, productdesc):
        self.path = '/update'
        self.p = {
            'productkey':productkey,
            'productname':productname,
            'productdesc':productdesc
        }
        return self

    def query(self,productkey):
        self.path = '/query'
        self.p = {
            'productkey':productkey
        }
        return self

    def list(self, currentpage, pagesize):
        self.path = '/list'
        self.p = {
            'currentpage':currentpage,
            'pagesize':pagesize
            
        }
        return self


class ALiDeviceService(BaseService):
    method = 'post'
    url = URL
    base = '/device'
    def process_data(self,productkey, devicename,addr):
        handler = [
            'create','query','delete','status','batch_status',
            'disable','enable'
        ]
        if addr in handler:
            self.path = '/' + addr
            self.p = {
                'productkey': productkey,
                'devicename': devicename,
            }
            return self
        else:
            self.path = '/' + addr
            self.p = {
                'productkey': productkey,
            }
            return self

class ALiTopicService(BaseService):
    method = 'post'
    url = URL
    base = '/topic'

    def create(self,productkey,topicshortname,operation):
        self.path = '/create'
        self.p = {
            'productkey':productkey,
            'topicshortname':topicshortname,
            'operation':operation
        }
        return self

    def update(self, topicid, topicshortname, operation):
        self.path = '/update'
        self.p = {
            'topicid': topicid,
            'topicshortname': topicshortname,
            'operation': operation
        }
        return self

    def query(self,productkey):
        self.path = '/query'
        self.p = {
            'productkey': productkey,
        }
        return self

    def delete(self, topicid):
        self.path = '/delete'
        self.p = {
            'topicid': topicid
        }
        return self


class ALiMessageService(BaseService):
    method = 'post'
    url = URL
    base = '/message'

    def pub(self,productkey, topicfullname, messagecontents, Qos):
        self.path = '/pub'
        self.p = {
            'productkey':productkey,
            'topicfullname': topicfullname,
            'message': messagecontents,
            'Qos': Qos
        }
        return self

    def broadcast(self, productkey):
        self.path = '/broadcast'
        self.p = {
            'productkey': productkey
        }
        return self

    def rrpc(self, productkey, devicename):
        self.path = '/broadcast'
        self.p = {
            'productkey': productkey,
            'devicename':devicename
        }
        return self

class ALiShadowService(BaseService):
    method = 'post'
    url = URL
    base = '/shadow'

    def query(self, productkey, devicename,):
        self.path = '/query'
        self.p = {
            'productkey': productkey,
            'devicename':devicename
        }
        return self

    def update(self, productkey, devicename,shadow_message):
        self.path = '/update'
        self.p = {
            'productkey': productkey,
            'devicename':devicename,
            'shadow_message':shadow_message
        }
        return self


class ALiRouteService(BaseService):
    method = 'post'
    url = URL
    base = '/route'


    def create(self, SrcTopic, DstTopicsList):
        self.path = '/create'
        self.p = {
            'SrcTopic': SrcTopic,
            'DstTopicsList': DstTopicsList
        }
        return self

    def query(self, Topic):
        self.path = '/query'
        self.p = {
            'Topic': Topic,
        }
        return self

    def query_reve(self, Topic):
        self.path = 'query_reve'
        self.p = {
            'Topic': Topic,
        }
        return self

    def delete(self, SrcTopic, DstTopicsList):
        self.path = '/delete'
        self.p = {
            'SrcTopic': SrcTopic,
            'DstTopicsList': DstTopicsList
        }
        return self


class FtpService(BaseService):
    method = 'post'
    url = FTPURL
    base = '/ftpupload'

    def upload(self,fileinfo,file_name):
        self.path = '/upload'
        self.p = {
            'file': fileinfo,
            'file_name':file_name,
        }
        return self

if __name__ == '__main__':
    print ALiProductService().create('asfwqe').sync()