# -*- coding: utf-8 -*-

'多维数据查询'

import datetime

class Filter(object):
    '过滤器'

    def __init__(self, name, op, value, column, type='dimension'):
        self.name = name
        self.op = op
        self.value = value
        self.type = type
        self.column = column


class FilterGroup(object):
    '过滤器组'

    def __init__(self, filter=None):
        self.filter_list = []
        self.op_list = []
        if filter:
            self.and_(filter)

    def and_(self, filter):
        self.op_list.append('AND')
        self.filter_list.append(filter)

    def or_(self, filter):
        self.op_list.append('OR')
        self.filter_list.append(filter)

    def as_expression(self, dimension_name_set=set([]), metric_name_set=set([])):
        r = []
        sum_set = dimension_name_set | metric_name_set
        for s, o in zip(self.filter_list, self.op_list):
            r.append(o)

            if s.op not in {'in'}:
                if s.type == 'dimension':
                    r.append(u"(`{}` {} '{}')".format(s.name if s.name in sum_set else s.column, s.op, s.value))
                elif s.type == 'metric':
                    r.append(u"(`{}` {} '{}')".format(s.name if s.name in sum_set else s.column, s.op, s.value))
                else:
                    r.append(u"({} {} {})".format(s.name if s.name in sum_set else s.column, s.op, s.value))
            else:
                if s.type == 'dimension':
                    r.append(u"(`{}` {} ({}))".format(s.name if s.name in sum_set else s.column, s.op,
                                                      ','.join("'%s'" % x for x in s.value.split(',')) ))
                elif s.type == 'metric':
                    r.append(u"(`{}` {} ({}))".format(s.name if s.name in sum_set else s.column, s.op,
                                                      ','.join("'%s'" % x for x in s.value.split(',')) ))
                else:
                    r.append(u"({} {} ({}))".format(s.name if s.name in sum_set else s.column, s.op, s.value))

        r.pop(0)
        return ' '.join(r)


class Fact(object):
    '事实表'

    def __init__(self, table):
        self.table = table


class Metric(object):
    '指标'

    def __init__(self, name, aggre, column):
        self.name = name
        self.aggre = aggre
        self.column = column


class CalculateMetric(object):
    '复合指标'

    def __init__(self, name, expression):
        self.name = name
        self.expression = self.__class__.transform(expression)

    @classmethod
    def transform(self, expression):
        token = expression.split(u' ')
        r = []
        for t in token:
            if t not in {u'+' , u'-', u'*', u'/'}:
                r.append(u'`{}`'.format(t))
            else:
                r.append(t)

        return ' '.join(r)


class Dimension(object):
    '维度'

    def __init__(self, name, column):
        self.name = name
        self.column = column



class Query(object):
    def __init__(self, fact):
        self.fact = fact
        self.dimension = []
        self.metric = []
        self.calculate_metric = []
        self.offset_number = 0
        self.limit_number = 0
        self.format_str = ''
        self.order_by_str = ''
        self.order_by_desc_str = False
        self.where_group = None
        self.having_group = None
        self.date_column = None
        self.date_start = None
        self.date_end = None

    def date(self, column, start, end):
        self.date_column = column
        self.date_start = start
        self.date_end = end

    def offset(self, n):
        self.offset_number = n

    def limit(self, n):
        self.limit_number = n

    def order_by(self, obj):
        self.order_by_str = u'`{}`'.format(obj.name)

    def order_by_desc(self, s):
        self.order_by_desc_str = bool(s)

    def format(self, s):
        self.format_str = s.upper()

    def add_dimension(self, dimension):
        self.dimension.append(dimension)

    def add_metric(self, metric):
        self.metric.append(metric)

    def add_calculate_metric(self, calculate_metric):
        self.calculate_metric.append(calculate_metric)

    def where(self, filter_group):
        self.where_group = filter_group

    def having(self, filter_group):
        self.having_group = filter_group

    def date_where(self):
        if (not self.date_start) or (not self.date_end) or (not self.date_column):
            return u"(`gmt_date` >= '{}')".format((datetime.datetime.today() - datetime.timedelta(days=6)).isoformat().split('T', 1)[0])

        date_s = self.date_column
        for o in self.dimension:
            if(o.column == self.date_column):
                date_s = o.name

        return u"(`{}` >= '{}') AND (`{}` <= '{}')".format(date_s, self.date_start, date_s, self.date_end)


    def as_sql(self):
        dimension_list = [u'`{}` AS `{}`'.format(o.column, o.name) for o in self.dimension]
        metric_list = [u'{}({}) AS `{}`'.format(o.aggre, o.column, o.name) for o in self.metric]
        calculate_metric_list = [u'{} AS `{}`'.format(o.expression, o.name) for o in self.calculate_metric]

        dimension_name_list = [u'`{}`'.format(o.name) for o in self.dimension]

        dimension_name_set = set(o.name for o in self.dimension)
        metric_name_set = set(o.name for o in self.metric) | set(o.name for o in self.calculate_metric)

        sql = [
            u'SELECT\n{}'.format( u',\n\n'.join( filter(None, [u', '.join(dimension_list),
                                                  u', '.join(metric_list),
                                                  u', '.join(calculate_metric_list)])) ),
            u'\nFROM {}'.format(self.fact.table),
            u'WHERE {}{}'.format(self.date_where(),
                                 u' AND ({})'.format(self.where_group.as_expression(dimension_name_set, metric_name_set)) if self.where_group else ''),
            u'GROUP BY {}'.format( u', '.join(dimension_name_list) ),
            u'HAVING {}'.format(self.having_group.as_expression(dimension_name_set, metric_name_set)) if self.having_group else '',
            self.order_by_str and u'ORDER BY {} {}'.format(self.order_by_str, 'DESC' if self.order_by_desc_str else '') or '',
            (self.limit_number) > 0 and (u'LIMIT {},{}'.format(self.offset_number, self.limit_number) \
                   if self.offset_number > 0 else u'LIMIT {}'.format(self.limit_number)) or '',
            u'FORMAT {}'.format(self.format_str) if self.format_str else '',
        ]

        return u'\n'.join(filter(None, sql))


if __name__ == '__main__':
    fact = Fact('monitor_v1')
    query = Query(fact)

    query.add_dimension(Dimension(u'日期', 'gmt_date'))

    query.add_metric(Metric(u'最高环境温度', 'max', 'env_temp'))
    query.add_metric(Metric(u'总流量', 'sum', 'flow'))
    query.add_metric(Metric(u'设备量', 'count', 'cpuid'))

    query.add_calculate_metric(CalculateMetric(u'平均流量', u'总流量 / 设备量'))

    query.order_by(Dimension(u'日期', 'gmt_date'))
    query.order_by_desc(True)

    f1 = Filter(u'总流量', '>', 20000, 'll', 'metric')
    f2 = Filter(u'日期', '=', 'gmt_date', '2017-07-24')
    f3 = Filter(u'最大流量', '<', 100, '123', 'metric')
    f4 = Filter(u'企业ID', 'in', '123,234,22', 'corp_id', 'dimension')
    f5 = Filter(u'天', '=', '32', 'day', 'dimension')

    fg = FilterGroup(f1)
    fg.and_(f3)

    fg2 = FilterGroup(f4)
    fg2.and_(f5)
    query.where(fg2)
    query.having(fg)

    query.format('json')
    query.date('gmt_date', '2018-01-01', '2018-01-02')
    print query.as_sql()



