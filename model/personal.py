#-*-coding:utf-8-*-
from base import BaseModel
from sqlalchemy import Column
from sqlalchemy.types import BigInteger, String

class Invoice(BaseModel):

    __tablename__ = 'invoice'
    id = Column(BigInteger, primary_key=True, autoincrement=True,nullable=False)
    corpname = Column(String(32), server_default='', nullable=False)
    taxnumber = Column(String(20), server_default='', nullable=False)
    register_address = Column(String(255), server_default='', nullable=False)
    telephone = Column(String(11), server_default='', nullable=False)
    bankname = Column(String(32), server_default='', nullable=False)
    banknumber = Column(String(19), server_default='', nullable=False)
    time = Column(BigInteger, server_default='', nullable=False)


