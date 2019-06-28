# -*- coding: utf-8 -*-

import time
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_decode
from base import RestHandler, BaseHandler, CONF
from app.model import Fact, Metric, CalculateMetric, Dimension, FactResource
from app.model import User, CorpUser
from app.lib import analytics as ays

HOST = CONF.get('clickhouse', 'host')
PORT = CONF.get('clickhouse', 'port')
DATABASE = CONF.get('clickhouse', 'database')
TABLE = CONF.get('clickhouse', 'table')

DATE_COLUMN = 'gmt_date'


class AnalyticsQueryHandler(BaseHandler):
    def check(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'需要登录'})
            return

    def post(self):
        return self.get()

    @gen.coroutine
    def get(self):
        '''
        fact=goodgood
        dimension=date+giie_rie+rurue+jie
        metric=gioe+rjk_fjkd+jire_ire
        calculateMetric=ihdk+jkfd_jke+jkre_jkre
        where=jgkdate~eq~100+kdkd~gt~abdcefg+
        having_metric=
        having_calculate_metric=
        offset=10
        limit=20
        orderBy=jgkdow
        orderDesc=1
        date=2017-08-08+2017-08-12
        '''


        start = time.time()
        fact = self.p.get('fact', '')
        if not fact:
            self.finish({'code': 1, 'msg': u'fact不能为空'})
            return

        q = self.session.query(Fact).filter_by(code=self.p.fact)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 2, 'msg': u'fact错误'})
            return

        dimension = filter(None, self.p.get('dimension', '').split('+'))
        q = self.session.query(Dimension).filter(Dimension.code.in_(dimension), Dimension.status == Dimension.STATUS_NORMAL)
        if q.count() < len(dimension):
            self.finish({'code': 3, 'msg': u'dimension错误'})
            return

        metric = filter(None, self.p.get('metric', '').split('+'))
        q = self.session.query(Metric).filter(Metric.code.in_(metric), Metric.status == Metric.STATUS_NORMAL)
        if q.count() < len(metric):
            self.finish({'code': 4, 'msg': u'metric错误'})
            return

        calculate_metric = filter(None, self.p.get('calculateMetric', '').split('+'))
        q = self.session.query(CalculateMetric).filter(CalculateMetric.code.in_(calculate_metric), CalculateMetric.status == CalculateMetric.STATUS_NORMAL)
        if q.count() < len(calculate_metric):
            self.finish({'code': 5, 'msg': u'calculateMetric错误'})
            return

        if (len(metric) == 0) and (len(calculate_metric) == 0):
            self.finish({'code': 6, 'msg': u'metric和calculateMetric至少需要1个'})
            return

        where = filter(None, self.p.get('where', '').split('+'))

        if self.current_user.type not in [User.TYPE_ADMIN]:

            corp_list = self.session.query(CorpUser.corp).filter_by(user=self.current_user.id).all()
            corp_list = [str(x[0]) for x in corp_list]
            where.append('~'.join(['corp_id', 'in', ','.join(corp_list)]))

        q = self.session.query(Dimension).filter(Dimension.code.in_([x.split('~')[0] for x in where]), Dimension.status == Dimension.STATUS_NORMAL)
        if q.count() < len(where):
            self.finish({'code': 7, 'msg': u'where错误'})
            return

        having_metric = filter(None, self.p.get('havingMetric', '').split('+'))
        q = self.session.query(Metric).filter(Metric.code.in_([x.split('~')[0] for x in having_metric]), Metric.status == Metric.STATUS_NORMAL)
        if q.count() < len(having_metric):
            self.finish({'code': 9, 'msg': u'havingMetric错误'})
            return

        having_calculate_metric = filter(None, self.p.get('havingCalculateMetric', '').split('+'))
        q = self.session.query(CalculateMetric).filter(CalculateMetric.code.in_([x.split('~')[0] for x in having_calculate_metric]),
                                                       CalculateMetric.status == CalculateMetric.STATUS_NORMAL)
        if q.count() < len(having_calculate_metric):
            self.finish({'code': 9, 'msg': u'havingCalculateMetric错误'})
            return


        # 对象转换
        table = self.session.query(Fact.table).filter(Fact.code == fact).scalar()
        query = ays.Query(ays.Fact(table))

        for code in dimension:
            p = self.session.query(Dimension.name, Dimension.column).filter_by(code=code, status=Dimension.STATUS_NORMAL).first()
            query.add_dimension(ays.Dimension(*p))

        for code in metric:
            p = self.session.query(Metric.name, Metric.aggre, Metric.column).filter_by(code=code, status=Metric.STATUS_NORMAL).first()
            query.add_metric(ays.Metric(*p))

        for code in calculate_metric:
            p = self.session.query(CalculateMetric.name, CalculateMetric.expression).filter_by(code=code, status=CalculateMetric.STATUS_NORMAL).first()
            query.add_calculate_metric(ays.CalculateMetric(*p))


        limit = 10
        if self.p.get('limit', None):
            p = self.p.limit
            if p.isdigit():
                p = int(p)
                if p > 0 and p < 3000:
                    limit = p

        query.limit(limit)


        offset = 0
        if self.p.get('offset', None):
            p = self.p.offset
            if p.isdigit():
                p = int(p)
                if p > 0:
                    offset = p

        query.offset(offset)

        order_by = self.p.get('orderBy', '')
        model = None
        if order_by:

            if order_by in dimension:
                p = self.session.query(Dimension.name, Dimension.column).filter_by(code=order_by, status=Dimension.STATUS_NORMAL).first()
                model = ays.Dimension(*p)

            if order_by in metric:
                p = self.session.query(Metric.name, Metric.aggre, Metric.column).filter_by(code=order_by, status=Metric.STATUS_NORMAL).first()
                model = ays.Metric(*p)

            if order_by in calculate_metric:
                p = self.session.query(CalculateMetric.name, CalculateMetric.expression).filter_by(code=order_by, status=CalculateMetric.STATUS_NORMAL).first()
                model = ays.CalculateMetric(*p)

            if model:
                query.order_by(model)

        if self.p.get('orderDesc', '0') == '1':
            query.order_by_desc(True)

        if where:
            group = ays.FilterGroup()
            for d in where:
                code, op, value = d.split('~')
                name, column = self.session.query(Dimension.name, Dimension.column).filter_by(code=code, status=Dimension.STATUS_NORMAL).first()
                group.and_(ays.Filter(name, op, value, column, 'dimension'))
            query.where(group)

        group = ays.FilterGroup()
        if having_metric:
            for d in having_metric:
                code, op, value = d.split('~')
                name, column = self.session.query(Metric.name, Metric.column).filter_by(code=code, status=Metric.STATUS_NORMAL).first()
                group.and_(ays.Filter(name, op, value, column, 'metric'))

        if having_calculate_metric:
            for d in having_calculate_metric:
                code, op, value = d.split('~')
                name, expression = self.session.query(CalculateMetric.name, CalculateMetric.expression).filter_by(code=code, status=CalculateMetric.STATUS_NORMAL).first()
                group.and_(ays.Filter(name, op, value, expression, 'calculate_metric'))

        if group.filter_list:
            query.having(group)

        if self.get_argument('date', ''):
            query.date(DATE_COLUMN, *self.p.date.split('+'))

        query.format('json')
        sql = query.as_sql()
        url = 'http://{}:{}/?database={}'.format(HOST, PORT, DATABASE)

        res = yield gen.Task(AsyncHTTPClient().fetch, url, method='POST', body=sql)
        if res.code != 200:
            self.finish({'code': -1, 'msg': u'服务出错了\n*****\n{}\n*****\n{}'.format(sql, res.body.decode('utf8'))})
        else:
            self.finish({'code': 0, 'data': {
                'sql': sql,
                'clickhouse': json_decode(res.body),
                'time': time.time() - start,
            }})



class AnalyticsHandler(RestHandler):
    def permission(self):
        pass


class FactHandler(AnalyticsHandler):
    def get_query(self):
        q = self.session.query(Fact).filter_by(status=Fact.STATUS_NORMAL)
        return q

    def create(self):
        code = self.get_argument('code', '')
        if not code:
            self.finish({'code': 1, 'msg': u'code 不能为空'})
            return

        table = self.get_argument('table', '')
        if not table:
            self.finish({'code': 2, 'msg': u'table 不能为空'})
            return

        name = self.get_argument('name', code)

        q = self.get_query().filter_by(code=code)
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'重复的 code'})
            return

        p = {
            'code': code,
            'name': name,
            'table': table,
        }
        obj = Fact(**p)
        self.session.add(obj)
        self.session.commit()
        self.finish({'code': 0, 'data': obj.dict()})

    def delete(self):
        code = self.get_argument('code', '')
        self.get_query().filter_by(code=code).update({'status': Fact.STATUS_DELETE}, synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})

    def update(self):
        id = self.get_argument('id', '')
        if not id:
            self.finish({'code': 1, 'msg': u'id 不能为空'})
            return

        p = {}
        for f in ['code', 'name', 'table']:
            if self.p.get(f, ''):
                p[f] = self.p[f]
        if not p:
            self.finish({'code':3,'msg':u'请输入至少一个更新参数'})
            return

        self.get_query().filter_by(id=id).update(p, synchronize_session=False)
        if 'code' in p:
            count = self.get_query().filter_by(code=p['code']).count()
            if count > 1:
                self.session.rollback()
                self.finish({'code': 2, 'msg': u'code 重复'})
                return

        self.session.commit()
        self.finish({'code': 0})


class MetricHandler(AnalyticsHandler):
    def get_query(self):
        q = self.session.query(Metric).filter_by(status=Metric.STATUS_NORMAL)
        return q

    def create(self):
        code = self.get_argument('code', '')
        if not code:
            self.finish({'code': 1, 'msg': u'code 不能为空'})
            return


        name = self.get_argument('name', code)
        column = self.get_argument('column', '')

        if not column:
            self.finish({'code':2 , 'msg': u'column不能为空'})
            return

        q = self.get_query().filter_by(code=code)
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'重复的 code'})
            return

        aggre = self.get_argument('aggre', '')
        if aggre not in Metric.AGGRE_SET:
            self.finish({'code': 4, 'msg': u'错误的聚合函数名'})
            return

        p = {
            'code': code,
            'name': name,
            'column': column,
            'aggre': aggre,
        }
        obj = Metric(**p)
        self.session.add(obj)
        self.session.commit()
        self.finish({'code': 0, 'data': obj.dict()})


    def delete(self):
        code = self.get_argument('code', '')
        code = map(lambda s: s.strip(), filter(None, code.split(',')))
        self.get_query().filter(Metric.code.in_(code)).update({'status': Metric.STATUS_DELETE}, synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})


    def update(self):
        id = self.get_argument('id', '')
        if not id:
            self.finish({'code': 1, 'msg': u'id 不能为空'})
            return

        p = {}
        for f in ['code', 'name', 'column', 'aggre']:
            if self.p.get(f, ''):
                p[f] = self.p[f]

        if ('aggre' in p) and (p['aggre'] not in Metric.AGGRE_SET):
            self.finish({'code': 3, 'msg': u'错误的聚合函数名'})
            return

        if 'code' in p:
            old_code = self.get_query().filter_by(id=id).first().code
            self.session.query(FactResource).filter_by(type=FactResource.TYPE_METRIC, code=old_code).update({'code': p['code']})
            self.session.flush()

        self.get_query().filter_by(id=id).update(p, synchronize_session=False)
        if 'code' in p:
            count = self.get_query().filter_by(code=p['code']).count()
            if count > 1:
                self.session.rollback()
                self.finish({'code': 2, 'msg': u'code 重复'})
                return


        self.session.commit()
        self.finish({'code': 0})


class CalculateMetricHandler(AnalyticsHandler):
    def get_query(self):
        q = self.session.query(CalculateMetric).filter_by(status=CalculateMetric.STATUS_NORMAL)
        return q


    def create(self):
        code = self.get_argument('code', '')
        if not code:
            self.finish({'code': 1, 'msg': u'code 不能为空'})
            return


        name = self.get_argument('name', code)
        expression = self.get_argument('expression', '')

        if not expression:
            self.finish({'code':2 , 'msg': u'expression不能为空'})
            return

        q = self.get_query().filter_by(code=code)
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'重复的 code'})
            return

        p = {
            'code': code,
            'name': name,
            'expression': expression,
        }
        obj = CalculateMetric(**p)
        self.session.add(obj)
        self.session.commit()
        self.finish({'code': 0, 'data': obj.dict()})

    def delete(self):
        code = self.get_argument('code', '')
        code = map(lambda s: s.strip(), filter(None, code.split(',')))
        self.get_query().filter(CalculateMetric.code.in_(code)).update({'status': CalculateMetric.STATUS_DELETE}, synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})


    def update(self):
        id = self.get_argument('id', '')
        if not id:
            self.finish({'code': 1, 'msg': u'id 不能为空'})
            return

        p = {}
        for f in ['code', 'name', 'expression']:
            if self.p.get(f, ''):
                p[f] = self.p[f]

        if 'code' in p:
            old_code = self.get_query().filter_by(id=id).first().code
            self.session.query(FactResource).filter_by(type=FactResource.TYPE_CALCULATE_METRIC, code=old_code).update({'code': p['code']})
            self.session.flush()

        self.get_query().filter_by(id=id).update(p, synchronize_session=False)
        if 'code' in p:
            count = self.get_query().filter_by(code=p['code']).count()
            if count > 1:
                self.session.rollback()
                self.finish({'code': 2, 'msg': u'code 重复'})
                return

        self.session.commit()
        self.finish({'code': 0})


class DimensionHandler(AnalyticsHandler):

    def get_query(self):
        q = self.session.query(Dimension).filter_by(status=Dimension.STATUS_NORMAL)
        return q


    def create(self):
        code = self.get_argument('code', '')
        if not code:
            self.finish({'code': 1, 'msg': u'code 不能为空'})
            return


        name = self.get_argument('name', code)
        column = self.get_argument('column', '')

        if not column:
            self.finish({'code':2 , 'msg': u'column不能为空'})
            return

        q = self.get_query().filter_by(code=code)
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 3, 'msg': u'重复的 code'})
            return


        p = {
            'code': code,
            'name': name,
            'column': column,
        }
        obj = Dimension(**p)
        self.session.add(obj)
        self.session.commit()
        self.finish({'code': 0, 'data': obj.dict()})

    def delete(self):
        code = self.get_argument('code', '')
        code = map(lambda s: s.strip(), filter(None, code.split(',')))
        self.get_query().filter(Dimension.code.in_(code)).update({'status': Dimension.STATUS_DELETE}, synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})


    def update(self):
        id = self.get_argument('id', '')
        if not id:
            self.finish({'code': 1, 'msg': u'id 不能为空'})
            return

        p = {}
        for f in ['code', 'name', 'column']:
            if self.p.get(f, ''):
                p[f] = self.p[f]

        if 'code' in p:
            old_code = self.get_query().filter_by(id=id).first().code
            self.session.query(FactResource).filter_by(type=FactResource.TYPE_DIMENSION, code=old_code).update({'code': p['code']})
            self.session.flush()

        self.get_query().filter_by(id=id).update(p, synchronize_session=False)
        if 'code' in p:
            count = self.get_query().filter_by(code=p['code']).count()
            if count > 1:
                self.session.rollback()
                self.finish({'code': 2, 'msg': u'code 重复'})
                return

        self.session.commit()
        self.finish({'code': 0})


class FactResourceHandler(AnalyticsHandler):
    def get_query(self):
        q = self.session.query(FactResource)
        return q

    def create(self):

        code = self.get_argument('code', '')
        if not code:
            self.finish({'code': 1, 'msg': u'code 不能为空'})
            return

        fact = self.get_argument('fact', '')
        if not fact:
            self.finish({'code': 2, 'msg': u'table 不能为空'})
            return

        type = self.get_argument('type', '')
        if not type:
            self.finish({'code': 3, 'msg': u'type 不能为空'})
            return

        if type not in FactResource.TYPE_SET:
            self.finish({'code': 4, 'msg': u'错误的 type'})
            return

        model = {FactResource.TYPE_DIMENSION: Dimension,
                 FactResource.TYPE_METRIC: Metric,
                 FactResource.TYPE_CALCULATE_METRIC: CalculateMetric}[type]

        q = self.session.query(model).filter_by(code=code, status=model.STATUS_NORMAL)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 5, 'msg': u'错误的 code 或 type'})
            return

        q = self.session.query(FactResource).filter_by(code=code, type=type, fact=fact)
        if self.session.query(q.exists()).scalar():
            self.finish({'code': 6, 'msg': u'code-type-fact 已经存在'})
            return

        p = {
            'type': type,
            'fact': fact,
            'code': code,
        }
        obj = FactResource(**p)
        self.session.add(obj)
        self.session.commit()
        self.finish({'code': 0, 'data': obj.dict()})


    def delete(self):
        id = self.get_argument('id', '')
        self.get_query().filter_by(id=id).delete()
        self.session.commit()
        self.finish({'code': 0})

    def list_filter(self, q):
        fact = self.get_argument('fact', '')
        if fact and fact.isdigit():
            q = q.filter_by(fact=fact)
        return q

