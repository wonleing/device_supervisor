begin;
alter table device_session change column mac cpu_id varchar(64) not null default '' ;
alter table device_session drop index ix_device_session_mac;
alter table device_session add index ix_device_session_cpu_id (cpu_id);
commit;

