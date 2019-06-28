# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship



class ALiProduct(BaseModel):
    '用户'

    __tablename__ = 'aliyun_product'

    TYPE_NORMAL = 'normal'
    TYPE_ADMIN = 'admin'

    STATUS_NORMAL = 'normal'
    STATUS_DELETE = 'delete'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)
    name = Column(String(32), server_default='', nullable=False)
    field_alias = Column(String(128), server_default='', nullable=False)
    create = Column(BigInteger, server_default='0', nullable=False)
    productkey = Column(String(255), server_default='', nullable=False)


class ProductAttribute(BaseModel):
    '产品的自定义属性值'

    __tablename__ = 'product_attribute'

    TYPE_CONF= 'conf'
    TYPE_CONT = 'cont'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(128), server_default='', nullable=False, index=True)
    name = Column(String(128), server_default='', nullable=False)
    value = Column(String(512), server_default='', nullable=False)
    productkey = Column(BigInteger, ForeignKey('aliyun_product.id'), nullable=False, index=True)
    edit = Column(String(10), server_default='0', nullable=False)
    type = Column(BigInteger, server_default='conf', nullable=False)