# -*- coding: utf-8 -*-


from urllib import urlencode
import tornado.gen
from tornado.escape import json_decode
from tornado.httpclient import HTTPClient, HTTPRequest, AsyncHTTPClient



class BaseService(object):
    method = 'get'
    url = 'http://localhost:8888'
    base = ''
    headers = {}
    json = True

    def __init__(self):
        pass

    def gen_request(self):

        p = self.p.copy()
        for k in p:
            if type(p[k]) in [unicode]:
                p[k] = p[k].encode('utf8')

        if self.method in ['get', 'head']:
            url = '%s%s%s?%s' % (self.url, self.base, self.path, urlencode(p))
            body = None
        else:
            url = '%s%s%s' % (self.url, self.base, self.path)
            body = urlencode(p)

        if self.method == 'post' and 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded'


        req = HTTPRequest(url, method=self.method.upper(), headers=self.headers, body=body)
        return req


    def parse_response(self, res):
        if self.json:
            return json_decode(res.body)
        else:
            return res


    def sync(self):
        req = self.gen_request()
        res = HTTPClient().fetch(req)
        res = self.parse_response(res)
        return res


    @tornado.gen.engine
    def async(self, callback):
        req = self.gen_request()
        res = yield tornado.gen.Task(AsyncHTTPClient().fetch, req)
        res = self.parse_response(res)
        callback(res)


