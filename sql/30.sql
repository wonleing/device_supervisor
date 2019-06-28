CREATE TABLE product_device (
    id BIGINT NOT NULL AUTO_INCREMENT,
    product BIGINT NOT NULL,
    device BIGINT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(product) REFERENCES aliyun_product (id),
    FOREIGN KEY(device) REFERENCES device (id)
)ENGINE=InnoDB CHARSET=utf8;

CREATE INDEX ix_product_device_device ON product_device (device);
CREATE INDEX ix_product_device_productkey ON product_device (product);