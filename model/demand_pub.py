# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column
from sqlalchemy.types import BigInteger, String

class DemandPub(BaseModel):

    __tablename__ = 'demandpub'
    id = Column(BigInteger, primary_key=True, autoincrement=True,nullable=False)
    title = Column(String(32), server_default='', nullable=False)
    content = Column(String(64), server_default='', nullable=False)
    time = Column(BigInteger, server_default='', nullable=False)
    type = Column(String(16), server_default='', nullable=False)
    process = Column(String(16), server_default='', nullable=False)
    handler = Column(String(16), server_default='', nullable=False)
    publisher = Column(String(16), server_default='', nullable=False)
    regist = Column(String(64), server_default='', nullable=False)


class SuggestionBack(BaseModel):

    __tablename__ = 'suggestionback'
    id = Column(BigInteger, primary_key=True, autoincrement=True,nullable=False)
    title = Column(String(32), server_default='', nullable=False)
    content = Column(String(64), server_default='', nullable=False)
    time = Column(BigInteger, server_default='', nullable=False)
    type = Column(String(16), server_default='', nullable=False)
    process = Column(String(16), server_default='', nullable=False)
    handler = Column(String(16), server_default='', nullable=False)
    publisher = Column(String(16), server_default='', nullable=False)
    regist = Column(String(64), server_default='', nullable=False)