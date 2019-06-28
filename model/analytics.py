# -*- coding: utf-8 -*-

 
from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship


class Fact(BaseModel):
    '事实表'

    __tablename__ = 'fact'

    STATUS_NORMAL = 'normal'
    STATUS_DELETE = 'delete'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)
    code = Column(String(32), server_default='', nullable=False, index=True)
    name = Column(String(32), server_default='', nullable=False)
    table = Column(Text, nullable=False)



class Metric(BaseModel):
    '指标'

    __tablename__ = 'metric'

    STATUS_NORMAL = 'normal'
    STATUS_DELETE = 'delete'

    AGGRE_SET = {'avg', 'min', 'max', 'count', 'uniq'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)
    code = Column(String(32), server_default='', nullable=False, index=True)
    name = Column(String(32), server_default='', nullable=False)
    column = Column(String(32), server_default='', nullable=False)
    aggre = Column(String(32), server_default='', nullable=False)


class CalculateMetric(BaseModel):
    '复合指标'

    __tablename__ = 'calculate_metric'

    STATUS_NORMAL = 'normal'
    STATUS_DELETE = 'delete'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)
    code = Column(String(32), server_default='', nullable=False, index=True)
    name = Column(String(32), server_default='', nullable=False)
    expression = Column(String(128), server_default='', nullable=False)


class Dimension(BaseModel):
    '维度'

    __tablename__ = 'dimension'

    STATUS_NORMAL = 'normal'
    STATUS_DELETE = 'delete'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)
    code = Column(String(32), server_default='', nullable=False, index=True)
    name = Column(String(32), server_default='', nullable=False)
    column = Column(String(32), server_default='', nullable=False)


class FactResource(BaseModel):
    '事实表中有的资源'

    __tablename__ = 'fact_resource'

    TYPE_DIMENSION = 'dimension'
    TYPE_METRIC = 'metric'
    TYPE_CALCULATE_METRIC = 'calculate_metric'
    TYPE_SET = {TYPE_DIMENSION, TYPE_METRIC, TYPE_CALCULATE_METRIC}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(16), server_default='dimension', nullable=False, index=True)
    fact = Column(BigInteger, ForeignKey(Fact.id), nullable=False, index=True)
    code = Column(String(32), nullable=False, index=True)


