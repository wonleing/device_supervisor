# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship


class Supply(BaseModel):
    '充装记录'
    __tablename__ = 'supply'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    serial_number = Column(String(64), server_default='', nullable=False,index=True)
    medium = Column(String(64), server_default='', nullable=False,index=True)
    cpu_id = Column(String(64), server_default='', nullable=False,index=True)
    create = Column(BigInteger, server_default='0', nullable=False,index=True)
    before = Column(Numeric(9, 2), server_default='0', nullable=False)
    after = Column(Numeric(9, 2), server_default='0', nullable=False)
    add = Column(Numeric(9, 2), server_default='0', nullable=False)
    adjust = Column(Numeric(9, 2), server_default='0', nullable=False)




class SupplyPrint(BaseModel):
    '充装打印记录'

    __tablename__ = 'supply_print'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cpu_id = Column(String(64), server_default='', nullable=False, index=True)
    serial_number = Column(String(64), server_default='', nullable=False, index=True)
    create = Column(BigInteger, server_default='0', nullable=False, index=True)
    adjust = Column(Numeric(9, 2), server_default='0', nullable=False)
    unit_price = Column(Numeric(9, 2), server_default='0.00', nullable=False)
    total_cost = Column(Numeric(9, 2), server_default='0.00', nullable=False)
    add = Column(Numeric(9, 2), server_default='0.00', nullable=False)
    medium = Column(String(30), server_default='', nullable=False, index=True)
    operator = Column(String(40), server_default='', nullable=False, index=True)
    supplier = Column(String(64), server_default='', nullable=False, index=True)
    end_user = Column(String(64), server_default='', nullable=False, index=True)
    before = Column(Numeric(9, 2), server_default='0', nullable=False)
    after = Column(Numeric(9, 2), server_default='0', nullable=False)
    supply = Column(BigInteger,server_default='0', nullable=False, index=True)
