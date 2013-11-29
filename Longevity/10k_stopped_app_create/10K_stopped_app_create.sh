#!/bin/bash
app_type=$1
pwd=$(pwd)
time=$(date +%Y%m%d-%H%M%S)
log="$pwd/${0%.*}_${time}.log"

#no parameter
app_create_all()
{
		for app in $app_types;do
			run app_create $app
    	                #run url_check $app_name
			run rhc app stop $app_name -p$passwd --timeout 360
			echo "$app_name		$cartridge_type			noscalable		$(date +%Y%m%d-%H%M%S)" >> $log

			if [ "$app" = "diy-0.1" ];then
				echo "Diy is cann't support scalable !"
				continue
			fi

			run app_create $app -s
    		        #run url_check $app_name
			run rhc app stop $app_name -p$passwd --timeout 360
			echo "$app_name		$cartridge_type			scalable			$(date +%Y%m%d-%H%M%S)" >> $log
		done
	echo_yellow "Already have $(($app_number+1)) applications"
}

[ -f function.sh ] || ln -s $(pwd)/../function.sh function.sh
[ -f common_func.sh ] || ln -s $(pwd)/../common_func.sh common_func.sh
[ -f AutoCreate.cfg ] || ln -s $(pwd)/../AutoCreate.cfg AutoCreate.cfg
[ -d testdir ] && rm -rf testdir/* || mkdir testdir
. ./function.sh
cd testdir
run set_running_parameter
rhc domain show -predhat|grep jenkins-1.4 > /dev/null
[ $? -ne 0 ] && run app_create jenkins-1.4
while (($app_number < 10000));do
    run app_create_all
done
