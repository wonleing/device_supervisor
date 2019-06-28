# -*- coding: utf-8 -*-

from base import RestHandler
from app.model import Rule, User


class RuleHandler(RestHandler):

    def permission(self):
        if not self.current_user:
            self.finish({'code': -1, 'msg': u'没有权限'})
            return

        if self.current_user.type not in [User.TYPE_ADMIN]:
            self.finish({'code': -1, 'msg': u'没有权限'})


    def get_query(self):
        q = self.session.query(Rule).filter_by(status=Rule.STATUS_NORMAL)
        return q

    def get_option_query(self):
        query = self.get_argument('q', '')
        q = self.session.query(Rule.id, Rule.name).filter_by(status=Rule.STATUS_NORMAL)
        if query:
            q = q.filter(Rule.name.ilike('%' + query + '%'))
        q = q.order_by(-Rule.id)
        return q


    def create(self):
        p = {
            'name': self.get_argument('name', ''),
            'code': self.get_argument('code', ''),
            'field': self.get_argument('field', ''),
            'op': self.get_argument('op', ''),
            'value': self.get_argument('value', ''),
        }

        if not p['name']:
            self.finish({'code': 1, 'msg': u'name不能为空'})
            return

        if not p['code']:
            self.finish({'code': 2, 'msg': u'code不能为空'})
            return

        if not p['field']:
            self.finish({'code': 3, 'msg': u'field不能为空'})
            return

        if not p['op']:
            self.finish({'code': 4, 'msg': u'op不能为空'})
            return

        if not p['value']:
            self.finish({'code': 5, 'msg': u'value不能为空'})
            return

        rule = Rule(**p)
        self.session.add(rule)
        self.session.commit()
        self.finish({'code': 0, 'data': rule.dict()})


    def delete(self):
        if not self.get_argument('id', ''):
            self.finish({'code': 1, 'msg': u'id不能为空'})
            return
        id =  [i.strip() for i in filter(None,self.p.id.split(','))]
        self.get_query().filter(Rule.id.in_(id)).update({'status': Rule.STATUS_DELETE},
                                                         synchronize_session=False)
        self.session.commit()
        self.finish({'code': 0})


    def update(self):
        if not self.get_argument('id', ''):
            self.finish({'code': 1, 'msg': u'id不能为空'})
            return

        p = {
            'name': self.get_argument('name', ''),
            'code': self.get_argument('code', ''),
            'field': self.get_argument('field', ''),
            'op': self.get_argument('op', ''),
            'value': self.get_argument('value', ''),
        }
        data = {}
        for k in p:
            if p[k]: data[k] = p[k]

        self.get_query().filter_by(id=self.p.id).update(data)
        self.session.commit()
        self.finish({'code': 0})


