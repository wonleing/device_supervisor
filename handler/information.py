#-*-coding:utf-8-*-

import time
from base import RestHandler
from app.model import Information,User

class InformationHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code':-1,'msg':u'没有权限'})
            return
        action = self.request.uri.split('/')
        if action[-1] not in ['list']:
            if self.current_user.type not in [User.TYPE_ADMIN]:
                self.finish({'code':-1,'msg':u'没有权限'})
                return


    def get_query(self):
        q = self.session.query(Information).order_by(Information.id.desc())
        return q

    def create(self):

        createtime = time.time()
        title = self.get_argument('title','')
        picture = self.get_argument('picture','')
        url = self.get_argument('url','')
        p = {
            'time':createtime,
            'title':title,
            'picture':picture,
            'url':url
        }
        if not p['title']:
            self.finish({'code': 1, 'msg': u'title不能为空'})
            return

        if not p['picture']:
            self.finish({'code': 2, 'msg': u'picture不能为空'})
            return

        if not p['url']:
            self.finish({'code': 3, 'msg': u'url不能为空'})
            return

        title = self.session.query(Information).filter_by(title = title).scalar()
        if title:
            self.finish({'code':4,'data':'the title has been exist'})
        try :
            information = Information(title=p['title'], time=p['time'], picture=p['picture'],url=p['url'])
            self.session.add(information)
            self.session.commit()
            self.finish({'code':0,'Sucess':True})
        except Exception as e:
            self.finish({'code': 2, 'err':u'数据写入失败'})

    def delete(self):
        id = self.get_argument('id','')
        if not id:
            self.finish({'code':1,'data':u'id不能为空'})
        try:
            self.session.query(Information).filter_by(id = id).delete()
            self.session.commit()
            self.finish({'code': 0, 'success': True})
        except:
            self.finish({'code': 2, 'data': u'数据delete失败'})


