# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy


class Telecontrol(BaseModel):
    '企业'

    __tablename__ = 'telecontrol'

    STATUS_NORMAL = 'normal'
    STATUS_FAIL = 'fail'
    STATUS_DELETE = 'delete'
    STATUS_SEND = 'send'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    device_id = Column(BigInteger, nullable=True,index=True)
    cpu_id = Column(String(64), server_default='normal', nullable=False, index=True)

    status = Column(String(16), server_default='normal', nullable=False, index=True)

    command = Column(String(512), server_default='', nullable=False)
    create = Column(BigInteger, server_default='0', nullable=False)
    time = Column(BigInteger, server_default='0', nullable=False)