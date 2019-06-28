# -*- coding: utf-8 -*-# filename: basic.py

import urllib
import json
import time

from base import BaseService

# 微信获取access_token
class Basic(BaseService):

    __accessToken = ''
    __leftTime = 0

    def __real_get_access_token(self):
        appId = "wx19136f6ad8ae9ea1"
        appSecret = "f63d1248f4ebaeef87353bf68962844c"
        postUrl = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (appId, appSecret))
        urlResp = urllib.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())
        self.__accessToken = urlResp['access_token']
        self.__leftTime = urlResp['expires_in']

    def get_access_token(self):
        if self.__leftTime < 10:
            self.__real_get_access_token()
            return self.__accessToken

    def run(self):
        while(True):
            if self.__leftTime > 10:
                time.sleep(2)
                self.__leftTime -= 2
            else:
                self.__real_get_access_token()