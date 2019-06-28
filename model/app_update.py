#-*-coding:utf-8-*-
from base import BaseModel
from sqlalchemy import Column,ForeignKey
from sqlalchemy.types import BigInteger, String
from sqlalchemy.orm import relationship

class AppUpdate(BaseModel):
    u'app升级'

    __tablename__ = 'app_version'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    version = Column(String(32), server_default='', nullable=False, index=True)
    time = Column(BigInteger, server_default='0', nullable=False, index=True)
    comment = Column(String(64), server_default='', nullable=False)
    updater = Column(BigInteger, ForeignKey('user.id'), server_default='0', nullable=False)
    size = Column(BigInteger, server_default='0', nullable=False)
    url = Column(String(255), server_default='', nullable=False)
    name = Column(String(64),server_default = '',nullable=False, index=True)
    user_obj = relationship('User', lazy='joined')

    def extra_attribute(self, obj):
        obj['user_obj'] = dict(
            name=self.user_obj.name,
            user_id=self.user_obj.id,
        )
