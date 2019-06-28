# -*- coding: utf-8 -*-

import urllib
from base import BaseHandler
from tornado.escape import json_decode
import tornado.web
import tornado.gen
from tornado.httpclient import AsyncHTTPClient
from app.config import CONF

HOST = CONF.get('clickhouse', 'host')
PORT = CONF.get('clickhouse', 'port')
DATABASE = CONF.get('clickhouse', 'database')
TABLE = CONF.get('clickhouse', 'table')

class RealdataHandler(BaseHandler):

    @tornado.gen.engine
    def run_sql(self, sql, callback):
        url = 'http://{}:{}/'.format(HOST, PORT)
        p = {
            'database': DATABASE,
            'query': sql + ' FORMAT JSON',
        }
        url = url + '?' + urllib.urlencode(p)
        res = yield tornado.gen.Task(AsyncHTTPClient().fetch, url)
        callback(json_decode(res.body))

    @tornado.gen.coroutine
    def get(self):
        res = yield tornado.gen.Task(self.run_sql, 'select count() as count from {}'.format(TABLE))
        sum_count = int(res['data'][0]['count'])

        count = self.get_argument('count', None)
        render = self.get_argument('render', None)

        if count:
            try:
                count = int(count)
            except:
                count = 0

            if count and count < sum_count:
                sample = float(count) / sum_count
                sql = 'select * from {} sample {} order by gmt'.format(TABLE, sample)
                res = yield tornado.gen.Task(self.run_sql, sql)
                if render:
                    self.render('realdata.html', data=res)
                else:
                    self.finish(res)
                return

        page = self.get_argument('page', '1')

        try:
            page = int(page)
        except:
            page = 1

        per_page = self.get_argument('perPage', '100')
        try:
            per_page = int(per_page)
        except:
            per_page = 100

        sql = 'select * from {} order by gmt limit {},{}'.format(TABLE, per_page * (page-1), per_page)
        res = yield tornado.gen.Task(self.run_sql, sql)

        if render:
            self.render('realdata.html', data=res)
        else:
            self.finish(res)


