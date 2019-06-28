#-*-coding:utf-8-*-
from base import BaseModel
from sqlalchemy import Column
from sqlalchemy.types import BigInteger, String

class Information(BaseModel):

    __tablename__ = 'information'
    id = Column(BigInteger, primary_key=True, autoincrement=True,nullable=False)
    title = Column(String(64), server_default='', nullable=False)
    picture = Column(String(32), server_default='', nullable=False)
    time = Column(BigInteger, server_default='', nullable=False)
    url = Column(String(32), server_default='', nullable=False)