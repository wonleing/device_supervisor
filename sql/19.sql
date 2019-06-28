-- 创建 message 的 2 张表

begin;

CREATE TABLE message (
        id BIGINT NOT NULL AUTO_INCREMENT, 
        type VARCHAR(16) NOT NULL DEFAULT 'normal', 
        status VARCHAR(16) NOT NULL DEFAULT 'normal', 
        `create` BIGINT NOT NULL DEFAULT '0', 
        title VARCHAR(64) NOT NULL DEFAULT '', 
        content TEXT NOT NULL, 
        PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;

CREATE INDEX ix_message_type ON message (type);
CREATE INDEX ix_message_create ON message (`create`);
CREATE INDEX ix_message_status ON message (status);



CREATE TABLE user_message (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    type VARCHAR(16) NOT NULL DEFAULT 'normal', 
    status VARCHAR(16) NOT NULL DEFAULT 'normal', 
    user BIGINT NOT NULL, 
    message BIGINT NOT NULL, 
    `update` BIGINT NOT NULL DEFAULT '0', 
    PRIMARY KEY (id), 
    FOREIGN KEY(user) REFERENCES user (id), 
    FOREIGN KEY(message) REFERENCES message (id)
)ENGINE=InnoDB CHARSET=utf8;


CREATE INDEX ix_user_message_message ON user_message (message);
CREATE INDEX ix_user_message_type ON user_message (type);
CREATE INDEX ix_user_message_status ON user_message (status);
CREATE INDEX ix_user_message_user ON user_message (user);

commit;

