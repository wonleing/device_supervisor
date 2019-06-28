-- 维度指标
begin;

insert into fact (`code`, `name`, `table`) values ('monitor_v1', '上报数据', 'monitor_v1');

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
('valve', '阀状态', 'valve'),
('jiezhi', '介质ID', 'jiezhi'),
('jiezhi_name', '介质名', 'jiezhi_name'),
('corp_id', '企业ID', 'corp_id'),
('corp_name', '企业名', 'corp_name'),
('mysql_id', 'MYSQL-ID', 'mysql_id'),
('lng', '经度', 'lng'),
('lat', '纬度', 'lat');

insert into metric (`code`, `name`, `column`, `aggre`) values 
('weight_avg', '平均重量', 'weight', 'avg'),
('pressure_avg', '平均气压', 'pressure', 'avg'),
('per_avg', '平均容积百分比', 'per', 'avg'),
('voltage_avg', '平均电池电压', 'voltage', 'avg'),
('env_temp_avg', '平均环境温度', 'env_temp', 'avg'),
('tank_temp_avg', '平均罐体温度', 'tank_temp', 'avg'),
('flow_avg', '平均总流量', 'flow', 'avg'),
('device_count', '设备数', 'cpuid', 'uniq'),
('row_count', '条目数', 'mysql_id', 'count');

insert into metric (`code`, `name`, `column`, `aggre`) values 
('weight_min', '最小重量', 'weight', 'min'),
('pressure_min', '最小气压', 'pressure', 'min'),
('per_min', '最小容积百分比', 'per', 'min'),
('voltage_min', '最小电池电压', 'voltage', 'min'),
('env_temp_min', '最小环境温度', 'env_temp', 'min'),
('tank_temp_min', '最小罐体温度', 'tank_temp', 'min'),
('flow_min', '最小总流量', 'flow', 'min');

insert into metric (`code`, `name`, `column`, `aggre`) values 
('weight_max', '最大重量', 'weight', 'max'),
('pressure_max', '最大气压', 'pressure', 'max'),
('per_max', '最大容积百分比', 'per', 'max'),
('voltage_max', '最大电池电压', 'voltage', 'max'),
('env_temp_max', '最大环境温度', 'env_temp', 'max'),
('tank_temp_max', '最大罐体温度', 'tank_temp', 'max'),
('flow_max', '最大总流量', 'flow', 'max');

commit;

