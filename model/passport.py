# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship



class Passport(BaseModel):
    '登录账号'

    __tablename__ = 'passport'

    TYPE_NORMAL = 'normal'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user = Column(BigInteger, ForeignKey('user.id'), nullable=False, index=True)
    type = Column(String(16), server_default='normal', nullable=False, index=True)

    username = Column(String(32), server_default='', nullable=False)
    password = Column(String(64 + 16), server_default='', nullable=False)

    create = Column(BigInteger, server_default='0', nullable=False)
    openid = Column(String(64 + 16), server_default='', nullable=False)
    login_time = Column(BigInteger, server_default='0', nullable=False)


