# -*- coding: utf-8 -*-
 

import time
from base import RestHandler

from app.model import UserMessage, Message,User

from sqlalchemy import func

class MyUserMessageHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有登录'})
            return

    def get_query(self):
        q = self.session.query(UserMessage).filter_by(user=self.current_user.id)
        q = q.filter(UserMessage.status.in_([UserMessage.STATUS_NORMAL, UserMessage.STATUS_READED]))
        return q

    def list_filter(self, q):
        status = self.get_argument('status', '')
        if status:
            q = q.filter(UserMessage.status.in_(status.split(',')))
        q = q.order_by(-UserMessage.update)

        type = self.get_argument('type','')
        if type:
            q = q.filter(UserMessage.type == type )

        return q

    def update(self):
        status = self.get_argument('status', '')
        id_list = self.get_argument('id', '')

        if status not in UserMessage.STATUS_MAP:
            self.finish({'code': 1, 'msg': u'缺少status值或status值错误'})
            return

        if not id_list:
            self.finish({'code': 2, 'msg': 'the user_message id is missing'})
            return

        id_list = ['%s' % x.strip() for x in filter(None, id_list.split(','))]
        q = self.get_query().filter(UserMessage.id.in_(id_list))
        q.update({'status':status}, synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0,'msg':u'修改成功'})


class UserMessageHandler(RestHandler):
    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

    def get_query(self):
        q = self.session.query(UserMessage)
        return q

    def list_filter(self, q):
        user = self.get_argument('user','')
        if user:
            q = q.filter(UserMessage.user == user)

        id = self.get_argument('id', '')
        if id:
            q = q.filter(UserMessage.id == id)

        type = self.get_argument('type', '')
        if type:
            q = q.filter(UserMessage.type == type)

        return q

    def create(self):
        title = self.get_argument('title', '')
        content = self.get_argument('content', '')
        user_list = self.get_argument('id', '')
        type= self.get_argument('type','normal')
        cur_time = int(time.time())

        if not content:
            self.finish({'code': 1, 'msg': u'content不能为空'})
            return

        message = Message(create=cur_time, title=title, content=content,type =type)
        self.session.add(message)
        self.session.flush()
        data = []
        if user_list:
            user_list = ['%s' % x.strip() for x in filter(None, user_list.split(','))]
            for user_id in user_list:
                user_message = UserMessage(message=message.id, update=cur_time, user=user_id,type = type)
                self.session.add(user_message)
                self.session.commit()
                data.append(user_message.dict())
            self.finish({'code': 0, 'data': data})
        else:
            q = self.session.query(User.id).all()
            for i in q:
                user_message = UserMessage(message=message.id, update=cur_time, user=i[0],type = type)
                self.session.add(user_message)
                self.session.commit()
                data.append(user_message.dict())
            self.finish({'code': 0, 'data': data})

    def delete_user_message(self):
        id_list = self.get_argument('id', '')
        if not id_list:
            self.finish({'code': 1, 'msg': u'缺少user_message id'})
            return
        id_list = ['%s' %x.strip() for x in filter(None,id_list.split(','))]
        try:
            for x in id_list:
                q = self.get_query()
                q.filter_by(id=x).delete(synchronize_session=False)
                self.session.commit()
            self.finish({'code': 0,'msg':u'删除成功'})
        except:
            self.finish({'code': 2,'msg':u'删除失败'})

    def delete_message(self):
        id_list = self.get_argument('id', '')
        if not id_list:
            self.finish({'code': 1, 'msg': u'缺少id'})
            return
        id_list = ['%s' %x.strip() for x in filter(None,id_list.split(','))]
        try:
            for x in id_list:
                self.get_query().filter_by(message = x).delete(synchronize_session=False)
                q = self.session.query(Message)
                q.filter_by(id=x).delete(synchronize_session=False)
                self.session.commit()
            self.finish({'code': 0,'msg':u'删除成功'})
        except:
            self.finish({'code': 2,'msg':u'删除失败'})

    def query(self):
        user_count =self.session.query(User).count()
        print user_count
        page, per_page = self.get_page_and_per_page()
        q = self.session.query(UserMessage.message.label('message'), Message.create.label('time'),
                               Message.title.label('title'), Message.content.label('content'),
                               User.name.label('name'),User.id.label('id')) \
            .join(Message, Message.id == UserMessage.message) \
            .join(User, UserMessage.user == User.id).subquery()

        sub_q = self.session.query(q.c.message, q.c.title, q.c.content, func.group_concat(q.c.name)
                                   , func.count(q.c.name), q.c.time).group_by(q.c.message).order_by(-q.c.time)

        user_name  = self.get_argument('name','')
        if user_name :
            sub_q = sub_q.filter(q.c.name == user_name)

        id = self.get_argument('id','')
        if id:
            id = [x.strip() for x in filter(None, id.split(','))]
            sub_q = sub_q.filter(q.c.id.in_(id))

        sub_q = sub_q.limit(per_page).offset((page - 1) * per_page)
        sub_q = sub_q.all()
        data = []
        count = 0
        for n in sub_q:

            if user_count == n[4] or user_name or id:
                count += 1
                data_list = {
                    'message': n[0],
                    'title': n[1],
                    'content': n[2],
                    'user_list': n[3],
                    'user_count': n[4],
                    'create': n[5]
                }
                data.append(data_list)

        p = {
            'count': count,
            'page': page,
            'perPage': per_page,
            'itemList': data
        }
        self.finish({'code': 0, 'data': p})

    def update_message(self):
        id_list = self.get_argument('id','')
        status = self.get_argument('status','')

        if not id_list:
            self.finish({'code':1,'msg':'the message id is missing'})
            return

        if status not in Message.STATUS_MAP:
            self.finish({'code': 2, 'msg': u'缺少status值或status值错误'})
            return

        id_list = ['%s' % x.strip() for x in filter(None, id_list.split(','))]
        q = self.session.query(Message).filter(Message.id.in_(id_list))
        q.update({'status': status}, synchronize_session=False)
        q = self.get_query().filter(UserMessage.message.in_(id_list))
        q.update({'status':status},synchronize_session = False)
        self.session.commit()
        self.finish({'code': 0, 'msg': u'修改成功'})

    def update_user_message(self):
        id_list = self.get_argument('id', '')
        status = self.get_argument('status', '')

        if not id_list:
            self.finish({'code': 1, 'msg': 'the user_message id is missing'})
            return

        if status not in UserMessage.STATUS_MAP:
            self.finish({'code': 2, 'msg': u'缺少status值或status值错误'})
            return

        id_list = ['%s' % x.strip() for x in filter(None, id_list.split(','))]
        q = self.get_query().filter(UserMessage.id.in_(id_list))
        q.update({'status': status}, synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0, 'msg': u'修改成功'})


            

