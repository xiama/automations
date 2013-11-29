#!/bin/bash
app_type=$1
pwd=$(pwd)
time=$(date +%Y%m%d-%H%M%S)
log="$pwd/${0%.*}_${time}.log"

[ -f function.sh ] || ln -s $(pwd)/../function.sh function.sh
[ -f common_func.sh ] || ln -s $(pwd)/../common_func.sh common_func.sh
[ -f AutoCreate.cfg ] || ln -s $(pwd)/../AutoCreate.cfg AutoCreate.cfg
[ -d testdir ] && rm -rf testdir/* || mkdir testdir
. ./function.sh
cd testdir
#run set_running_parameter

#################################################
# $0 $app_type
#################################################
scaling_negative()
{
#    app_create $1
#    rest_api scale-up $app_name
#    scale_check $app_name scale-up
#    [ $? -eq 0 ] && echo_red "Scale-up should be failed!" && exit
    
    run rest_api create $1
    run url_check $app_name
    run rest_api scale-up $app_name
    run scale_check $app_name scale-up
    run url_check $app_name

    run rest_api scale-down $app_name
    run scale_check $app_name scale-down
    run url_check $app_name
    run rest_api scale-down $app_name
    run url_check $app_name
    run app_delete $app_name
}

if [ $# -ne 1 ];then
    echo "Please input the correct format,such as:"
    echo "$0 php-5.10"
else
    run scaling_negative $1
fi
