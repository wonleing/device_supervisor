-- 重置 query 中的相关数据 

begin;

drop table fact_resource;

CREATE TABLE `fact_resource` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `type` varchar(16) NOT NULL DEFAULT 'dimension',
  `fact` varchar(32) NOT NULL,
  `code` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_fact_resource_fact` (`fact`),
  KEY `ix_fact_resource_type` (`type`),
  KEY `ix_fact_resource_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


delete from fact;
delete from fact_resource;
delete from metric;
delete from dimension;


insert into fact (`code`, `name`, `table`) values ('monitor_v2', '上报数据', 'monitor_v2');


insert into dimension (`code`, `name`, `column`) values
('gmt_date', '日期', 'gmt_date'),
('gmt', '时间', 'gmt'),
('year', '年', 'year'),
('month', '月', 'month'),
('day', '日', 'day'),
('hour', '小时', 'hour'),
('date_hour', '日期-小时', 'date_hour'),
('year_month', '年-月', 'year_month'),
('week', '星期', 'week'),
('week_number', '年中的周序数', 'week_number'),
('year_week', '年-周', 'year_week'),

('cpuid', 'CPUID', 'cpuid'),
('devid', 'DEVID', 'devid'),
('corp_id', '企业ID', 'corp_id'),
('corp_name', '企业名', 'corp_name'),
('mysql_id', 'MYSQL-ID', 'mysql_id'),
('lng', '经度', 'lng'),
('lat', '纬度', 'lat');


insert into metric (`code`, `name`, `column`, `aggre`) values 
('device_count', '设备数', 'cpuid', 'uniq'),
('row_count', '条目数', 'mysql_id', 'count');

commit;

