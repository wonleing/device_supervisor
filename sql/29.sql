CREATE TABLE `topiclog`(
    id BIGINT auto_increment primary key,
    name varchar(64) default '' not null,
    topic varchar(64) default '' not null,
    message varchar(64) default 0,
    updatetime BIGINT not null default 0,
    remarks varchar(64) default '',
    messagecount BIGINT(10) default 0,
    productkey varchar(64) default '' not null,
    devicename varchar(64) default '' not null
)ENGINE=InnoDB DEFAULT CHARSET=utf8;