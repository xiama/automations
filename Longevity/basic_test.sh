###step 1 : Create app
app_create $1
url_check $app_name

###step 2 : hot_deploy 
./hot_deply.sh $app_name

###step 3 : cartridge_add mysql
run cartridge_add mysql-5.1 $app_name

###step 4 : mysql insert
app_path=`rhc app show -a $1 -p$passwd|grep -A0 "SSH:"|awk '{print $2}'`
echo "$1 SSH path is : $app_path"
cartridge_dir=`ssh $app_path env|grep OPENSHIFT_PRIMARY_CARTRIDGE_DIR|cut -d'=' -f2`
insert_sql=`create table test(id int(8), name char(20));insert into test values('0','openshifit');insert into test values('1','nsun');select * from test;`
ssh $app_path "echo '$aaa' > '$cartridge_dir'/mysql_insert.sql"

###step* : app operation test
app_operations="status start restart reload stop force-stop tidy delete"
run app_oper_testing $app_name
