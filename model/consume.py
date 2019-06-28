# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column
from sqlalchemy.types import BigInteger, String, Numeric

class Consume(BaseModel):
    '会话'

    __tablename__ = 'consume'

    TYPE_DAY = 'day'
    TYPE_MONTH = 'month'
    TYPE_YEAR = 'year'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(16), server_default='', nullable=False, index=True)
    cpu_id = Column(String(64), server_default='', nullable=False, index=True)
    consume = Column(Numeric(9, 2), server_default='', nullable=False)
    supply = Column(Numeric(9, 2), server_default='', nullable=False)
    time = Column(BigInteger, server_default='0', nullable=False, index=True)
    create = Column(BigInteger, server_default='0', nullable=False)
    warn = Column(BigInteger, server_default='0', nullable=False)



