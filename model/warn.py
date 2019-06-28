# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship


class Warn(BaseModel):
    '预警'

    __tablename__ = 'warn'

    TYPE_NORMAL = 'normal'

    STATUS_NORMAL = 'normal'
    STATUS_ERROR = 'error'
    STATUS_POSED = 'posed'

    STATUS_MAP = {
        STATUS_NORMAL: u'未处理',
        STATUS_POSED: u'已处理',
        STATUS_ERROR: u'错误'
    }

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(16), server_default='normal', nullable=False, index=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)

    cpu_id = Column(String(64), server_default='', nullable=False, index=True)
    code = Column(String(16), ForeignKey('warn_contrast.code'), nullable=False, index=True)
    content = Column(String(512), server_default='', nullable=False)
    time = Column(BigInteger, server_default='0', nullable=False)
    create = Column(BigInteger, server_default='0', nullable=False)
    code_obj = relationship('WarnContrast', lazy='joined')

    def extra_attribute(self, obj):
        if self.code_obj:
            obj['warn_contrast_obj'] = self.code_obj.dict()

class WarnContrast(BaseModel):
    '报警参照'
    __tablename__ = 'warn_contrast'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(16), server_default='', nullable=False, index=True)
    content = Column(String(16), server_default='', nullable=False, index=True)
    create = Column(BigInteger, server_default='0', nullable=False)







