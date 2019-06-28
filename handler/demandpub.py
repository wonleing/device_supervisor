#-*-coding:utf-8-*-
import time
from base import RestHandler
from app.model import DemandPub , SuggestionBack , User

class DemandPubHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        action = self.request.uri.split('/')
        if action[-1] not in ['create']:
            if self.current_user.type not in [User.TYPE_ADMIN]:
                self.finish({'code': -1, 'msg': u'没有权限'})
                return

    def create(self):
        content = self.get_argument('content',None)
        title = self.get_argument('title',None)
        typecode = int(self.get_argument('typecode','0'))
        createtime = int(time.time())
        publisher = self.current_user.name
        type = self.get_argument('type',None)

        if not content:
            self.finish({'code':1,'msg':'the content is missing'})
            return
        if not title:
            self.finish({'code':2,'msg':'the title is missing'})
            return

        if typecode:
            p = {
                'content': content,
                'title': title,
                'time': createtime,
                'type': type,
                'publisher': publisher,
                'process': u'未处理'
            }
            try:
                suggestionback = SuggestionBack(content=p['content'], title=p['title'], time=p['time'], type=p['type'], \
                                  publisher=p['publisher'],process=p['process'])
                self.session.add(suggestionback)
                self.session.commit()
                self.finish({'code': 0, 'Sucess': True})
            except Exception as e:
                self.finish({'code': 3, 'err': '{}'.format(e)})

        else:
            p = {
                'content' : content,
                'title' : title,
                'time' : createtime,
                'type' : type,
                'publisher' :publisher,
                'process' : u'未处理'
               }
            try:
                demandpub = DemandPub(content=p['content'], title =p['title'], time = p['time'], type = p['type'],\
                                  publisher = p['publisher'],process=p['process'])
                self.session.add(demandpub)
                self.session.commit()
                self.finish({'code': 0, 'Sucess': True})
            except Exception as e:
                self.finish({'code': 2, 'err':'{}'.format(e)})

    def get_query(self):
        typecode = int(self.get_argument('typecode', '0'))
        if typecode:
            q = self.session.query(SuggestionBack).order_by(SuggestionBack.id.desc())
        else:
            q = self.session.query(DemandPub).order_by(DemandPub.id.desc())
        return q

    def delete(self):
        id = self.get_argument('id', '')
        typecode = int(self.get_argument('typecode','0'))
        if not id:
            self.finish({'code': 1, 'data': 'the id is missing'})
            return
        try:
            if typecode:
                self.session.query(SuggestionBack).filter_by(id=id).delete()
                self.session.commit()
                self.finish({'code': 0, 'success': True})
            else:
                self.session.query(DemandPub).filter_by(id=id).delete()
                self.session.commit()
                self.finish({'code': 0, 'success': True})
        except:
            self.finish({'code': 2, 'data': u'数据delete失败'})


    def edit(self):

        typecode = int(self.get_argument('typecode','0'))
        id = self.get_argument('id','')

        p ={
            'handler': self.current_user.name,
            'regist':self.get_argument('regist',''),
            'time':int(time.time())
        }

        if not id:
            self.finish({'code':1,'msg':'the id is missing'})
            return

        if p['regist']:
            process = u'已处理'
        else:
            process = u'未处理'

        p['process'] = process

        if not p['regist']:
            del p['regist']

        try:
            if typecode:
                self.session.query(SuggestionBack).filter_by(id=id).update(p)
                self.finish({'code': 0, 'data': 'Sucess'})
            else:
                self.session.query(DemandPub).filter_by(id=id).update(p)
                self.finish({'code':0,'data':'Sucess'})
        except:
            self.finish({'code':1,'data':'failed'})


