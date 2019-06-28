begin;
CREATE TABLE information (
        id BIGINT NOT NULL AUTO_INCREMENT,
        title VARCHAR(512) NOT NULL DEFAULT '',
        picture VARCHAR(512) NOT NULL DEFAULT '',
        time BIGINT  NOT NULL DEFAULT '0',
        url varchar(512) NOT NULL DEFAULT '',
        PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;

CREATE TABLE suggestionback (
        id BIGINT NOT NULL AUTO_INCREMENT,
        title VARCHAR(32)NOT NULL  DEFAULT '',
        content VARCHAR(64) NOT NULL DEFAULT '',
        time BIGINT NOT NULL DEFAULT '0',
        type VARCHAR(16) NOT NULL DEFAULT '',
        process VARCHAR(16) NOT NULL DEFAULT '未处理',
        handler VARCHAR(16) NOT NULL DEFAULT '',
        publisher VARCHAR(16) NOT NULL DEFAULT '',
        regist VARCHAR(64) NOT NULL DEFAULT '',
        PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;

CREATE TABLE demandpub (
        id BIGINT NOT NULL AUTO_INCREMENT,
        title VARCHAR(32)NOT NULL  DEFAULT '',
        content VARCHAR(64) NOT NULL DEFAULT '',
        time BIGINT NOT NULL DEFAULT '0',
        type VARCHAR(16) NOT NULL DEFAULT '',
        process VARCHAR(16) NOT NULL DEFAULT '未处理',
        handler VARCHAR(16) NOT NULL DEFAULT '',
        publisher VARCHAR(16) NOT NULL DEFAULT '',
        regist VARCHAR(64) NOT NULL DEFAULT '',
        PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;

CREATE TABLE invoice (
        id BIGINT NOT NULL AUTO_INCREMENT,
        username VARCHAR(32) NOT NULL DEFAULT '',
        corpname VARCHAR(32) NOT NULL DEFAULT '',
        taxnumber VARCHAR(20) NOT NULL DEFAULT '',
        time BIGINT  NOT NULL DEFAULT '0',
        register_address VARCHAR(255)  NOT NULL DEFAULT '0',
        telephone VARCHAR(11) NOT NULL DEFAULT '',
        bankname VARCHAR(32) NOT NULL DEFAULT '',
        banknumber VARCHAR(19) NOT NULL DEFAULT '',
        PRIMARY KEY (id)
)ENGINE=InnoDB CHARSET=utf8;
commit;

begin ;
CREATE TABLE app_version(
        id BIGINT NOT NULL AUTO_INCREMENT,
        version VARCHAR(32) NOT NULL DEFAULT '',
        comment VARCHAR(64) NOT NULL DEFAULT '',
        time BIGINT NOT NULL DEFAULT '0',
        updater VARCHAR(16) NOT NULL DEFAULT '',
        PRIMARY KEY (id)
       )ENGINE=InnoDB CHARSET=utf8;
create index ix_app_version_time
  on warn_contrast (time);

commit ;