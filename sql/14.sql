begin;
CREATE TABLE field_alias (
    id BIGINT NOT NULL AUTO_INCREMENT,
    cpu_id VARCHAR(64) NOT NULL DEFAULT '',

    lng varchar(255) not null default '',
    lat varchar(255) not null default '',

    weight1 varchar(255) not null default '',
    weight2 varchar(255) not null default '',
    weight3 varchar(255) not null default '',
    weight4 varchar(255) not null default '',

    height1 varchar(255) not null default '',
    height2 varchar(255) not null default '',
    height3 varchar(255) not null default '',
    height4 varchar(255) not null default '',

    pressure1 varchar(255) not null default '',
    pressure2 varchar(255) not null default '',
    pressure3 varchar(255) not null default '',
    pressure4 varchar(255) not null default '',
    pressure5 varchar(255) not null default '',
    pressure6 varchar(255) not null default '',
    pressure7 varchar(255) not null default '',
    pressure8 varchar(255) not null default '',

    diff_pressure1 varchar(255) not null default '',
    diff_pressure2 varchar(255) not null default '',
    diff_pressure3 varchar(255) not null default '',
    diff_pressure4 varchar(255) not null default '',

    per1 varchar(255) not null default '',
    per2 varchar(255) not null default '',
    per3 varchar(255) not null default '',
    per4 varchar(255) not null default '',

    voltage1 varchar(255) not null default '',
    voltage2 varchar(255) not null default '',

    temp1 varchar(255) not null default '',
    temp2 varchar(255) not null default '',
    temp3 varchar(255) not null default '',
    temp4 varchar(255) not null default '',
    temp5 varchar(255) not null default '',
    temp6 varchar(255) not null default '',
    temp7 varchar(255) not null default '',
    temp8 varchar(255) not null default '',
    temp9 varchar(255) not null default '',
    temp10 varchar(255) not null default '',
    temp11 varchar(255) not null default '',
    temp12 varchar(255) not null default '',

    valve1 varchar(255) not null default '',
    valve2 varchar(255) not null default '',
    valve3 varchar(255) not null default '',
    valve4 varchar(255) not null default '',
    valve5 varchar(255) not null default '',
    valve6 varchar(255) not null default '',
    valve7 varchar(255) not null default '',
    valve8 varchar(255) not null default '',
    valve9 varchar(255) not null default '',
    valve10 varchar(255) not null default '',
    valve11 varchar(255) not null default '',
    valve12 varchar(255) not null default '',
    valve13 varchar(255) not null default '',
    valve14 varchar(255) not null default '',
    valve15 varchar(255) not null default '',
    valve16 varchar(255) not null default '',

    flow1 varchar(255) not null default '',
    flow2 varchar(255) not null default '',

    dens1 varchar(255) not null default '',
    dens2 varchar(255) not null default '',
    dens3 varchar(255) not null default '',
    dens4 varchar(255) not null default '',
    dens5 varchar(255) not null default '',
    dens6 varchar(255) not null default '',
    dens7 varchar(255) not null default '',
    dens8 varchar(255) not null default '',

    vacuum1 varchar(255) not null default '',
    vacuum2 varchar(255) not null default '',
    vacuum3 varchar(255) not null default '',
    vacuum4 varchar(255) not null default '',

    inverter_frequency varchar(255) not null default '',
    inverter_current varchar(255) not null default '',

    pump1 varchar(255) not null default '',
    pump2 varchar(255) not null default '',

    warn varchar(255) not null default '',

    PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;

commit;
