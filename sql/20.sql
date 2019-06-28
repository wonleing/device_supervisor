-- 给 corp 添加联系人和电话字段 

begin;
alter table `corp` add column `contacts` varchar(32) not null default '';
alter table `corp` add column `tel` varchar(32) not null default '';
commit;
