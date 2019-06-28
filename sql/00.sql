
BEGIN;

CREATE TABLE `user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `type` varchar(16) NOT NULL DEFAULT 'normal',
  `status` varchar(16) NOT NULL DEFAULT 'normal',
  `name` varchar(32) NOT NULL DEFAULT '',
  `avatar` varchar(128) NOT NULL DEFAULT '',
  `mobile` varchar(11) NOT NULL DEFAULT '',
  `email` varchar(128) NOT NULL DEFAULT '',
  `create` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `ix_user_status` (`status`),
  KEY `ix_user_type` (`type`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

CREATE TABLE `passport` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user` bigint(20) NOT NULL,
  `type` varchar(16) NOT NULL DEFAULT 'normal',
  `username` varchar(32) NOT NULL DEFAULT '',
  `password` varchar(80) NOT NULL DEFAULT '',
  `create` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `ix_passport_user` (`user`),
  KEY `ix_passport_type` (`type`),
  CONSTRAINT `passport_ibfk_1` FOREIGN KEY (`user`) REFERENCES `user` (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

CREATE TABLE `corp` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `type` varchar(16) NOT NULL DEFAULT 'normal',
  `status` varchar(16) NOT NULL DEFAULT 'normal',
  `name` varchar(32) NOT NULL DEFAULT '',
  `create` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `ix_corp_type` (`type`),
  KEY `ix_corp_status` (`status`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

CREATE TABLE `session` (
  `id` varchar(32) NOT NULL,
  `user` bigint(20) DEFAULT NULL,
  `create` bigint(20) NOT NULL DEFAULT '0',
  `code` varchar(8) NOT NULL DEFAULT '',
  `code_create` bigint(20) NOT NULL DEFAULT '0',
  `code_mobile` varchar(11) NOT NULL DEFAULT '',
  `ip` varchar(64) NOT NULL DEFAULT '',
  `corp` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `corp` (`corp`),
  KEY `ix_session_user` (`user`),
  CONSTRAINT `session_ibfk_1` FOREIGN KEY (`user`) REFERENCES `user` (`id`),
  CONSTRAINT `session_ibfk_2` FOREIGN KEY (`corp`) REFERENCES `corp` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `device` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `type` varchar(16) NOT NULL DEFAULT 'normal',
  `status` varchar(16) NOT NULL DEFAULT 'normal',
  `mac` varchar(64) NOT NULL DEFAULT '',
  `name` varchar(32) NOT NULL DEFAULT '',
  `create` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `ix_device_mac` (`mac`),
  KEY `ix_device_type` (`type`),
  KEY `ix_device_status` (`status`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

 
CREATE TABLE `action_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create` bigint(20) NOT NULL DEFAULT '0',
  `user` bigint(20) NOT NULL,
  `type` varchar(16) NOT NULL DEFAULT 'none',
  `target` text NOT NULL,
  `content` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_action_log_create` (`create`),
  KEY `ix_action_log_user` (`user`),
  KEY `ix_action_log_type` (`type`),
  CONSTRAINT `action_log_ibfk_1` FOREIGN KEY (`user`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `corp_device` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `corp` bigint(20) NOT NULL,
  `device` bigint(20) NOT NULL,
  `create` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `ix_corp_device_device` (`device`),
  KEY `ix_corp_device_corp` (`corp`),
  CONSTRAINT `corp_device_ibfk_1` FOREIGN KEY (`corp`) REFERENCES `corp` (`id`),
  CONSTRAINT `corp_device_ibfk_2` FOREIGN KEY (`device`) REFERENCES `device` (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

CREATE TABLE `corp_user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `corp` bigint(20) NOT NULL,
  `user` bigint(20) NOT NULL,
  `role` varchar(8) NOT NULL DEFAULT 'normal',
  `create` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `ix_corp_user_corp` (`corp`),
  KEY `ix_corp_user_user` (`user`),
  CONSTRAINT `corp_user_ibfk_1` FOREIGN KEY (`corp`) REFERENCES `corp` (`id`),
  CONSTRAINT `corp_user_ibfk_2` FOREIGN KEY (`user`) REFERENCES `user` (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;



CREATE TABLE `system` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `update` bigint(20) NOT NULL DEFAULT '0',
  `name` varchar(64) NOT NULL DEFAULT 'none',
  `value` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_system_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


COMMIT;
