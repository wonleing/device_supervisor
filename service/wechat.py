# -*- coding: utf-8 -*-# filename: basic.py

import urllib
import time
import json


from app.config import CONF
from base import BaseService
from basic import Basic

URL = CONF.get('agent','url')

class WeChatService(BaseService):
    method = 'post'
    url = URL + '/wechat'
    base = ''

    # 获取openid 和 session_key
    def get_user_info(self, js_code):
        self.path = '/get_user_info'
        self.p = {
            'js_code': js_code,
        }
        return self

    def temp_send(self,news):
        accessToken = Basic().get_access_token()
        postUrl = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % accessToken
        urlResp = urllib.urlopen(postUrl,news)
        urlResp = json.loads(urlResp.read())
        print urlResp

    def temp_msg(self):
        news = {
            "touser": "o8",
            "template_id": "6S",
            "url": "https://www.baidu.com",
            "data": {
                "first": {"value": "hj"},
                "keyword1": {"value": "巧克力"},
                "keyword2": {"value": "16516516554185"},
                "keyword3": {"value": "65元"},
                "keyword4": {"value": "2017年10月15日"},
                "remark": {"value": "欢迎再次购买！"}
            }
        }

        # o8GV_0bSXP9AX6hqfJdy7tZUeOwM
        news['touser'] = CONF.get('weixin', 'touser')
        news['template_id'] = CONF.get('weixin', 'template_id')
        news['url'] = CONF.get('weixin', 'url')

        news['data']["first"]["value"] = u"恭喜你购买成功！".encode('utf-8')
        news['data']["keyword1"]["value"] = u"SQD设备！".encode('utf-8')
        news['data']["keyword2"]["value"] = u"5165161321513215！".encode('utf-8')
        news['data']["keyword3"]["value"] = u"3500元！".encode('utf-8')
        news['data']["keyword4"]["value"] = u"2017年10月15日".encode('utf-8')
        news['data']["remark"]["value"] = u"欢迎再次购买！".encode('utf-8')

        return news

    # 获取用户基本信息
    def user_info(self, openid):
        accessToken = Basic().get_access_token()
        postUrl = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s" % (accessToken, openid)
        urlResp = urllib.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        return urlResp

    # 批量获取用户信息
    def batch_user_info(self, list):
        accessToken = Basic().get_access_token()
        postUrl = "https://api.weixin.qq.com/cgi-bin/user/info/batchget?access_token=%s" % accessToken
        print list
        urlResp = urllib.urlopen(postUrl, list)
        urlResp = json.loads(urlResp.read())
        return urlResp

    # 获取用户列表
    def user_list(self, next_openid):
        accessToken = Basic().get_access_token()
        postUrl = "https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s&next_openid=%s" % (
        accessToken, next_openid)
        urlResp = urllib.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        return urlResp

    # 设置用户备注名
    def update_remark(self, news):
        accessToken = Basic().get_access_token()
        postUrl = "https://api.weixin.qq.com/cgi-bin/user/info/updateremark?access_token=%s" % accessToken
        urlResp = urllib.urlopen(postUrl, news)
        urlResp = json.loads(urlResp.read())
        return urlResp

    def create_menu(self,news):
        accessToken = Basic().get_access_token()
        postUrl = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % accessToken
        urlResp = urllib.urlopen(postUrl, news)
        urlResp = json.loads(urlResp.read())
        return urlResp

    def query_menu(self):
        accessToken = Basic().get_access_token()
        postUrl = "https://api.weixin.qq.com/cgi-bin/menu/get?access_token=%s" % accessToken
        urlResp = urllib.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        return urlResp


    def delete_menu(self):
        accessToken = Basic().get_access_token()
        postUrl = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=%s" % accessToken
        urlResp = urllib.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        return urlResp