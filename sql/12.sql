begin;
CREATE TABLE z_device_data_0000 (
    id BIGINT NOT NULL AUTO_INCREMENT,
    device_id BIGINT NOT NULL,
    cpu_id VARCHAR(64) NOT NULL DEFAULT '',
    `create` BIGINT NOT NULL DEFAULT '0',
    `time` BIGINT NOT NULL DEFAULT '0',
    devid text not null,

    lng decimal(9,6) not null default '0',
    lat decimal(9,6) not null default '0',

    weight1 decimal(9,4) not null default '0',
    weight2 decimal(9,4) not null default '0',
    weight3 decimal(9,4) not null default '0',
    weight4 decimal(9,4) not null default '0',

    height1 decimal(9,4) not null default '0',
    height2 decimal(9,4) not null default '0',
    height3 decimal(9,4) not null default '0',
    height4 decimal(9,4) not null default '0',

    pressure1 decimal(9,4) not null default '0',
    pressure2 decimal(9,4) not null default '0',
    pressure3 decimal(9,4) not null default '0',
    pressure4 decimal(9,4) not null default '0',
    pressure5 decimal(9,4) not null default '0',
    pressure6 decimal(9,4) not null default '0',
    pressure7 decimal(9,4) not null default '0',
    pressure8 decimal(9,4) not null default '0',

    diff_pressure1 decimal(9,4) not null default '0',
    diff_pressure2 decimal(9,4) not null default '0',
    diff_pressure3 decimal(9,4) not null default '0',
    diff_pressure4 decimal(9,4) not null default '0',

    per1 decimal(9,4) not null default '0',
    per2 decimal(9,4) not null default '0',
    per3 decimal(9,4) not null default '0',
    per4 decimal(9,4) not null default '0',

    voltage1 decimal(9,4) not null default '0',
    voltage2 decimal(9,4) not null default '0',

    temp1 decimal(9,4) not null default '0',
    temp2 decimal(9,4) not null default '0',
    temp3 decimal(9,4) not null default '0',
    temp4 decimal(9,4) not null default '0',
    temp5 decimal(9,4) not null default '0',
    temp6 decimal(9,4) not null default '0',
    temp7 decimal(9,4) not null default '0',
    temp8 decimal(9,4) not null default '0',
    temp9 decimal(9,4) not null default '0',
    temp10 decimal(9,4) not null default '0',
    temp11 decimal(9,4) not null default '0',
    temp12 decimal(9,4) not null default '0',

    valve1 decimal(9,4) not null default '0',
    valve2 decimal(9,4) not null default '0',
    valve3 decimal(9,4) not null default '0',
    valve4 decimal(9,4) not null default '0',
    valve5 decimal(9,4) not null default '0',
    valve6 decimal(9,4) not null default '0',
    valve7 decimal(9,4) not null default '0',
    valve8 decimal(9,4) not null default '0',
    valve9 decimal(9,4) not null default '0',
    valve10 decimal(9,4) not null default '0',
    valve11 decimal(9,4) not null default '0',
    valve12 decimal(9,4) not null default '0',
    valve13 decimal(9,4) not null default '0',
    valve14 decimal(9,4) not null default '0',
    valve15 decimal(9,4) not null default '0',
    valve16 decimal(9,4) not null default '0',

    flow1 decimal(15,4) not null default '0',
    flow2 decimal(15,4) not null default '0',

    dens1 decimal(9,4) not null default '0',
    dens2 decimal(9,4) not null default '0',
    dens3 decimal(9,4) not null default '0',
    dens4 decimal(9,4) not null default '0',
    dens5 decimal(9,4) not null default '0',
    dens6 decimal(9,4) not null default '0',
    dens7 decimal(9,4) not null default '0',
    dens8 decimal(9,4) not null default '0',

    vacuum1 decimal(9,4) not null default '0',
    vacuum2 decimal(9,4) not null default '0',
    vacuum3 decimal(9,4) not null default '0',
    vacuum4 decimal(9,4) not null default '0',

    inverter_frequency decimal(9,4) not null default '0',
    inverter_current decimal(9,4) not null default '0',

    pump1 decimal(9,4) not null default '0',
    pump2 decimal(9,4) not null default '0',

    warn decimal(9,4) not null default '0',

    PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;

create table z_device_data_1707 like z_device_data_0000;
create table z_device_data_1708 like z_device_data_0000;
create table z_device_data_1709 like z_device_data_0000;
create table z_device_data_1710 like z_device_data_0000;
create table z_device_data_1711 like z_device_data_0000;
create table z_device_data_1712 like z_device_data_0000;

create table z_device_data_1801 like z_device_data_0000;
create table z_device_data_1802 like z_device_data_0000;
create table z_device_data_1803 like z_device_data_0000;
create table z_device_data_1804 like z_device_data_0000;
create table z_device_data_1805 like z_device_data_0000;
create table z_device_data_1806 like z_device_data_0000;
create table z_device_data_1807 like z_device_data_0000;
create table z_device_data_1808 like z_device_data_0000;
create table z_device_data_1809 like z_device_data_0000;
create table z_device_data_1810 like z_device_data_0000;
create table z_device_data_1811 like z_device_data_0000;
create table z_device_data_1812 like z_device_data_0000;

create table z_device_data_1901 like z_device_data_0000;
create table z_device_data_1902 like z_device_data_0000;
create table z_device_data_1903 like z_device_data_0000;
create table z_device_data_1904 like z_device_data_0000;
create table z_device_data_1905 like z_device_data_0000;
create table z_device_data_1906 like z_device_data_0000;
create table z_device_data_1907 like z_device_data_0000;
create table z_device_data_1908 like z_device_data_0000;
create table z_device_data_1909 like z_device_data_0000;
create table z_device_data_1910 like z_device_data_0000;
create table z_device_data_1911 like z_device_data_0000;
create table z_device_data_1912 like z_device_data_0000;


commit;
