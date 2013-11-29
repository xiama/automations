#!/bin/bash
app_type=$1
pwd=$(pwd)
time=$(date +%Y%m%d-%H%M%S)
log="$pwd/${0%.*}_${time}.log"

#no parameter
app_create_all()
{
	for scale in on off;do
		for app in $app_types;do
			if [ "$app" = "diy-0.1" ] && [ "$scale" = "on" ];then
				echo "Diy is cann't support scalable !"
				continue
			fi
			for cartridge_type in $cartridges;do
				if [ "$scale" = "on" ] && [ "$cartridge_type" = "cron-1.4" ];then
					echo "Cron-1.4 is can not embedded to scalable application!"
				elif [ "$app" = "jbosseap-6.0" ] && [ "$cartridge_type" = "cron-1.4" ];then
					echo "Cron-1.4 is not support at jbosseap-6.0"
				elif [ "$scale" = "off" ];then
					run app_create $app
					run url_check $app_name
					run cartridge_add $cartridge_type $app_name
					run url_check $app_name
					echo "$app_name		$cartridge_type			noscalable		$(date +%Y%m%d-%H%M%S)" >> $log
				else
					run app_create $app -s
					run cartridge_add $cartridge_type $app
					echo "$app_name		$cartridge_type			scalable			$(date +%Y%m%d-%H%M%S)" >> $log
				fi
			done
		done
	done
	echo_yellow "Already have $(($app_number+1)) applications"
}

. ./function.sh
run set_running_parameter
while true;do
	[ -d testdir ] && rm -rf testdir/* || mkdir testdir
	cd testdir
	rhc domain show -predhat|grep jenkins-1.4 > /dev/null
	[ $? -ne 0 ] && run app_create jenkins-1.4
	run app_create_all
	run app_delete_all
done
