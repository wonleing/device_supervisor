begin; 
CREATE TABLE device_attribute (
        id BIGINT NOT NULL AUTO_INCREMENT, 
        cpu_id VARCHAR(64) NOT NULL DEFAULT '', 
        code VARCHAR(128) NOT NULL DEFAULT '', 
        name VARCHAR(128) NOT NULL DEFAULT '', 
        value VARCHAR(512) NOT NULL DEFAULT '',
        `type` varchar(128) NOT NULL DEFAULT 'conf',
        `edit` int(10) NOT NULL DEFAULT '0',
        `user` int(10) NOT NULL DEFAULT '0',
        `product` int(10) NOT NULL DEFAULT '0',
        PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;

CREATE INDEX ix_device_attribute_cpu_id ON device_attribute (cpu_id);
CREATE INDEX ix_device_attribute_code ON device_attribute (code);
commit;
