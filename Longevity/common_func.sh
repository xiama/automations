#!/bin/bash

#################################################################################
# FileName:      common_func.sh
# Author:        <nsun@redhat.com> 
# Description:   provide the common fucntion for all test cases
# Version:       1.0
# Function List: kill_process; end_test; run; error; info; check_point; sysinfo
#    kill_process: Kill the process base on passed  parameter.
#    target_reboot: Reboot tested machine when current running failed. 
#    run:        print the info for the command and execute the command
#    error:      print the error infomation with standard format
#    info:       print some infomation with (INFO) tag
#    sysinfo:    profile the system information
# History:       Revision history
#################################################################################

export PATH=/sbin:/usr/sbin:/bin:$PATH

#################################################################################
#$0 $(file or direcotry) $ip $pasword $(source directory)
#################################################################################
scp_task()
{
expect -f - <<EOF
set  timeout -1
spawn scp -r $1 root@$2:$4
expect {
	"Are you sure you want to continue connecting (yes/no)?"		{send "yes\r";exp_continue}
	"*assword:"			{send "$3\r";exp_continue}
}
wait
EOF
}

#################################################################################
#$0 $ip $pasword "command"
#################################################################################
task_ssh_root()
{
expect -f - <<EOF
set  timeout -1
spawn ssh root@$1 "$3"
expect {
	"Are you sure you want to continue connecting (yes/no)?"		{send "yes\r";exp_continue}
	"*assword:"			{send "$2\r";exp_continue}
}
wait
EOF
}

#################################################################################
# Function:    kill_process
# Description: Kill all process with keyword
# Input:       keywords of child process name 
# Output:      child process pid
# Return:      0
# Others:      none
#################################################################################

function kill_process()
{
sign=$1
pid=`ps aux|grep $sign|grep -v grep|awk '{print $2}'`
kill -9 $pid
return 0
}

#################################################################################
# Function:    target_reboot 
# Description: Reboot tested machine
# Input:       target machine IP
# Output:      none
# Return:      0
# Others:      none
#################################################################################
function target_reboot()
{
expect -f - <<EOF
spawn ssh root@$SUT_IP "init 6"
expect {
	    "Are you sure you want to continue connecting (yes/no)?"    { send "yes\r"; exp_continue }
	    "*assword:"                                                 { send "123456\r";exp_continue }
		eof							{ send_user "eof" }
			    }
		wait
EOF
sleep 1
exit
return 0
}

#################################################################################
# Function:    echo_$color
# Description: echo color with font,Facilitate the observation log output
# Input:       echo log
# Output:      none
# Others:      none
#################################################################################
function echo_red()
{
	    echo -e "\e[1;31m"$*"\e[0m"
}

echo_blue()
{ 
	    echo -e "\e[1;34m"$*"\e[0m" 
}

echo_green()
{ 
	    echo -e "\e[1;32m"$*"\e[0m" 
}

echo_yellow()
{ 
	echo -e "\e[1;33m"$*"\e[0m"
}

echo_pink()
{ 
	echo -e "\e[1;35m"$*"\e[0m"
}

echo_bold()
{ 
	    echo -e "\e[1;38m"$*"\e[0m" 
}


#################################################################################
# Function:    run
# Description: print the command information and execute the command
# Input:       the command
# Output:      the comand information and execution result
# Return:      return the value which returned by the command
# Others:      none
#################################################################################
function run()
{
	echo 
	echo_blue "-------------------------Function $1 start-------------------------------"
	echo -n "[$(pwd)]#"
	echo "$*"
	eval "$*"
	r_value=$?
	echo_blue "--------------------------Function $1 end--------------------------------"
	if [ "$r_value" -ne 0 ] ;then 
        echo_red "$1 function running failed!" && 
        runlevel|grep 5 > /dev/null && notify-send "Testing failed ..." 
        #exit 1 
    else
        echo_green "$1 function running end!"
    fi
	echo 
}

#################################################################################
# Function:    task_scp
# Description: Auto scp file to target machine
# Input:       file user@target_ip:/dir/
# Output:      none
# Return:      none
# Others:      none
#################################################################################
function task_scp()
{
	#expect is a software suite for automating interactive tools
expect -f - <<EOF
set timeout 6000
spawn scp -r $1 $2@$3:$4
expect {
	"Are you sure you want to continue connecting (yes/no)?" { send "yes\r" ; exp_continue }
	"assword:" { send "$5\r"; exp_continue }
	eof	{ send_user "eof" }
}
wait
EOF
}

#################################################################################
# Function:    sysinfo
# Description: profile the system information
# Input:       none
# Output:      system information
# Return:      none
# Others:      none
#################################################################################
function sysinfo()
{
    tmpstarts=`dmidecode | grep -n "" | grep "Handle 0x" | cut -d ":" -f 1`
    shopt -s extglob
    tmpstarts=`echo $tmpstarts`
    tmpends=${tmpstarts/#+([[:digit:]]) /}
    tmpends="$tmpends 10000"
    index=0
    for start in $tmpstarts
    do
        starts[$index]=$start
        index=$((index+1))
    done
    
    index=0
    for end in $tmpends
    do
        ends[$index]=$end
        index=$((index+1))
    done
    
    
    
    # processor
    echo "Processor Information"
    echo "====================="
    processor=`mydmidecode -t processor | grep Version | head -n 1 | awk -F ":" '{print $2}' | sed 's/^ //g' | sed 's/ \{1,\}/ /g'`
    if [ "${processor:0:3}" = "Not" ]
    then
        processor=`cat /proc/cpuinfo | grep "model name" | head -n 1 | awk -F ":" '{print $2}' | sed 's/^ //g' | sed 's/ \{1,\}/ /g'`
    fi
    processornum=`mydmidecode -t processor | grep "Socket Designation: " | wc -l`
    
    cores=`cat /proc/cpuinfo | grep "cpu cores" | head -n 1 | sed 's/^.*: //g'`
    
    phymem=`mydmidecode -t memory | grep Size | awk 'BEGIN {sum=0} {if (int($2)!=0) sum+=$2} END {print sum/1024;}'`
    availmem=`cat /proc/meminfo | head -n 1 | awk '{printf "%.2f", $2/1024/1024;}'`
    
    echo "processor type: $processor"
    echo "number of CPU: $processornum"
    echo "number of core per CPU: $cores"
    
    # Cache info
    index=0
    tmpvar=`mydmidecode -t cache | grep "Configuration: " | grep "Level " | sed 's/^.*, Level //g'`
    for item in $tmpvar
    do
        levels[$index]=$item
        index=$((index+1))
    done
    
    index=0
    tmpvar=`mydmidecode -t cache | grep "System Type" | cut -d ":" -f 2 | sed 's/ //g'`
    for item in $tmpvar
    do
        cachetypes[$index]=$item
        index=$((index+1))
    done
    
    index=0
    tmpvar=`mydmidecode -t cache | grep "Installed Size" | cut -d ":" -f 2 | sed 's/ //g'`
    for item in $tmpvar
    do
        cachesizes[$index]=$item
        index=$((index+1))
    done
    
    rm -f /tmp/.cacheinfo.txt
    for (( i = 0; i < $index; i++ ))
    do
        echo "L${levels[$i]} ${cachetypes[$i]} cache size: ${cachesizes[$i]/KB/ KB}" >> /tmp/.cacheinfo.txt
    done
    cat /tmp/.cacheinfo.txt | sort | uniq
    rm -f /tmp/.cacheinfo.txt
    echo ""
    
    # Memory
    echo "Memory Information"
    echo "=================="
    echo "Physical memory size: $phymem GB"
    echo "Available memory size: $availmem GB"
    echo ""
    
    # Harddisk
    echo "Harddisk Information"
    echo "===================="
    fdisk -l 2>&1 | grep Disk | sed 's/^Disk //g'
    echo ""
    
    # SCSI device list
    which lsscsi > /dev/null 2>&1
    if [ $? -eq 0 ]
    then
        echo "SCSI Device List"
        echo "================"
        lsscsi
    fi
    echo ""
    
    # PCI/PCIE Slot Information
    rm -f /tmp/.pciinfo1.txt
    rm -f /tmp/.pciinfo2.txt
    echo "PCI/PCIE Slot Information"
    echo "========================="
    printf "%20s\t%s\n" "Slot" "Type"
    printf "%20s\t%s\n" "----" "----"
    mydmidecode -t slot | grep "Designation: " | sed 's/^.*Designation: //g' > /tmp/.pciinfo1.txt
    mydmidecode -t slot | grep "Type: " | sed 's/^.*Type: //g' > /tmp/.pciinfo2.txt
    
    lines=`cat /tmp/.pciinfo2.txt | wc -l`
    for (( i = 0; i < $lines; i++ ))
    do
        slot=`cat /tmp/.pciinfo1.txt | sed -n "$((i+1))"p | sed 's/^ \{1,\}//g' | sed 's/ \{1,\}$//g'`
        type=`cat /tmp/.pciinfo2.txt | sed -n "$((i+1))"p`
        printf "%20s\t%s\n" "$slot" "$type"
    done
    rm -f /tmp/.pciinfo1.txt
    rm -f /tmp/.pciinfo2.txt
    echo ""
    
    # lspci
    echo "PCI Device Information"
    echo "======================"
    lspci | cut -d " " -f 2-
    echo ""
    
    # On Board Device Information
    echo "On Board Device Information"
    echo "==========================="
    mydmidecode -t baseboard | grep -A 200 "On Board Device" | grep "Description: " | sed 's/^.*Description: //g'
    echo ""
    
    # OS Version
    echo "OS Version"
    echo "=========="
    cat /etc/*-release
}
