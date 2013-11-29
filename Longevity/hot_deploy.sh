#!/bin/bash
. ./function.sh
app_name=$1

run add_hot_deploy $app_name
run app_service_pid $app_name
pids_before_push=$pids
#git push
run app_modify_and_push $app_name
run url_check $app_name "${app_name}-Welcome to OpenShift"
run app_service_pid $app_name
pids_after_push=$pids
echo_bold "pids_before_push = $pids_before_push"
echo_bold "pids_after_push = $pids_after_push"
for pid in $pids_before_pus;do
        cat $pids_after_push |grep $pid >/dev/null
        [ $? -eq 0 ] && echo_bold "$pid still existed!" || echo_red "$pid can't found after pussed, please check!";break 
done
echo_green "hot_deploy successed!"
