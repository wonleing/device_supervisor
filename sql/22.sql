-- corp_user 添加 status 

begin;
alter table `corp_user` add column `status` varchar(8) not null default 'normal';
create index `ix_corp_user_status` on `corp_user`(`status`);
commit;
