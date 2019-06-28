# -*- coding: utf-8 -*-
# filename: handle.py

import time
import json
import hmac
import hashlib
import uuid

from app.model import Passport,User,CorpUser
from app.config import CONF
from base import RestHandler
from app.service.wechat import WeChatService

class WeiXinLoginHandler(RestHandler):
    def permission(self):
        pass

    # 微信登陆接口
    def wx_login(self):
        js_code = self.get_argument('js_code', '')
        openid,session_key =  self.get_user_info(js_code)

        passport = self.session.query(Passport).filter_by(openid=openid).first()
        if not passport:
            self.finish({'code': 1, 'msg': u'用户未绑定'})
            return

        q = self.session.query(User).filter_by(id=passport.user, status=User.STATUS_NORMAL)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 2, 'msg': u'用户状态异常'})
            return

        user = q.first()
        user_uuid = str(uuid.uuid4().hex)  # 暴露给小程序端的用户标示

        corp = None
        a = user.type
        if user.type not in [User.TYPE_ADMIN]:
            corp_user = self.session.query(CorpUser).filter_by(user=user.id, status=CorpUser.STATUS_NORMAL).first()
            if corp_user:
                corp = corp_user.corp

        self.util_wechat_login(user.id,user_uuid,session_key,openid,corp)
        # 微信小程序不能设置cookie，把用户信息存在了 headers 中
        self.set_header('Authorization', user_uuid)
        self.session.query(Passport).filter_by(user=passport.id).update({'login_time':time.time()},synchronize_session=False)
        self.session.commit()
        self.finish({'code':0,'data':{ 'user':user.id,'user_name':passport.username}})

    # 获取openid 和　session_key
    def get_user_info(self,js_code):

        user_info = WeChatService().get_user_info(js_code).sync()

        try:
            openid = user_info['openid']
            session_key = user_info['session_key']
            return openid, session_key
        except Exception as i:
            self.finish({'code':2,'error': user_info['errcode'], 'errmsg': user_info['errmsg']})

    # 绑定微信号
    def wx_login_bind(self):
        username = self.get_argument('username', '')
        password = self.get_argument('password', '')
        js_code = self.get_argument('js_code', '')

        passport = self.session.query(Passport).filter_by(username=username).first()
        if not passport:
            self.finish({'code': 1, 'msg': u'用户名或密码错误'})
            return

        if hmac.new(passport.password[:16].encode('utf8'), password.encode('utf8'),
                    hashlib.sha256).hexdigest() != passport.password[16:]:
            self.finish({'code': 2, 'msg': u'用户名或密码错误'})
            return

        if not js_code:
            self.finish({'code':3,'msg':u'绑定出错'})
            return

        openid, session_key = self.get_user_info(js_code)
        self.session.query(Passport).filter_by(openid=openid).update({'openid': ''})
        self.session.query(Passport).filter_by(username=username).update({'openid': openid})
        self.session.commit()

        q = self.session.query(User).filter_by(id=passport.user, status=User.STATUS_NORMAL)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'用户状态异常'})
            return

        user = q.first()
        user_uuid = str(uuid.uuid4().hex)  # 暴露给小程序端的用户标示

        corp = None
        if user.type not in [User.TYPE_ADMIN]:
            corp_user = self.session.query(CorpUser).filter_by(user=user.id, status=CorpUser.STATUS_NORMAL).first()
            if corp_user:
                corp = corp_user.corp

        self.util_wechat_login(user.id, user_uuid, session_key, openid,corp)

        # 微信小程序不能设置cookie，把用户信息存在了 headers 中
        self.set_header('Authorization', user_uuid)
        self.session.query(Passport).filter_by(user=passport.user).update({'login_time':time.time()},synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0, 'data': {'user': user.id, 'user_name': passport.username}})

class WeChatHandler(RestHandler):
    def permission(self):
        u'登录用户'
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

    # 发送模板消息
    def send(self):
        tempmsg = WeChatService()
        data =tempmsg.temp_msg()
        news = json.dumps(data, ensure_ascii=False)
        print news
        tempmsg.temp_send(news)

        self.finish({'code': 0})

    # 获取用户基本信息
    def user_info(self):
        user = WeChatService()
        touser = 'o8GV_0bSXP9AX6hqfJdy7tZUeOwM'
        data = user.user_info(touser)
        self.finish({'code': 0, 'user_info': data})

    # 批量获取用户信息
    def batch_user_info(self):
        user_list = []
        user_id =dict(
            openid = 'o8GV_0bSXP9AX6hqfJdy7tZUeOwM',

        )
        user_id2 = dict(
            openid='o8GV_0aKptDvIsX7-7Ph92D23P2M',

        )
        user_list.append(user_id)
        user_list.append(user_id2)
        info = {"user_list":user_list}
        news = json.dumps(info, ensure_ascii=False)
        user = WeChatService()
        data = user.batch_user_info(news)
        result = []
        for i in data['user_info_list']:
            data_list ={}
            data_list['nickname'] = i['nickname']
            data_list['openid'] = i['openid']
            data_list['lang'] = i['language']
            result.append(data_list)
        self.finish({'code':0,'user_info': result})

    # 获取用户列表
    def user_list(self):
        user = WeChatService()
        next_openid = ''
        data = user.user_list(next_openid)
        self.finish({'code': 0, 'user_list': data})

     # 设置用户备注名
    def update_remark(self):
        openid = 'o8GV_0bSXP9AX6hqfJdy7tZUeOwM'
        remark = 'yeyu'
        data = dict(
            openid=openid,
            remark=remark
        )
        news = json.dumps(data, ensure_ascii=False)
        user = WeChatService()
        data = user.update_remark(news)
        self.finish({'code': data})


    def create_menu(self):
        name = self.get_argument("name","")
        type1 = self.get_argument("type","")
        key = self.get_argument("key","")

        butt = []
        data = dict(
            type= type1,
            name=name,
            key = key,
        )
        butt.append(data)
        new = {
            "button":butt
        }
        news = json.dumps(new, ensure_ascii=False)
        user = WeChatService()
        data = user.create_menu(new)
        self.finish({'code': 0,'data':data})

