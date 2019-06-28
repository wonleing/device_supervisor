# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship


class Push(BaseModel):
    '移动端消息推送'

    __tablename__ = 'push'

    TYPE_NORMAL = 'normal'

    STATUS_NORMAL = 'normal'
    STATUS_COMPLETE = 'complete'
    STATUS_FAIL = 'fail'

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    type = Column(String(16), server_default='normal', nullable=False, index=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)

    create = Column(BigInteger, server_default='0', nullable=False, index=True)
    last = Column(BigInteger, server_default='0', nullable=False)
    device = Column(BigInteger, server_default='0', nullable=False)

    title = Column(String(64), server_default='', nullable=False)
    content = Column(Text, default='', nullable=False)
    target = Column(Text, default='', nullable=False)


