# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship



class System(BaseModel):
    '系统项'

    __tablename__ = 'system'

    NAME_NONE = 'none'

    NAME_FRONT_ADMIN_TEMPLATE = 'front_admin_template';
    NAME_FRONT_ADMIN_VERSION = 'front_admin_version';
    NAME_FRONT_ADMIN_ENV = 'front_admin_env';
    NAME_FRONT_ADMIN_CND = 'front_admin_cdn';

    ALL_NAME = {
        NAME_FRONT_ADMIN_TEMPLATE,
        NAME_FRONT_ADMIN_VERSION,
        NAME_FRONT_ADMIN_ENV,
        NAME_FRONT_ADMIN_CND,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    update = Column(BigInteger, server_default='0', nullable=False)
    name = Column(String(64), server_default='none', nullable=False, index=True, unique=True)
    value = Column(Text, default='', nullable=False)

