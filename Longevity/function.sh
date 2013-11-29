#!/bin/bash

###################################################
# FileName:      common_func.sh
# Author:        <nsun@redhat.com> 
# Description:   provide the common fucntion for all test cases
# Version:       1.0
#*************************************************
### Fuction List:
#rhc_setup                  Setup rhc domain automation
#app_create                Create a new app
#app_snapshot              Snapshot app
#app_restore               Restore app from backup
#app_delete                Delete an new app according to app_name
#app_delete_all            Delete all apps
#cartridge_add             Added on cartridge to assigned app
#cartridge_remove           Remove a cartridge from assigned app
#cartridge_oper_testing    Testing cartridge operations
#add_hot_deploy             Hot_deploy function added to assigned app
#add_disable_auto_scaling   Disable auto scaling function to assigned app
#ssh_app                    Ssh lonin the assigned app
#app_service_pid            Get app services pid
#add_jenkins_client         Added jenkins_client to app
#rest_api                   REST API function,Now we support create/scale-up/scale-down
#rest_api_delete            Delete all using rest api command
#alias_add                  Alias add to an app
#alias_remove               Alias remove from an app
#url_check                  Check the app web service available
#scale_check                Scale-up/scale-down check
#app_oper_testing           App operation testing, stop/reload/start...
#set_running_parameter      Setup testing environment
#rest_api_delete            Delete All(app,domain...)
#alias_add
#alias_remove
#add_mysql_data
#delete_mysql_data
###################################################

. ./common_func.sh
[ -f /usr/bin/expect ] || yum install expect -y
git config --global user.name "Sun Ning"
git config --global user.email "nsun@redhat.com"
pwd=`pwd`
CONFIG_FILE=$pwd/AutoCreate.cfg
#time=`date +%Y%m%d-%H%M%S`

user=`cat ~/.openshift/express.conf|grep default_rhlogin|awk -F= '{print $2}'`
passwd=redhat
domain=`rhc domain show -predhat|sed -n 1p|awk '{print $3}'`
app_number=`rhc domain show -p$passwd|grep  uuid|wc -l`
broker_url=`cat ~/.openshift/express.conf|grep -i libra_server|awk -F= '{print $2}'`


#####################
# $0 $user
# default password is "redhat"
#return value
#####################
rhc_setup()
{
    [ $# -ne 1 ] && echo "Please input correct format. such as: rhc_setup username" && return 1
    domain_name="sun$(date +%m%d)"
    expect -f - <<EOF
    spawn rhc setup
    expect {
        "enter your OpenShift login (email or Red Hat login id):*"  {send "$1\r";exp_continue}
        "Password:"                                                 {send "$passwd\r";exp_continue}
        "Checking for your namespace ... found namespace:*"         {send "$domain_name\r"}
    }
wait
EOF
rhc domain show > /dev/null
[ $? -eq 0 ] && value=0 || value=1
return $value
}


# $0 $app_type $scalable
#####################
app_create()
{
	if [ $# -eq 2 ] && [ "$2" = "-s" ];then
		app_name=${1%-*}${app_number}s
		create_command="rhc app create $app_name $1 -p${passwd} -s --timeout 360" 
	elif [ $# -eq 1 ];then 
		app_name=${1%-*}${app_number}
		create_command="rhc app create $app_name $1 -p${passwd} --timeout 360" 
	fi	
	echo_bold "The new create app NO. is : $app_number "
	echo_bold "$create_command"
	expect -f - <<EOF
	set timeout -1
	spawn $create_command
	expect {
				"Are you *(yes/no)?"	{send "yes\r";exp_continue}
			}
	wait
EOF
	rhc app show $app_name -p${passwd} &>/dev/null
	[ $? -eq 0 ] && value=0 || value=1
	#[ -d $app_name ] && value=0 || value=1
	app_number=$(($app_number + 1))
	echo_blue "Already have $app_number applations created!"
	return "$value"
}

#####################
# $0 $app_name
#####################
app_snapshot()
{
	rhc snapshot save $1 -predhat
}
#####################
# $0 $app_name $app_name
#    Source    Target
#####################
app_restore()
{
	echo_bold "rhc snapshot restore -f ${1}.tar.gz -a $2 -predhat"
	rhc snapshot restore -f ${1}.tar.gz -a $2 -predhat
}

#####################
# $0 $app_name
#####################
app_delete()
{
    echo_bold "The delete app NO. is : $app_number"
	echo_bold "rhc app delete $1 -p${passwd}"
	expect -f - <<EOF
	set timeout -1
	spawn rhc app delete $1 -p${passwd} --timeout 360
	expect {
				"Are you *(yes|no):"	{send "yes\r";exp_continue}
			}
	wait
EOF
	app_number=$(($app_number - 1))
    rhc app show $1 -p${passwd} &>/dev/null
    [ $? -ne 0 ] && value=0 || value=1
    return $value
}
#no parameter
app_delete_all()
{
	apps=`rhc domain show -p${passwd}|grep uuid|awk '{print $1}'`
	echo_blue "All APPs: $apps"
	value=0
	for app in $apps;do
		run app_delete $app
		[ $? -ne 0 ] && value=1 && break
	done
    return $value
}

##########################
# $0 $cartridge_type $app_name
##########################
cartridge_add()
{
	echo_bold "rhc cartridge add $1  -a $2 -p${passwd} --timeout 360"
	rhc cartridge add $1 -a $2 -p${passwd} --timeout 360
    value=$?
    return $value
}
##########################
# $0 $cartridge_type $app_name
##########################
cartridge_remove()
{
	echo_bold "rhc cartridge remove $1 -a $2 -p${passwd} --confirm"
	rhc cartridge remove $1 -a $2 -p${passwd} --confirm
}

#################################
# $0 $app_name
#################################
cartridge_oper_testing()
{
    for oper in $cart_operations;do
    	echo_bold "rhc cartridge $oper $1 -a $2 -predhat"
    	rhc cartridge $oper $1  -a $2 -predhat
        [ $? -ne 0 ] && value=1 && break
    done
}
#################################
# $0 $app_name
#################################
add_hot_deploy()
{
	cd $1
	touch .openshift/markers/hot_deploy
	git add .; git commit -am "Add hot_deploy" ;git push
	cd -
}

add_disable_auto_scaling()
{
	cd $1
	touch .openshift/markers/disable_auto_scaling
	git add . && git commit -am "Add disable_auto_scaling" && git push
    [ $? -eq 0 ] && value=0 || value=1
	cd -
}

ssh_app()
{
if [ "$#" == "1" ];then
	   #app_path=`rhc domain show -paaa|grep $1|grep "SSH URL"|awk -F'//' '{print $2}'`
		app_path=`rhc app show -a $1 -p$passwd|grep -A0 "SSH:"|awk '{print $2}'`
		echo "$1 SSH path is : $app_path"
		cd  
		ssh  $app_path
else
		echo "Please input your App name."
		echo "Such as : $0 app1"
fi
}

#################################################################################
#$0 $app_name $command
#################################################################################
task_ssh_app()
{
command='mysql -Druby0 -e "create table test(id int(8), name char(20));insert into test values('0','openshifit');select * from table;"'
app_path=`rhc app show -a $1 -p$passwd|grep -A0 "SSH:"|awk '{print $2}'`
echo "$1 SSH path is : $app_path"
expect -f - <<EOF
set  timeout -1
spawn ssh $app_path
expect {
        "*>"                {send "$command\r";exp_continue}
}
wait
EOF
}

app_service_pid()
{
	app_path=`rhc app show -a $1 -p$passwd|grep -A0 "SSH:"|awk '{print $2}'`
	echo "$1 SSH path is : $app_path"
	cd $1
	if [[ "$1" =~ ^jbossas ]] || [[ "$1" =~ ^jbosseap ]];then
		pids=`ssh $app_path ps -ef|grep -i standalone|grep -v grep|awk '{print $2}'`
	elif [[ "$1" =~ ^jbossews ]];then
		pids=`ssh $app_path ps -ef|grep jre|grep -v grep|awk '{print $2}'`	
	else
		pids=`ssh $app_path ps -ef|grep -i bin/httpd|grep -v grep|awk '{print $2}'`
	fi
	cd -
}

add_jenkins_client()
{
	spawn rhc cartridge add jenkins-client -a $app -predhat
}

###################################
#parameter 2
# $0  action  app_type/app_name	
###################################
rest_api()
{
	if [ "$1" = "create" ];then
		app_type=$2
		app_name=${app_type%-*}${app_number}s
		curl -k -H "Accept: application/xml" --user "$user:$passwd" https://$broker_url/broker/rest/domains/$domain/applications -X POST -d name=$app_name -d cartridge=$app_type -d scale=true
		[ $? -ne 0 ] && return $? 
		#git clone $(rhc app show $app_name -p$passwd|grep "Git URL"|awk '{print $3}')
		expect -f - <<EOF
		set timeout -1
		spawn rhc git-clone $app_name -p$passwd
		expect {
			"Are you *(yes/no)?"    {send "yes\r";exp_continue}
		}
		wait
EOF
	elif [ "$1" = "scale-up" ] || [ "$1" = "scale-down" ];then
		app=$2
		echo_bold "curl -k -H 'Accept: application/xml' --user "$user:$passwd"  https://$broker_url/broker/rest/domains/$domain/applications/$app/events -X POST -d event=$1"
		curl -k -H 'Accept:application/xml' --user "$user:$passwd"  https://$broker_url/broker/rest/domains/$domain/applications/$app/events -X POST -d event=$1
		return $?
	else 
		app=$2
		echo_bold "curl -k -H 'Accept: application/xml' --user "$user:$passwd"  https://$broker_url/broker/rest/domains/$domain/applications/$app/events -X POST -d event=$1"
		curl -k -H 'Accept:application/xml' --user "$user:$passwd"  https://$broker_url/broker/rest/domains/$domain/applications/$app/events -X POST -d event=$1
		return $?
	fi
}

####################################
#parameter number 1
# $0  $app_name [$check_content]
####################################
url_check()
{
	check_name=$1
#	curl http://p53-sun0131.p0129.com/read.php
	[ -n "$2" ] && check_content=$2 ||  check_content="Welcome to OpenShift"
	echo_bold "curl http://$check_name-$domain.${broker_url#*.}|grep $check_content"
	curl http://$check_name-$domain.${broker_url#*.}|grep "Welcome to OpenShift"
    value=$?
	[ $value -eq 0 ] && echo_green "Access $check_name Successed!" || echo_red "Access $check_name Failed!"
    return $value
}

#parameter number 2
# $0  $app_name  $action_type
scale_check()
{
	app_path=`rhc app show -a $1 -p$passwd|grep -A0 "SSH:"|awk '{print $2}'`
	scp $app_path:./haproxy-1.4/conf/haproxy.cfg .
    gears=$(curl -k -H "Accept: application/xml" --user "${user}:${passwd}" https://${broker_url}/broker/rest/domains/${domain}/applications/${1}/gears.json -X GET |python -mjson.tool|grep proxy_host|egrep -v "null|$1")
    gears_num=$(curl -k -H "Accept: application/xml" --user "${user}:${passwd}" https://${broker_url}/broker/rest/domains/${domain}/applications/${1}/gears.json -X GET |python -mjson.tool|grep proxy_host|egrep -v "null|$1"|wc -l)
    echo_blue "Have gears after $2: $gears"
	 if [ $gears_num -ge 2 ] && [ "$2" = "scale-up" ];then
			 echo_green "Scale-up successed!"
			 cat haproxy.cfg |grep "$domain"
	elif [ $gears_num -eq 1 ] && [ "$2" = "scale-down" ];then
		echo_green "Scale-down successed!"
		cat haproxy.cfg |grep "$domain"
	else
			echo_red "$2 is Failed!"
            value=1
	fi
    return $value
}

#app management testing
app_oper_testing()
{
    for oper in $app_operations;do
    	echo_bold "rhc app $oper $1 -p$passwd"
    	rhc app $oper $1 -p$passwd
        [ $? -ne 0 ] && value=1 && break
    done
}

#no parameter
set_running_parameter()
{
	SAVEDIFS=$IFS
	IFS='='
	while read NAME VALUE
	do
		case $NAME in
			\#*)
				;; #ignore comments
			cartridges)
				cartridges=$VALUE
				;;
			app_types)
				app_types=$VALUE
				;;
            		app_operations)
               			 app_operations=$VALUE
				;;
			cart_operations)
				cart_operations=$VALUE
		esac
	done < $CONFIG_FILE
	IFS=$SAVEDIFS
	echo_blue "App types are :$app_types"
	echo_blue "cartridges are :$cartridges"
}

#rest_api delete all app and domain
rest_api_delete()
{
	echo_bold "curl -k -X DELETE -H 'Accept: application/xml' -d force=true --user ${user}:${passwd} https://${broker_url}/broker/rest/domains/$domain"
	curl -k -X DELETE -H 'Accept: application/xml' -d force=true --user ${user}:${passwd} https://${broker_url}/broker/rest/domains/$domain
}

#############################################
# $0 $app_name $alias_string
#############################################
alias_add()
{
	echo_bold "rhc alias add $2 ${1}.onpremise.com -p${passwd}"
	rhc alias add $2 ${1}.onpremise.com -p${passwd}
}
#############################################
# $0 $app_name $alias_string
#############################################
alias_remove()
{
	echo_bold "rhc alias remove $2 ${1}.onpremise.com -p${passwd}"
	rhc alias remove $2 ${1}.onpremise.com -p${passwd}
}
###########################################
# $0 $app_name
###########################################
add_mysql_data()
{
app_path=`rhc app show -a $1 -predhat|grep -A0 "SSH:"|awk '{print $2}'`
echo "$1 SSH path is : $app_path"
cartridge_dir=`ssh $app_path env|grep OPENSHIFT_PRIMARY_CARTRIDGE_DIR|cut -d'=' -f2`
sql_file="mysql_insert.sql"
echo "App Path: $app_path, Cartridge_dir: $cartridge_dir"

scp $sql_file $app_path:$cartridge_dir

expect -f - <<EOF
spawn ssh $app_path 
expect {
	"\['$1'*>"			{ send "mysql -D'$1' < '$cartridge_dir'/'$sql_file'\r" }
}
sleep 1
EOF
}

###########################################
# $0 $app_name
###########################################
delete_mysql_data()
{
app_path=`rhc app show -a $1 -predhat|grep -A0 "SSH:"|awk '{print $2}'`
echo "$1 SSH path is : $app_path"
cartridge_dir=`ssh $app_path env|grep OPENSHIFT_PRIMARY_CARTRIDGE_DIR|cut -d'=' -f2`
sql_file="mysql_delete.sql"
echo "App Path: $app_path, Cartridge_dir: $cartridge_dir"
scp $sql_file $app_path:$cartridge_dir

expect -f - <<EOF
spawn ssh $app_path 
expect {
        "\['$1'*>"                      { send "mysql -D'$1' < '$cartridge_dir'/'$sql_file'\r" }
}
sleep 1
EOF
}
