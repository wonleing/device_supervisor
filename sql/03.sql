BEGIN; 
CREATE TABLE device_session (
        id BIGINT NOT NULL AUTO_INCREMENT, 
        session_id VARCHAR(64) NOT NULL DEFAULT '', 
        mac VARCHAR(64) NOT NULL DEFAULT '', 
        `update` BIGINT NOT NULL DEFAULT '0', 
        PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;

CREATE INDEX ix_device_session_session_id ON device_session (session_id);
CREATE INDEX ix_device_session_mac ON device_session (mac);
COMMIT;
