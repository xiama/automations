#!/bin/sh
user_home=$(env | grep '^HOME=' | cut -d= -f2)
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

echo "###Test Case###: Security - Write or modify libra important data";

command1="touch  ${user_home}/git/write_x.git"
echo "Command 1: $command1"
eval "$command1"
command1_ret=$?
echo "Command 1 return $command1_ret"
echo ""
echo ""
echo ""

command2_ret=0
for i in $(ls ${user_home}/*/conf.d/libra.conf); do
    echo "Command 2: echo xx >>$i"
    echo "xx" >>$i
    tmp_ret=$?
    if [ $tmp_ret -eq 0 ]; then
        echo "Scceed to write $i"
        command2_ret=0
        break
    else
        command2_ret=1
    fi
done
echo "Command 2 return $command2_ret"
echo ""
echo ""
echo ""


command3="echo xx >> /etc/libra/controller.conf"
echo "Command 3: $command3"
eval "$command3"
command3_ret=$?
echo "Command 3 return $command3_ret"
echo ""
echo ""
echo ""


command4="echo xx >> /etc/mcollective/server.cfg"
echo "Command 4: $command4"
eval "$command4"
command4_ret=$?
echo "Command 4 return $command4_ret"
echo ""
echo ""
echo ""

command5="echo xx >> /etc/mcollective/client.cfg"
echo "Command 5: $command5"
eval "$command5"
command5_ret=$?
echo "Command 5 return $command5_ret"
echo ""
echo ""
echo ""

command6="echo xx >> /etc/libra/resource_limits.conf"
echo "Command 6: $command6"
eval "$command6"
command6_ret=$?
echo "Command 6 return $command6_ret"
echo ""
echo ""
echo ""

command7="echo xx >> /etc/qpidd.conf"
echo "Command 7: $command7"
eval "$command7"
command7_ret=$?
echo "Command 7 return $command7_ret"
echo ""
echo ""
echo ""

command8="cat /etc/libra/controller.conf"
echo "Command 8: $command8"
eval "$command8"
command8_ret=$?
echo "Command 8 return $command8_ret"
echo ""
echo ""
echo ""

command9="cat /etc/mcollective/server.cfg"
echo "Command 9: $command9"
eval "$command9"
command9_ret=$?
echo "Command 9 return $command9_ret"
echo ""
echo ""
echo ""

command10="cat /etc/libra/node.conf"
echo "Command 10: $command10"
eval "$command10"
command10_ret=$?
echo "Command 10 return $command10_ret"
echo ""
echo ""
echo ""

command11="ls /var/lib/libra/"
echo "Command 11: $command11"
eval "$command11"
command11_ret=$?
echo "Command 11 return $command11_ret"
echo ""
echo ""
echo ""

command12="touch /var/lib/libra/com12_test"
echo "Command 12: $command12"
eval "$command12"
command12_ret=$?
echo "Command 12 return $command12_ret"
echo ""
echo ""
echo ""

command13_ret=1
for i in $(grep 'libra guest' /etc/passwd | awk -F":" '{print $6}' | grep -v $user_name); do
    command="ls $i"
    echo "Command 13: $command"
    eval "$command"
    tmp_ret=$?
    if [ $tmp_ret -eq 0 ]; then
        echo "Scceed to read $i"
        command13_ret=0
        break
    else
        command13_ret=1
    fi
done
echo "Command 13 return $command13_ret"
echo ""
echo ""
echo ""

command14_ret=1
for i in $(grep 'libra guest' /etc/passwd | awk -F":" '{print $6}' | grep -v $user_name); do
    command="cd $i"
    echo "Command 14: $command"
    eval "$command"
    tmp_ret=$?
    if [ $tmp_ret -eq 0 ]; then
        echo "Scceed to excute $i"
        command14_ret=0
        break
    else
        command14_ret=1
    fi
done
echo "Command 14 return $command14_ret"
echo ""
echo ""
echo ""


command15_ret=1
for i in $(grep 'libra guest' /etc/passwd | awk -F":" '{print $6}' | grep -v $user_name); do
    command="stat $i"
    echo "Command: $command"
    eval "$command"
    tmp_ret=$?
    if  [ X"$tmp_ret" == X"0" ]; then
        command="stat $i | grep Uid | awk -F'(' '{print \$2}' | awk -F')' '{print \$1}' | cut -c4"
        other_flag=$(eval "$command")
        echo "Command 15: {$command} - {$other_flag}"
        if [ X"$other_flag" != X"0" ]; then
            echo "Dir - $i have some permisson for other user"
            command15_ret=0
            break
        else
            command15_ret=1
        fi
    else
        echo "stat operation to $i failed, skipping "
        command15_ret=1
    fi
done
echo "Command 15 return $command15_ret"
echo ""
echo ""
echo ""


command16="cat /etc/mcollective/client.cfg"
echo "Command 16: $command16"
eval "$command16"
command16_ret=$?
echo "Command 16 return $command16_ret"
echo ""
echo ""
echo ""

command17="cat /etc/qpidd.conf"
echo "Command 17: $command17"
eval "$command17"
command17_ret=$?
echo "Command 17 return $command17_ret"
echo ""
echo ""
echo ""

command18="cat /etc/qpid/qpidc.conf"
echo "Command 18: $command18"
eval "$command18"
command18_ret=$?
echo "Command 18 return $command18_ret"
echo ""
echo ""
echo ""

command19="echo xx >> /etc/qpid/qpidc.conf"
echo "Command 19: $command19"
eval "$command19"
command19_ret=$?
echo "Command 19 return $command19_ret"
echo ""
echo ""
echo ""

command20="ls /etc/qpid/pki; cp -r /etc/qpid/pki ./; ls ./pki"
echo "Command20: $command20"
eval "$command20"
line_count=$(ls ./pki | wc -l)
if [ ${line_count} -gt 0 ]; then 
    command20_ret=0
else 
    command20_ret=1
fi
echo "Command 20 return $command20_ret"
echo ""
echo ""
echo ""

command21="ls /etc/mcollective/ssl/clients/; cp -r /etc/mcollective/ssl/clients/* ./; ls ./clients/*"
echo "Command21: $command21"
eval "$command21"
line_count=$(ls ./pki | wc -l)
if [ ${line_count} -gt 0 ]; then
    command21_ret=0
else
    command21_ret=1
fi
echo "Command 21 return $command21_ret"
echo ""
echo ""
echo ""

command22="cat /etc/passwd"
echo "Command 22: $command22"
eval "$command22"
command22_ret=$?
echo "Command 22 return $command22_ret"
echo ""
echo ""
echo ""


for i in {1..22}; do 
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

