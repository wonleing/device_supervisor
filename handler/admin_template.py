# -*- coding: utf-8 -*-

from base import BaseHandler
from app.model import System
from tornado.template import Template


class AdminTemplateHandler(BaseHandler):
    NAME = 'front_admin_template'
    def get(self):
        obj = self.session.query(System).filter_by(name=self.NAME).first()
        all_params = dict(self.session.query(System.name, System.value).all())
        tpl = Template(obj.value)
        s = tpl.generate(**all_params)
        self.finish(s)


class AdminTestTemplateHandler(BaseHandler):
    NAME = 'front_admin_test_template'
    def get(self):
        obj = self.session.query(System).filter_by(name=self.NAME).first()
        all_params = dict(self.session.query(System.name, System.value).all())
        tpl = Template(obj.value)
        s = tpl.generate(**all_params)
        self.finish(s)


class StaticTemplateHandler(BaseHandler):
    NAME = 'front_static_template'
    def get(self):
        obj = self.session.query(System).filter_by(name=self.NAME).first()
        all_params = dict(self.session.query(System.name, System.value).all())
        tpl = Template(obj.value)
        s = tpl.generate(**all_params)
        self.finish(s)


class HPLTemplateHandler(BaseHandler):
    NAME = 'front_hpl_template'
    def get(self):
        obj = self.session.query(System).filter_by(name=self.NAME).first()
        all_params = dict(self.session.query(System.name, System.value).all())
        tpl = Template(obj.value)
        s = tpl.generate(**all_params)
        self.finish(s)

class WebTemplateHandler(BaseHandler):
    NAME = 'front_web_template'
    def get(self):
        obj = self.session.query(System).filter_by(name=self.NAME).first()
        all_params = dict(self.session.query(System.name, System.value).all())
        tpl = Template(obj.value)
        s = tpl.generate(**all_params)
        self.finish(s)