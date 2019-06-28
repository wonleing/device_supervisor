begin; 
CREATE TABLE sms (
        id BIGINT NOT NULL AUTO_INCREMENT, 
        type VARCHAR(16) NOT NULL DEFAULT 'normal', 
        status VARCHAR(16) NOT NULL DEFAULT 'normal', 
        `create` BIGINT NOT NULL DEFAULT '0', 
        last BIGINT NOT NULL DEFAULT '0',
        device BIGINT NOT NULL DEFAULT '0',
        content TEXT NOT NULL, 
        target TEXT NOT NULL, 
        PRIMARY KEY (id)
) ENGINE=InnoDB CHARSET=utf8;
CREATE INDEX ix_sms_type ON sms (type);
CREATE INDEX ix_sms_status ON sms (status);
CREATE INDEX ix_sms_create ON sms (`create`);
commit;
