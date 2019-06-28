begin;
CREATE TABLE device_package_record (
        id BIGINT NOT NULL AUTO_INCREMENT, 
        cpu_id VARCHAR(64) NOT NULL DEFAULT '', 
        version VARCHAR(32) NOT NULL DEFAULT '', 
        `update` BIGINT NOT NULL DEFAULT '0', 
        user BIGINT NOT NULL DEFAULT '0', 
        url VARCHAR(255) NOT NULL DEFAULT '', 
        size INTEGER NOT NULL DEFAULT '0',
        `type` varchar(20) NOT NULL,
        PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;

CREATE INDEX ix_device_package_record_update ON device_package_record (`update`);
CREATE INDEX ix_device_package_record_cpu_id ON device_package_record (cpu_id);
CREATE INDEX ix_device_package_record_type ON device_package_record (`type`);

commit;
