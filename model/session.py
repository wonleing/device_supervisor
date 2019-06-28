# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, Integer, SmallInteger, Date, Text

class Session(BaseModel):
    '会话'

    __tablename__ = 'session'

    id = Column(String(32), primary_key=True, nullable=False)

    user = Column(BigInteger, ForeignKey('user.id'), nullable=True, index=True)
    create = Column(BigInteger, server_default='0', nullable=False)

    code = Column(String(8), server_default='', nullable=False) #验证码
    code_create = Column(BigInteger, server_default='0', nullable=False)
    code_mobile = Column(String(11), server_default='', nullable=False) #验证码对应的手机

    ip = Column(String(64), server_default='', nullable=False)
    corp = Column(BigInteger, ForeignKey('corp.id'), nullable=True)
    email = Column(String(32), server_default='', nullable=False)


