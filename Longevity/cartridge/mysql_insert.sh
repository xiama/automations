#!/bin/bash
mysql -uroot<<EOF
use $1
create table test(id int(8), name char(20));
insert into test values('0','openshifit');
insert into test values('1','nsun');
select * from test;
EOF

#drop table test
#mysql -Druby0 "create table test(id int(8), name char(20));"
#mysql -Druby0 -e "create table test(id int(8), name char(20));"
#mysql -Druby0 -e "insert into test values('0','openshifit');"
