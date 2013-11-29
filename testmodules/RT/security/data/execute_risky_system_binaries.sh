#!/bin/sh
user_home=$(env | grep HOME | cut -d= -f2)
echo "User Home Directory: $user_home"
user_name=$(basename $user_home)
echo "User name: $user_name"
user_id=$(id -u $user_name)
echo "User ID: $user_id"
libra_version=$(/bin/rpm -qa | grep rhc)
echo "Libra Verison on node: "
echo "$libra_version"
echo ""
echo ""
echo ""

echo "###Test Case 1###: Security - Execute risky system binaries"
command="ps -ef"
echo "Command: $command"
$command
command1="ps -ef --no-headers | grep -v $user_id"
echo "Command1: $command1"
eval "$command1"
command1_ret=$?
echo "Command 1 return $command1_ret"
echo ""
echo ""
echo ""

command2="/usr/sbin/mc-ping"
echo "Command2: $command2"
$command2 >./temp.log 2>&1
tmp_ret=$?
cat ./temp.log
echo "Return $tmp_ret"
command="cat ./temp.log | grep 'ip-'"
echo "Command: $command"
eval "$command"
command2_ret=$?
echo "Command 2 return $command2_ret"
echo ""
echo ""
echo ""

ssh_pub_key='AAAAB3NzaC1yc2EAAAADAQABAAABAQDcjvxtCN9CGLk/BUXe7wo/LL+5cguYQbwe3o4gfQnu7gBHjMhxs1I1/J6c3E52sMN+83/LUb/CuKAuV9lzG5fOkbNxps6F0RqzEqvSH3UF7qdCgBZJx19Xyo+YQfd8eVnM3honLira+i/PiqRmMr0yrryqa5qNqreL52hVguQ0vFC7vJX6Nbg52mmFfZvyXG8ksrC3H+zpMT5FHq6MoxWqU3jCxQ4rpJZqM2VZ7xSpU/7wKevUK345CbwRfGSPsr6M1tkaaAhOoAYJrC3U0si+JFc6hS2OTFD9QmjYAWS0NvibbFPT3SOKzEm9U5GQDzlEIr33KNwAQmv1ZjTcWjZh'
fake_uuid=$(uuidgen |sed 's/-//g')
fake_email="fakeuser@redhat.com"
fake_app="fakeapp"
fake_namespace="fakeuser"

command3="/usr/sbin/mc-rpc --agent libra --action cartridge_do --arg cartridge=li-controller-0.1 --arg action=configure --arg args=\"-c ${fake_uuid} -e ${fake_email} -s ${ssh_pub_key} -d\""
echo "Command3: $command3"
eval "$command3"
tmp_ret=$?
echo "Return $tmp_ret"
command="grep $fake_uuid /etc/passwd"
echo "Command: $command"
$command
command3_ret=$?
echo "Command3 return $command3_ret"
echo ""
echo ""
echo ""

command4="/usr/sbin/mc-rpc --agent libra --action cartridge_do --arg cartridge=php-5.3 --arg action=configure --arg args=\"${fake_app} ${fake_namespace} ${user_name}\""
echo "Command4: $command4"
eval "$command4"
tmp_ret=$?
echo "Return $tmp_ret"
echo "ps -ef output:"
ps -ef
command="ps -ef | grep -v grep | grep $fake_app"
echo "Command: $command"
eval "$command"
command4_ret=$?
echo "Command 4 return $command4_ret"
echo ""
echo ""
echo ""

    

command5="/usr/sbin/mc-rpc --agent libra --action cartridge_do --arg cartridge=php-5.3 --arg action=deconfigure --arg args=\"${fake_app} ${fake_namespace} ${user_name}\""
echo "Command5: $command5"
if [ X"$command4_ret" == X"0" ]; then
    eval "$command5"
    tmp_ret=$?
    echo "Return $tmp_ret"
    echo "ps -ef output:"
    ps -ef
    command="ps -ef | grep -v grep | grep $fake_app"
    echo "Command: $command"
    eval "$command"
    command_ret=$?
    if [ X"$command_ret" == X"0" ]; then
        command5_ret=1
    else
        command5_ret=0
    fi
else
    echo "Skipping command 5 due to dependent command 4 failed, and assume it return 1"
    command5_ret=1
fi
echo "Command 5 return $command5_ret"
echo ""
echo ""
echo ""


command6="/sbin/reboot"
echo "Command 6: $command6"
eval "$command6"
command6_ret=$?
echo "Command 6 return $command6_ret"
echo ""
echo ""
echo ""

command7="/sbin/poweroff"
echo "Command 7: $command7"
eval "$command7"
command7_ret=$?
echo "Command 7 return $command7_ret"
echo ""
echo ""
echo ""

command8="/bin/rpm -qa | grep rhc"
echo "Command: $command8"
eval "$command8"
command8_ret=$?
echo "Command 8 return $command8_ret"
echo ""
echo ""
echo ""


for i in {1..8}; do 
    eval ii="$"command${i}_ret
    echo "Command ${i} result: $ii"
    if [ X"$ii" == X"0" ]; then 
        result="FAIL"
        break
    else 
        result="PASS"
    fi
done


echo "###RESULT###: ${result}"
echo ""
echo ""
echo ""


