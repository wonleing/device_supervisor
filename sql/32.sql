begin;
CREATE TABLE product_attribute (
        id BIGINT NOT NULL AUTO_INCREMENT,
        productkey bigint(20) NOT NULL,
        code VARCHAR(128) NOT NULL DEFAULT '',
        name VARCHAR(128) NOT NULL DEFAULT '',
        value VARCHAR(512) NOT NULL DEFAULT '',
        `edit` bigint(10) NOT NULL DEFAULT '0',
        `type` varchar(128) NOT NULL DEFAULT 'conf',
        PRIMARY KEY (id),
        FOREIGN KEY(productkey) REFERENCES aliyun_product (id)
)ENGINE=InnoDB CHARSET=utf8;

CREATE INDEX ix_product_attribute_cpu_id ON product_attribute (productkey);
CREATE INDEX ix_product_attribute_code ON product_attribute (code);
commit;