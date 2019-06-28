# -*- coding: utf-8 -*-

from base import BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import BigInteger, String, SmallInteger, Integer, Numeric, Text
from sqlalchemy.orm import relationship



class Device(BaseModel):
    '设备'

    __tablename__ = 'device'

    TYPE_NORMAL = 'normal'

    STATUS_NORMAL = 'normal'
    STATUS_DELETE = 'delete'
    STATUS_WARNING = 'warning'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(16), server_default='normal', nullable=False, index=True)
    status = Column(String(16), server_default='normal', nullable=False, index=True)
    cpu_id = Column(String(64), server_default='', nullable=False, index=True)

    name = Column(String(32), server_default='', nullable=False)
    productkey = Column(String(32), server_default='', nullable=False)
    create = Column(BigInteger, server_default='0', nullable=False)
    data_update = Column(BigInteger, server_default='0', nullable=False)
    device_name = Column(String(64), nullable=False)


class DeviceSession(BaseModel):
    '设备会话,嵌入式通信时会使用'

    __tablename__ = 'device_session'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(64), server_default='', nullable=False, index=True)
    cpu_id = Column(String(64), server_default='', nullable=False, index=True)
    update = Column(BigInteger, server_default='0', nullable=False)



class DevicePackageRecord(BaseModel):
    '设备更新包的记录'

    __tablename__ = 'device_package_record'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cpu_id = Column(String(64), server_default='', nullable=False, index=True)
    version = Column(String(32), server_default='', nullable=False)
    update = Column(BigInteger, server_default='0', nullable=False, index=True)
    user = Column(BigInteger, ForeignKey('user.id'), server_default='0', nullable=False)
    url = Column(String(255), server_default='', nullable=False)
    size = Column(Integer, server_default='0', nullable=False)
    type = Column(String(20), nullable=False,index=True)
    remarks = Column(String(255), server_default='', nullable=False)

    user_obj = relationship('User', lazy='joined')
    def extra_attribute(self, obj):
        obj['user_obj'] = dict(
            name = self.user_obj.name,
            user_id=self.user_obj.id,
        )


class DeviceAttribute(BaseModel):
    '设备的自定义属性值'

    __tablename__ = 'device_attribute'

    TYPE_CONF= 'conf'
    TYPE_CONT = 'cont'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cpu_id = Column(String(64), server_default='', nullable=False, index=True)
    code = Column(String(128), server_default='', nullable=False, index=True)
    name = Column(String(128), server_default='', nullable=False)
    value = Column(String(512), server_default='', nullable=False)
    edit = Column(BigInteger, server_default='1', nullable=False)
    user = Column(BigInteger, server_default='0', nullable=False)
    type = Column(String(128), server_default='conf', nullable=False)
    product = Column(BigInteger, server_default='0', nullable=False)
    confirm = Column(BigInteger, server_default='0', nullable=False)

class DeviceAppendix(BaseModel):
    '设备的自定义属性值'

    __tablename__ = 'device_appendix'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cpu_id = Column(String(64), server_default='', nullable=False, index=True)
    device_name = Column(String(64), server_default='', nullable=False, index=True)
    type = Column(String(64), server_default='', nullable=False, index=True)
    location = Column(String(128), server_default='', nullable=False)
    range = Column(String(128), server_default='', nullable=False)
    serial_number = Column(String(128), server_default='', nullable=False,index=True)
    manufacturer = Column(String(128), server_default='', nullable=False)
    start_time = Column(BigInteger, server_default='0', nullable=False)
    end_time = Column(BigInteger, server_default='0', nullable=False)
    last_check = Column(BigInteger, server_default='0', nullable=False)
    check_cycle = Column(BigInteger, server_default='0', nullable=False)
    remarks = Column(String(512), server_default='', nullable=False)
    create = Column(BigInteger, server_default='0', nullable=False)
    update = Column(BigInteger, server_default='0', nullable=False)
    advance = Column(BigInteger, server_default='2592000', nullable=False)
    marker = Column(String(64), server_default='', nullable=False)

class FieldAlias(BaseModel):
    '设备的字段别名'

    __tablename__ = 'field_alias'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cpu_id = Column(String(64), server_default='', nullable=False, index=True)

    lng = Column(String(255), server_default='', nullable=False)
    lat = Column(String(255), server_default='', nullable=False)
    weight1 = Column(String(255), server_default='', nullable=False)
    weight2 = Column(String(255), server_default='', nullable=False)
    weight3 = Column(String(255), server_default='', nullable=False)
    weight4 = Column(String(255), server_default='', nullable=False)
    height1 = Column(String(255), server_default='', nullable=False)
    height2 = Column(String(255), server_default='', nullable=False)
    height3 = Column(String(255), server_default='', nullable=False)
    height4 = Column(String(255), server_default='', nullable=False)
    pressure1 = Column(String(255), server_default='', nullable=False)
    pressure2 = Column(String(255), server_default='', nullable=False)
    pressure3 = Column(String(255), server_default='', nullable=False)
    pressure4 = Column(String(255), server_default='', nullable=False)
    pressure5 = Column(String(255), server_default='', nullable=False)
    pressure6 = Column(String(255), server_default='', nullable=False)
    pressure7 = Column(String(255), server_default='', nullable=False)
    pressure8 = Column(String(255), server_default='', nullable=False)
    diff_pressure1 = Column(String(255), server_default='', nullable=False)
    diff_pressure2 = Column(String(255), server_default='', nullable=False)
    diff_pressure3 = Column(String(255), server_default='', nullable=False)
    diff_pressure4 = Column(String(255), server_default='', nullable=False)
    per1 = Column(String(255), server_default='', nullable=False)
    per2 = Column(String(255), server_default='', nullable=False)
    per3 = Column(String(255), server_default='', nullable=False)
    per4 = Column(String(255), server_default='', nullable=False)
    voltage1 = Column(String(255), server_default='', nullable=False)
    voltage2 = Column(String(255), server_default='', nullable=False)
    temp1 = Column(String(255), server_default='', nullable=False)
    temp2 = Column(String(255), server_default='', nullable=False)
    temp3 = Column(String(255), server_default='', nullable=False)
    temp4 = Column(String(255), server_default='', nullable=False)
    temp5 = Column(String(255), server_default='', nullable=False)
    temp6 = Column(String(255), server_default='', nullable=False)
    temp7 = Column(String(255), server_default='', nullable=False)
    temp8 = Column(String(255), server_default='', nullable=False)
    temp9 = Column(String(255), server_default='', nullable=False)
    temp10 = Column(String(255), server_default='', nullable=False)
    temp11 = Column(String(255), server_default='', nullable=False)
    temp12 = Column(String(255), server_default='', nullable=False)
    valve1 = Column(String(255), server_default='', nullable=False)
    valve2 = Column(String(255), server_default='', nullable=False)
    valve3 = Column(String(255), server_default='', nullable=False)
    valve4 = Column(String(255), server_default='', nullable=False)
    valve5 = Column(String(255), server_default='', nullable=False)
    valve6 = Column(String(255), server_default='', nullable=False)
    valve7 = Column(String(255), server_default='', nullable=False)
    valve8 = Column(String(255), server_default='', nullable=False)
    valve9 = Column(String(255), server_default='', nullable=False)
    valve10 = Column(String(255), server_default='', nullable=False)
    valve11 = Column(String(255), server_default='', nullable=False)
    valve12 = Column(String(255), server_default='', nullable=False)
    valve13 = Column(String(255), server_default='', nullable=False)
    valve14 = Column(String(255), server_default='', nullable=False)
    valve15 = Column(String(255), server_default='', nullable=False)
    valve16 = Column(String(255), server_default='', nullable=False)
    flow1 = Column(String(255), server_default='', nullable=False)
    flow2 = Column(String(255), server_default='', nullable=False)
    dens1 = Column(String(255), server_default='', nullable=False)
    dens2 = Column(String(255), server_default='', nullable=False)
    dens3 = Column(String(255), server_default='', nullable=False)
    dens4 = Column(String(255), server_default='', nullable=False)
    dens5 = Column(String(255), server_default='', nullable=False)
    dens6 = Column(String(255), server_default='', nullable=False)
    dens7 = Column(String(255), server_default='', nullable=False)
    dens8 = Column(String(255), server_default='', nullable=False)
    vacuum1 = Column(String(255), server_default='', nullable=False)
    vacuum2 = Column(String(255), server_default='', nullable=False)
    vacuum3 = Column(String(255), server_default='', nullable=False)
    vacuum4 = Column(String(255), server_default='', nullable=False)
    inverter_frequency = Column(String(255), server_default='', nullable=False)
    inverter_current = Column(String(255), server_default='', nullable=False)
    pump1 = Column(String(255), server_default='', nullable=False)
    pump2 = Column(String(255), server_default='', nullable=False)
    warn = Column(String(255), server_default='', nullable=False)

class DeviceWarnRelation(BaseModel):
    '报警关联设备'

    __tablename__ = 'device_warn_relation'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cpu_id = Column(String(64), server_default='', nullable=False, index=True)
    relation_warn_1 = Column(String(64), server_default='', nullable=False, index=True)
    relation_warn_2 = Column(String(64), server_default='', nullable=False, index=True)
    relation_warn_3 = Column(String(64), server_default='', nullable=False, index=True)
    relation_warn_4 = Column(String(64), server_default='', nullable=False, index=True)
    relation_warn_5 = Column(String(64), server_default='', nullable=False, index=True)
