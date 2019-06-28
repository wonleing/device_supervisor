# -*- coding: utf-8 -*-
 
from base import BaseModel
from device import Device
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship


class Rule(BaseModel):
    '预警的规则'

    __tablename__ = 'rule'

    TYPE_NORMAL = 'normal'

    STATUS_NORMAL = 'normal'
    STATUS_DELETE = 'delete'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(16), server_default='normal', nullable=False, index=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)

    name = Column(String(32), server_default='', nullable=False)
    code = Column(String(32), server_default='', nullable=False, index=True)
    field = Column(String(32), server_default='', nullable=False, index=True)
    op = Column(String(8), server_default='', nullable=False)
    value = Column(String(32), server_default='', nullable=False)


class DeviceRule(BaseModel):
    '设备与规则的关系'

    __tablename__ = 'device_rule'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    device = Column(BigInteger, ForeignKey(Device.id), nullable=False, index=True)
    rule = Column(BigInteger, ForeignKey(Rule.id), nullable=False, index=True)


