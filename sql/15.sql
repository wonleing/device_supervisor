begin; 

CREATE TABLE rule (
        id BIGINT NOT NULL AUTO_INCREMENT, 
        type VARCHAR(16) NOT NULL DEFAULT 'normal', 
        status VARCHAR(16) NOT NULL DEFAULT 'normal', 
        name VARCHAR(32) NOT NULL DEFAULT '', 
        code VARCHAR(32) NOT NULL DEFAULT '', 
        field VARCHAR(32) NOT NULL DEFAULT '', 
        op VARCHAR(8) NOT NULL DEFAULT '', 
        value VARCHAR(32) NOT NULL DEFAULT '', 
        PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;


CREATE INDEX ix_rule_type ON rule (`type`);
CREATE INDEX ix_rule_status ON rule (`status`);
CREATE INDEX ix_rule_field ON rule (`field`);
CREATE INDEX ix_rule_code ON rule (`code`);


CREATE TABLE device_rule (
        id BIGINT NOT NULL AUTO_INCREMENT, 
        device BIGINT NOT NULL, 
        rule BIGINT NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(device) REFERENCES device (id), 
        FOREIGN KEY(rule) REFERENCES rule (id)
)ENGINE=InnoDB CHARSET=utf8;


CREATE INDEX ix_device_rule_device ON device_rule (device);
CREATE INDEX ix_device_rule_rule ON device_rule (`rule`);

commit;
