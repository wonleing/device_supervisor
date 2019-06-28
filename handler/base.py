# -*- coding: utf-8 -*-

import traceback
import time
import uuid
import logging
import tornado.web
import os
import sys
from tornado.util import ObjectDict
from tornado.escape import json_decode, json_encode
from sqlalchemy.orm import defer
from sqlalchemy import literal_column, desc, column
from app.config import DBSession
from app.config import CONF
from app.model import User, Session, ActionLog
from util import UtilHandler

COOKIE_NAME = CONF.get('general', 'cookie_name')
DEBUG = CONF.getboolean('general', 'debug')

logger = logging.getLogger('app.base')

class BaseHandler(tornado.web.RequestHandler, UtilHandler):
    SUPPORTED_METHODS = ('GET', 'POST')

    @property
    def session(self):
        if not hasattr(self, '_session'):
            self._session = DBSession
        return self._session


    def on_finish(self):
        if hasattr(self, '_session'):
            self._session.rollback()


    def initialize(self, *args, **kargs):
        self.request.uuid = uuid.uuid4().hex[:8]
        self.session.rollback()

    def check(self):
        pass

    def prepare(self):

        #跨域行为

        origin = self.request.headers.get('Origin', None) or None

        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Methods', self.request.headers.get('Access-Control-Request-Method', ''));
        self.set_header('Access-Control-Allow-Headers', self.request.headers.get('Access-Control-Request-Headers', ''))

        if DEBUG:
            self.set_header('Access-Control-Allow-Origin', origin or '*')


        if self.request.headers.get('Content-Type', '').startswith('multipart/form-data'):
            self.p = {}
        else:
            self.p = self.all_arguments()

        self.check()
        if self._finished:
            return


    def check_captcha(self, code):
        sid = self.get_secure_cookie(COOKIE_NAME)
        if not sid:
            return False

        try:
            session = self.session.query(Session).filter_by(id=sid).first()
        except:
            return False

        now = int(time.time())
        ok = True

        if not session.code:
            ok = False

        if abs(session.code_create - now) > 60 * 5:
            ok = False

        if session.code.lower() != code.lower():
            ok = False

        session.code = ''
        session.code_create = 0
        self.session.add(session)
        self.session.commit()
        return ok


    def get_current_user(self):
        sid = self.get_secure_cookie(COOKIE_NAME)
        if not sid:
            return None

        #这个因为在 log_function 中, 所以比 init 还要早, 数据库的连接可能出问题
        try:
            session = self.session.query(Session).filter_by(id=sid).first()
        except:
            self.session.rollback()
            session = self.session.query(Session).filter_by(id=sid).first()

        if not session:
            return None

        #if self.request.remote_ip != session.ip:
        #    return None

        if session.user is None:
            return None

        user = self.session.query(User).filter_by(id=session.user).first()
        if not user:
            return None

        p = user.dict()
        p['sid'] = sid
        return ObjectDict(p)


    def get_current_session(self):
        current_session = getattr(self, '_current_session', None)
        if current_session:
            return current_session

        if not self.current_user:
            return None

        if not self.current_user.sid:
            return None

        current_session = self.session.query(Session).filter_by(id=self.current_user.sid).first()
        setattr(self, '_current_session', current_session)
        return current_session


    def get_error_html(self, status_code, **kargs):
        '返回一个字符串'

        if not getattr(self, 'uuid', None):
            self.uuid = ''

        try:
            return self.render_string('%s.html' % status_code, uuid=self.uuid)
        except:
            return self.render_string('500.html', uuid=self.uuid)


    def render_string(self, template_name, **kwargs):
        '照官方文档, 把 template_name 传入模板, 方便开发与调试'

        # If no template_path is specified, use the path of the calling file
        RequestHandler = tornado.web.RequestHandler

        template_path = self.get_template_path()
        if not template_path:
            frame = sys._getframe(0)
            web_file = frame.f_code.co_filename
            while frame.f_code.co_filename == web_file:
                frame = frame.f_back
            template_path = os.path.dirname(frame.f_code.co_filename)
        with RequestHandler._template_loader_lock:
            if template_path not in RequestHandler._template_loaders:
                loader = self.create_template_loader(template_path)
                RequestHandler._template_loaders[template_path] = loader
            else:
                loader = RequestHandler._template_loaders[template_path]

        t = loader.load(template_name)
        args = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            _=self.locale.translate,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.reverse_url,
            template_name=template_name, #ZYS
        )
        args.update(kwargs)
        return t.generate(**args)

    def all_arguments(self):
        all = {}
        for k in self.request.arguments:
            all[k] = self.get_argument(k, '')
        return ObjectDict(all)

    def get_argument_int(self, key, default=None, min=0):
        v = str(self.get_argument(key, default))
        return int(v) if v and v.isdigit() and int(v) >= min else default

    def get_argument_enum(self, key, choice=[], default=None):
        v = self.get_argument(key, default)
        choice = [str(x) for x in choice]
        return v if v in choice else default

    def finish(self, chunk=None):

        if self._status_code != 200:
            super(BaseHandler, self).finish(chunk)
            return

        body = chunk
        if body is None:
            body = ''.join(self._write_buffer)
            try:
                body = json_decode(body)
            except:
                body = None

        if self.request.method == 'POST' and self.current_user and isinstance(body, dict) and body['code'] == 0:
            args = self.all_arguments()
            d = {}
            for k, v in args.items():
                if not 'password' in k and len(v) < 5000:
                    d[k] = v

            p = {
                'create': time.time(),
                'user': self.current_user.id,
                'type': self.request.path,
                'target': json_encode(d),
                'content': '',
            }
            self.session.add(ActionLog(**p))
            self.session.commit()


        super(BaseHandler, self).finish(chunk)


class RestHandler(BaseHandler):
    SUPPORTED_METHODS = ('GET', 'POST')

    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 10
    MAX_PER_PAGE = 100
    TEMPLATE = None

    def get_query(self):
        raise Exception('not implemented')

    def get_option_query(self):
        raise Exception('not implemented')

    def create(self):
        raise Exception('not implemented')

    def delete(self):
        raise Exception('not implemented')

    def update(self):
        raise Exception('not implemented')

    def is_post_method(self, action):
        return action in {'create', 'update', 'delete'}

    def get_template_args(self):
        return {}

    def permission(self):
        self.finish({'code': -1, 'msg': u'没有权限'})

    def prepare(self):
        super(RestHandler, self).prepare()
        self.permission()

    @tornado.web.asynchronous
    def get(self, action):
        action = action.replace('-', '_')

        if not action:
            self.render(self.TEMPLATE, **self.get_template_args()) if self.TEMPLATE else self.send_error(404)
            return

        action = action[1:]
        if self.is_post_method(action):
            self.send_error(403)
        else:
            getattr(self, action)()


    @tornado.web.asynchronous
    def post(self, action):
        action = action.replace('-', '_')
        if not action:
            self.send_error(404)
            return

        action = action[1:]
        getattr(self, action)()


    def get_page_and_per_page(self):
        page = self.get_argument('page', str(self.DEFAULT_PAGE))
        page = int(page) if page.isdigit() else self.DEFAULT_PAGE

        per_page = self.get_argument('perPage', str(self.DEFAULT_PER_PAGE))
        per_page = int(per_page) if per_page.isdigit() else self.DEFAULT_PER_PAGE
        if per_page > self.MAX_PER_PAGE: per_page = self.MAX_PER_PAGE

        return page, per_page

    def list_filter(self, q):
        return q

    def list_defer(self):
        return []

    def list(self):
        page, per_page = self.get_page_and_per_page()
        order_by = self.get_argument('orderBy', '')
        order_desc = self.get_argument('orderDesc', '1') == '1'
        is_count = self.get_argument('isCount', '1') == '1'

        q = self.list_filter(self.get_query())

        # 排序这里的处理没有太好的办法.
        # 使用 literal_column 的话, 像 create 这种关键词, sqlalchemy 是不会自己加上 `` 或 '' 的
        # 使用 column , 如果涉及多个 model 又会报错.
        # 所有, 这里的处理, 就以 . 来区分了, 单一 model 不需要 . , 可能是 create 这种关键词, 用 column 处理
        # 带 . 的, 不可能是关键词, 直接用 literal_column 处理就好.

        if ' ' in order_by: order_by = ''
        if order_by:
            if '.' in order_by:
                q = q.order_by( desc(literal_column(order_by)) \
                               if order_desc \
                               else literal_column(order_by) )
            else:
                q = q.order_by( desc(column(order_by)) \
                               if order_desc \
                               else column(order_by) )

        q.options(*[defer(k) for k in self.list_defer()])

        count = q.count() if is_count else 0
        q = q.limit(per_page).offset((page - 1) * per_page)

        try:
            obj = [o.dict(self.list_defer()) for o in q]
        except:
            data = 'query error, maybe since the ~ orderBy ~\n' + traceback.format_exc()
            logger.error(data)
            self.finish({'code': -2, 'msg': u'出现了错误，可能是排序参数给的不完整'})
            return

        p = {
            'count': count,
            'page': page,
            'perPage': per_page,
            'isCount': is_count,
            'itemList': obj
        }
        self.finish({'code': 0, 'data': p})


    def read(self):
        id = self.get_argument('id', '')
        if not id:
            self.finish({'code': 1, 'msg': 'id 不能为空'})
            return

        q = self.get_query()
        q = q.filter_by(id=id)
        if not self.session.query(q.exists()).scalar():
            self.finish({'code': 2, 'msg': '指定 id 的内容不存在'})
            return

        obj = q.first()
        self.finish({'code': 0, 'data': obj.dict()})


    def option(self):
        page, per_page = self.get_page_and_per_page()
        is_count = self.get_argument('isCount', '1') == '1'
        q = self.list_filter(self.get_option_query())
        count = q.count() if is_count else 0
        q = q.limit(per_page).offset((page - 1) * per_page)
        obj = [{'name': name, 'value': id} for (id, name) in q]

        p = {
            'count': count,
            'page': page,
            'perPage': per_page,
            'isCount': is_count,
            'itemList': obj
        }
        self.finish({'code': 0, 'data': p})



class TemplateHandler(BaseHandler):
    '直接渲染一个模板'

    def initialize(self, template):
        self.template = template
        super(TemplateHandler, self).initialize()

    def get(self, **kargs):
        self.render(self.template, **kargs)


class IndexHandler(BaseHandler):
    pass


