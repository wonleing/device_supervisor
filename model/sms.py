# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship


class Sms(BaseModel):
    '短信'

    __tablename__ = 'sms'

    TYPE_NORMAL = 'normal'
    TYPE_WARN = 'warn'

    STATUS_NORMAL = 'normal'
    STATUS_COMPLETE = 'complete'
    STATUS_FAIL = 'fail'

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    type = Column(String(16), server_default='normal', nullable=False, index=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)

    create = Column(BigInteger, server_default='0', nullable=False, index=True)
    last = Column(BigInteger, server_default='0', nullable=False)
    device = Column(BigInteger, server_default='0', nullable=False)

    content = Column(Text, default='', nullable=False)
    target = Column(Text, default='', nullable=False)


