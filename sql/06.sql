begin;
alter table device_session add column seq int not null default '0' ;
commit;
