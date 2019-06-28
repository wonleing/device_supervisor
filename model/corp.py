# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy


class Corp(BaseModel):
    '企业'

    __tablename__ = 'corp'

    TYPE_NORMAL = 'normal'

    STATUS_NORMAL = 'normal'
    STATUS_DELETE = 'delete'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(16), server_default='normal', nullable=False, index=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)

    name = Column(String(32), server_default='', nullable=False)
    create = Column(BigInteger, server_default='0', nullable=False)
    contacts = Column(String(32), server_default='', nullable=False)
    tel = Column(String(32), server_default='', nullable=False)
    avatar = Column(String(128), server_default='', nullable=False)
    address = Column(String(255), server_default='', nullable=False)



class CorpUser(BaseModel):
    '企业中的用户'

    __tablename__ = 'corp_user'

    ROLE_NORMAL = 'normal'
    ROLE_ADMIN = 'admin'
    ROLE_MAP = {
        ROLE_NORMAL: u'普通',
        ROLE_ADMIN: u'管理员',
    }

    STATUS_NORMAL = 'normal'
    STATUS_DELETE = 'delete'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    corp = Column(BigInteger, ForeignKey('corp.id'), nullable=False, index=True)
    user = Column(BigInteger, ForeignKey('user.id'), nullable=False, index=True)
    role = Column(String(8), server_default='normal', nullable=False)
    create = Column(BigInteger, server_default='0', nullable=False)
    status = Column(String(8), server_default='normal', nullable=False, index=True)

    user_obj = relationship('User', lazy='joined')
    corp_obj = relationship('Corp', lazy='joined')

    def extra_attribute(self, obj):
        obj['user_obj'] = self.user_obj.dict()
        obj['corp_obj'] = self.corp_obj.dict()



class CorpDevice(BaseModel):
    '企业的设备'

    __tablename__ = 'corp_device'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    corp = Column(BigInteger, ForeignKey('corp.id'), nullable=False, index=True)
    device = Column(BigInteger, ForeignKey('device.id'), nullable=False, index=True)
    create = Column(BigInteger, server_default='0', nullable=False)
    role = Column(String(8), server_default='', nullable=False)
    corp_obj = relationship('Corp', lazy='joined')
    device_obj = relationship('Device', lazy='joined')

    def extra_attribute(self, obj):
        obj['corp_obj'] = self.corp_obj.dict()
        obj['device_obj'] = self.device_obj.dict()



