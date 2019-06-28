# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base

_BaseModel = declarative_base()

class BaseModel(_BaseModel):
    __abstract__ = True
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
    }

    def extra_attribute(self, obj):
        pass

    def dict(self, defer=[]):
        o = dict((k, getattr(self, k)) for k in self.__mapper__.c.keys() if k not in defer)
        self.extra_attribute(o)
        return o


