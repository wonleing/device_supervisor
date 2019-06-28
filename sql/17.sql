-- 预警

begin;

CREATE TABLE warn (
        id BIGINT NOT NULL AUTO_INCREMENT, 
        type VARCHAR(16) NOT NULL DEFAULT 'normal', 
        status VARCHAR(16) NOT NULL DEFAULT 'normal', 
        cpu_id VARCHAR(64) NOT NULL DEFAULT '', 
        code VARCHAR(16) NOT NULL DEFAULT '', 
        content VARCHAR(512) NOT NULL DEFAULT '', 
        time BIGINT NOT NULL DEFAULT '0', 
        `create` BIGINT NOT NULL DEFAULT '0', 
        PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;

CREATE INDEX ix_warn_type ON warn (type);
CREATE INDEX ix_warn_status ON warn (status);
CREATE INDEX ix_warn_cpu_id ON warn (cpu_id);

CREATE TABLE warn_contrast(
        id BIGINT NOT NULL AUTO_INCREMENT,
        code VARCHAR(16) NOT NULL DEFAULT '',
        content VARCHAR(64) NOT NULL DEFAULT '',
       `create` bigint(20) NOT NULL DEFAULT '0',
        PRIMARY KEY (id)

)ENGINE=InnoDB CHARSET=utf8;

commit;


