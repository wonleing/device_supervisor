begin;
CREATE TABLE z_device_data_0000 (
    id BIGINT NOT NULL AUTO_INCREMENT,
    device_id BIGINT NOT NULL,
    cpu_id VARCHAR(64) NOT NULL DEFAULT '',
    `create` BIGINT NOT NULL DEFAULT '0',
    devid text not null,
    jiezhi text not null,
    lng decimal(9,6) not null default '0',
    lat decimal(9,6) not null default '0',
    weight decimal(9,4) not null default '0',
    pressure decimal(9,4) not null default '0',
    per decimal(9,4) not null default '0',
    voltage decimal(9,4) not null default '0',
    env_temp decimal(9,4) not null default '0',
    tank_temp decimal(9,4) not null default '0',
    valve decimal(9,4) not null default '0',
    flow decimal(9,4) not null default '0',
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
