-- 添加需要的一些 system 中的值 

begin;
    insert into `system` (`name`, `value`) values ( 'front_admin_template', 'hello' );
    insert into `system` (`name`, `value`) values ( 'front_admin_version', '0.1.0' );
    insert into `system` (`name`, `value`) values ( 'front_admin_env', 'prod' );
commit;

