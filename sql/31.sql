alter table passport add login_time bigint(20) NOT NULL DEFAULT '0';
alter table passport add openid varchar(80) NOT NULL DEFAULT '';

alter table device add productkey varchar(32) NOT NULL DEFAULT '';
alter table device add `device_name` varchar(64) NOT NULL DEFAULT '';
alter table device add `data_update` bigint(20) NOT NULL DEFAULT '0';

alter table device_attribute add productkey VARCHAR(64) NOT NULL DEFAULT '';
alter table user_device add role varchar(8) NOT NULL DEFAULT 'normal';

alter TABLE device_package_record add remarks VARCHAR(255) not NULL DEFAULT '';

alter table session add email varchar(16) NOT NULL DEFAULT '';