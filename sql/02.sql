begin;
alter table `action_log` modify column `type` varchar(64);
commit;
