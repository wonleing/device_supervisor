begin;
alter table device change column mac cpu_id varchar(64) not null default '' ;
alter table device drop index ix_device_mac;
alter table device add index ix_device_cpu_id (cpu_id);
commit;

