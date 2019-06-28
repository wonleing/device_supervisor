-- analytics 相关的表

begin;

CREATE TABLE `calculate_metric` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `status` varchar(16) NOT NULL DEFAULT 'normal',
  `code` varchar(32) NOT NULL DEFAULT '',
  `name` varchar(32) NOT NULL DEFAULT '',
  `expression` varchar(128) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `ix_calculate_metric_status` (`status`),
  KEY `ix_calculate_metric_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `dimension` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `status` varchar(16) NOT NULL DEFAULT 'normal',
  `code` varchar(32) NOT NULL DEFAULT '',
  `name` varchar(32) NOT NULL DEFAULT '',
  `column` varchar(32) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `ix_dimension_code` (`code`),
  KEY `ix_dimension_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `fact` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `status` varchar(16) NOT NULL DEFAULT 'normal',
  `code` varchar(32) NOT NULL DEFAULT '',
  `name` varchar(32) NOT NULL DEFAULT '',
  `table` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_fact_status` (`status`),
  KEY `ix_fact_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `fact_resource` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `type` varchar(16) NOT NULL DEFAULT 'dimension',
  `fact` bigint(20) NOT NULL,
  `code` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_fact_resource_fact` (`fact`),
  KEY `ix_fact_resource_type` (`type`),
  KEY `ix_fact_resource_code` (`code`),
  CONSTRAINT `fact_resource_ibfk_1` FOREIGN KEY (`fact`) REFERENCES `fact` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `metric` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `status` varchar(16) NOT NULL DEFAULT 'normal',
  `code` varchar(32) NOT NULL DEFAULT '',
  `name` varchar(32) NOT NULL DEFAULT '',
  `column` varchar(32) NOT NULL DEFAULT '',
  `aggre` varchar(32) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `ix_metric_code` (`code`),
  KEY `ix_metric_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

commit;
