begin;
CREATE TABLE `supply` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `serial_number` varchar(64) NOT NULL DEFAULT '',
  `cpu_id` varchar(64) NOT NULL DEFAULT '',
  `medium` varchar(30) NOT NULL DEFAULT '',
  `before` decimal(9,2) NOT NULL DEFAULT '0.00',
  `after` decimal(9,2) NOT NULL DEFAULT '0.00',
  `add` decimal(9,2) NOT NULL DEFAULT '0.00',
  `adjust` decimal(9,2) NOT NULL DEFAULT '0.00',
  `create` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB CHARSET=utf8;

CREATE INDEX ix_supply_cpu_id ON supply (cpu_id);
CREATE INDEX ix_supply_serial_number ON supply (serial_number);
CREATE INDEX ix_supply_medium ON supply (`medium`);
CREATE INDEX ix_supply_create ON supply (`create`);



CREATE TABLE supply_print(
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `serial_number` varchar(64) NOT NULL DEFAULT '',
  `supply` bigint(20) NOT NULL,
  `cpu_id` varchar(64) NOT NULL DEFAULT '',
  `create` bigint(20) NOT NULL DEFAULT '0',
  `medium` varchar(30) NOT NULL DEFAULT '',
  `supplier` varchar(64) NOT NULL DEFAULT '',
  `end_user` varchar(64) NOT NULL DEFAULT '',
  `before` decimal(9,2) NOT NULL DEFAULT '0.00',
  `after` decimal(9,2) NOT NULL DEFAULT '0.00',
  `adjust` decimal(9,2) NOT NULL DEFAULT '0.00',
  `unit_price` bigint(20) NOT NULL,
  `total_cost` bigint(20) NOT NULL,
  `operator` varchar(40) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  FOREIGN KEY(supply) REFERENCES supply (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

CREATE INDEX ix_supply_print_serial_number ON supply_print (serial_number);
CREATE INDEX ix_supply_print_supply ON supply_print (supply);
CREATE INDEX ix_supply_print_cpu_id ON supply_print (cpu_id);
CREATE INDEX ix_supply_print_create ON supply_print (`create`);
CREATE INDEX ix_supply_print_operator ON supply_print (`operator`);
CREATE INDEX ix_supply_print_unit_price ON supply_print (`unit_price`);
CREATE INDEX ix_supply_print_medium ON supply_print (`medium`);
CREATE INDEX ix_supply_print_supplier ON supply_print (`supplier`);
CREATE INDEX ix_supply_print_end_user ON supply_print (`end_user`);
commit;
