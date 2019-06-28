begin;

CREATE TABLE push (
        id BIGINT NOT NULL AUTO_INCREMENT, 
        type VARCHAR(16) NOT NULL DEFAULT 'normal', 
        status VARCHAR(16) NOT NULL DEFAULT 'normal', 
        `create` BIGINT NOT NULL DEFAULT '0', 
        `last` BIGINT NOT NULL DEFAULT '0', 
        title VARCHAR(64) NOT NULL DEFAULT '', 
        content TEXT NOT NULL, 
        target TEXT NOT NULL, 
        PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;


CREATE INDEX ix_push_status ON push (status);
CREATE INDEX ix_push_type ON push (type);
CREATE INDEX ix_push_create ON push (`create`);

commit;


