# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text

class TakeOrder(BaseModel):
    '取货订单'

    __tablename__ = 'take_order'
    TYPE_take = 'take'

    STATUS_NORMAL = 'normal'
    STATUS_ABNORMAL = 'abnormal'
    STATUS_TREATED = 'treated'
    STATUS_DELETE = 'delete'


    STATUS_MAP = {
        STATUS_NORMAL: u'未处理',
        STATUS_ABNORMAL: u'异常',
        STATUS_TREATED: u'已处理',
        STATUS_DELETE: u'删除'
    }

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(16), server_default='', nullable=False, index=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)
    serial_number = Column(String(64), server_default='', nullable=False, index=True)
    mode = Column(String(64), server_default='', nullable=False, index=True)
    medium = Column(String(64), server_default='', nullable=False, index=True)
    supplier = Column(String(64), server_default='', nullable=False,index=True)
    source = Column(String(64), server_default='', nullable=False,index=True)
    user = Column(BigInteger, server_default='0', nullable=False,index=True)
    contacts = Column(String(16), server_default='', nullable=False)
    contacter = Column(String(64), server_default='', nullable=False)
    remark = Column(String(256), server_default='', nullable=False)
    arrive_t = Column(BigInteger, server_default='0', nullable=False)
    tractor = Column(String(64), server_default='', nullable=False)
    trailer = Column(String(64), server_default='', nullable=False)
    location = Column(String(64), server_default='', nullable=False)
    press_before = Column(Numeric(9, 2), server_default='0', nullable=False)
    press_after = Column(Numeric(9, 2), server_default='0', nullable=False)
    temp_before = Column(Numeric(9, 2), server_default='0', nullable=False)
    temp_after = Column(Numeric(9, 2), server_default='0', nullable=False)
    before = Column(Numeric(9, 2), server_default='0', nullable=False)
    after = Column(Numeric(9, 2), server_default='0', nullable=False)
    create = Column(BigInteger, server_default='0', nullable=False)
    update = Column(BigInteger, server_default='0', nullable=False)
    updater = Column(String(64), server_default='', nullable=False)

class DeliverOrder(BaseModel):
    '送货订单'

    __tablename__ = 'deliver_order'
    TYPE_deliver = 'deliver'

    STATUS_UNLOAD = 'unload'
    STATUS_DISPATCH = 'dispatch'
    STATUS_BACKSPACE = 'backspace'
    STATUS_DELETE = 'delete'
    STATUS_ABNORMAL = 'abnormal'


    STATUS_MAP = {
        STATUS_UNLOAD: u'待卸车',
        STATUS_ABNORMAL: u'异常',
        STATUS_DISPATCH: u'待派车',
        STATUS_DELETE: u'删除',
        STATUS_BACKSPACE:u'待回空'
    }

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(16), server_default='', nullable=False)
    status = Column(String(16), server_default='dispatch', nullable=False, index=True)
    serial_number = Column(String(64), server_default='', nullable=False, index=True)
    mode = Column(String(64), server_default='', nullable=False, index=True)
    station = Column(String(64), server_default='', nullable=False,index=True)
    customer = Column(String(64), server_default='', nullable=False,index=True)
    user = Column(BigInteger, server_default='0', nullable=False,index=True)
    tractor = Column(String(64), server_default='', nullable=False,index=True)
    trailer = Column(String(64), server_default='', nullable=False,index=True)

    take_order = Column(BigInteger, server_default='0', nullable=False)
    contacts = Column(String(16), server_default='', nullable=False)
    contacter = Column(String(64), server_default='', nullable=False)
    remark = Column(String(256), server_default='', nullable=False)
    arrive_t = Column(BigInteger, server_default='0', nullable=False)
    leave_t = Column(BigInteger, server_default='0', nullable=False)
    location = Column(String(64), server_default='', nullable=False)
    press_after = Column(Numeric(9, 2), server_default='0', nullable=False)
    press_arrive = Column(Numeric(9, 2), server_default='0', nullable=False)
    temp_after = Column(Numeric(9, 2), server_default='0', nullable=False)
    after = Column(Numeric(9, 2), server_default='0', nullable=False)
    leave = Column(Numeric(9, 2), server_default='0', nullable=False)
    add = Column(Numeric(9, 2), server_default='0', nullable=False)
    create = Column(BigInteger, server_default='0', nullable=False)
    update = Column(BigInteger, server_default='0', nullable=False)
    updater = Column(String(64), server_default='', nullable=False)


