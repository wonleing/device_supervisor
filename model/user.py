# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship



class User(BaseModel):
    '用户'

    __tablename__ = 'user'

    TYPE_NORMAL = 'normal'
    TYPE_ADMIN = 'admin'

    STATUS_NORMAL = 'normal'
    STATUS_DELETE = 'delete'

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    type = Column(String(16), server_default='normal', nullable=False, index=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)

    name = Column(String(32), server_default='', nullable=False)
    avatar = Column(String(128), server_default='', nullable=False)
    mobile = Column(String(11), server_default='', nullable=False)
    email = Column(String(128), server_default='', nullable=False)
    create = Column(BigInteger, server_default='0', nullable=False)
    address = Column(String(255), server_default='', nullable=False)
    position = Column(String(32), server_default='', nullable=False)
    department = Column(String(32), server_default='', nullable=False)
    sex = Column(String(8), server_default='', nullable=False)
    rid = Column(String(32), server_default='', nullable=False)


class UserDevice(BaseModel):
    '用户名下的设备'

    __tablename__ = 'user_device'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user =  Column(BigInteger, ForeignKey('user.id'), nullable=False, index=True)
    device = Column(BigInteger, ForeignKey('device.id'), nullable=False, index=True)
    role = Column(String(8), nullable=False)
    device_obj = relationship('Device', lazy='joined')

    def extra_attribute(self, obj):
        obj['device_obj'] = self.device_obj.dict()
