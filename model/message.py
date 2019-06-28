# -*- coding: utf-8 -*-
 
from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship


class Message(BaseModel):
    '单纯的消息'

    __tablename__ = 'message'

    TYPE_NORMAL = 'normal'
    TYPE_WARN = 'warn'

    STATUS_NORMAL = 'normal'
    STATUS_DELETE = 'delete'

    STATUS_MAP = {
        STATUS_NORMAL: u'正常',
        STATUS_DELETE: u'已删除'
    }

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    type = Column(String(16), server_default='normal', nullable=False, index=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)
    create = Column(BigInteger, server_default='0', nullable=False, index=True)

    title = Column(String(64), server_default='', nullable=False)
    content = Column(Text, default='', nullable=False)


class UserMessage(BaseModel):
    '用户消息'

    __tablename__ = 'user_message'

    TYPE_NORMAL = 'normal'
    TYPE_WARN = 'warn'

    STATUS_NORMAL = 'normal'
    STATUS_DELETE = 'delete'
    STATUS_READED = 'readed'

    STATUS_MAP = {
        STATUS_NORMAL: u'未读',
        STATUS_DELETE: u'已删除',
        STATUS_READED: u'已读'
    }

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(16), server_default='normal', nullable=False, index=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)
    user = Column(BigInteger, ForeignKey('user.id'), nullable=False, index=True)
    message = Column(BigInteger, ForeignKey('message.id'), nullable=False, index=True)
    update = Column(BigInteger, server_default='0', nullable=False)

    message_obj = relationship('Message', lazy='joined')
    user_obj = relationship('User', lazy='joined')

    def extra_attribute(self, obj):
        obj['message_obj'] = dict(
            id = self.message_obj.id,
            title = self.message_obj.title,
            content = self.message_obj.content,
            status = self.message_obj.status
        )
        obj['user_obj'] = dict(
            user_name = self.user_obj.name,
        )


