begin;
alter table device add column data_update bigint(20) not null default '0';
alter table `user` add column address varchar(255) not null default '';
commit;
