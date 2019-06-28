CREATE TABLE `aliyun_product` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `status` varchar(16) NOT NULL DEFAULT 'normal',
  `name` varchar(32) NOT NULL DEFAULT '',
  `create` bigint(20) NOT NULL DEFAULT '0',
  `field_alias` varchar(32) NOT NULL DEFAULT '',
  `productkey` varchar(32) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `ix_aliyun_product_name` (`name`),
  KEY `ix_aliyun_product_status` (`status`),
  KEY `ix_aliyun_product_id` (`productkey`)
) ENGINE=InnoDB AUTO_INCREMENT=278 DEFAULT CHARSET=utf8