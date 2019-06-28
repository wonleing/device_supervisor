#-*-coding:utf-8-*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, Integer, SmallInteger, Date, Text

class TopicLog(BaseModel):

    __tablename__ = 'topiclog'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(64),server_default='', nullable=False, index=True)
    topic = Column(String(64), server_default='', nullable=False, index=True)
    message = Column(String(64), server_default='0', nullable=False)
    updatetime = Column(BigInteger,server_default='0',nullable=False, index=True)
    remarks = Column(String(64),server_default='',nullable=True)
    messagecount = Column(BigInteger, server_default='0', nullable=False)
    productkey = Column(String(64),server_default='', nullable=False)
    devicename = Column(String(64),server_default='', nullable=False, index=True)