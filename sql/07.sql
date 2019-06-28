begin;
CREATE TABLE device_data (
        id BIGINT NOT NULL AUTO_INCREMENT, 
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

CREATE INDEX ix_device_data_cpu_id ON device_data (cpu_id);
commit;
