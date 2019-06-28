-- 添加用户和设备的关系

CREATE TABLE user_device (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    user BIGINT NOT NULL, 
    device BIGINT NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user) REFERENCES user (id), 
    FOREIGN KEY(device) REFERENCES device (id)
)ENGINE=InnoDB CHARSET=utf8;

CREATE INDEX ix_user_device_device ON user_device (device);
CREATE INDEX ix_user_device_user ON user_device (user);

