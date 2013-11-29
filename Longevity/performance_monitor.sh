#!/bin/bash
. ./common_func.sh

server_config()
{
if [ -f server.conf ];then
	echo "Will read config from server.conf"
else
	echo -n "Please input the number of server you needed to monitor:"
	read all
	no=0
	>server.conf
	while (($no < $all));do
		echo -n "Please input the $no server's IP you needed to monitor: "
		read server_ip
		echo -n "Please input (root)Password:"
		read server_passwd
		echo -n "Please input the alias of your server:"
		read server_alias
		echo "$server_alias $server_ip $server_passwd ">>server.conf
		no=$((no + 1))
	done
fi
}

confirm_and_deployment()
{
while read server_alias server_ip server_passwd;do
	echo "Confirm your input :"
	echo_bold "Alias: $server_alias,		IP: $server_ip,			Password: $server_passwd"
done < server.conf
echo -n "If these info is all right, please input 'yes' to continue: (yes/no)"
read yes
if [ "$yes" = "yes" ];then
	while read server_alias server_ip server_passwd;do
		run scp_task "record.sh" $server_ip $server_passwd "/opt"
	done < server.conf
else 
	echo "Please run it again!"
    exit 1
fi
}

run server_config
run confirm_and_deployment
tail -f $1|while read app_info;do
	echo_blue "New app created, app info: $app_info"
	while read server_alias server_ip server_passwd;do
	echo_green "####################### $server_alias INFO #######################"
	run task_ssh_root $server_ip $server_passwd "/opt/record.sh"
	done < server.conf
done
