-- 维度中的横线去掉

begin;
update `dimension` set name = '日期小时' where code = 'date_hour';
update `dimension` set name = '年月' where code = 'year_month';
update `dimension` set name = '年周' where code = 'year_week';
update `dimension` set name = 'MYSQLID' where code = 'mysql_id';
commit;
