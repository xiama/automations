#!/bin/sh
start_time=`date +%Y%m%d-%H%M%S`
rootdev=`df -h|grep /dev/sda|awk '{print $1}'|cut -d/ -f 3`

broker_info()
{
	time=`date +%Y%m%d-%H%M%S`
	echo "time: $time"
	echo ""
	echo "****** 1. Filesystem info: ******"
	df -h|grep -B1 "/$"
	echo
	echo "****** 2. MEMORY info: ******"
	 free -m |grep "buffers\/cache"
	echo ""
	echo "****** 3. Vmstat info: ******"
	echo
	vmstat 1 3|tee -a vmstat-$start_time.log 
	echo
	echo "****** 4. Cpu consume top 3: ******"
	ps auxw|head -1;ps auxw|sort -rn -k3|head -3
	echo
	echo "****** 5. Mem consume top 3: ******"
	echo
	ps auxw|head -1;ps auxw|sort -rn -k4|head -3
	echo
	echo "****** 6. Mongo and apache ******"
	echo
	pstree |egrep 'mongo|httpd'
	echo
<<<<<<< HEAD
	echo "****** 7. Mongo fds number ******"
	echo "Mongo process fds: (/proc/`pidof mongod`/fd/)"
	ls /proc/`pidof mongod`/fd/|wc -l
	echo
	echo "===========================next ========= record==============================="
	sleep 20
=======
    echo "****** 7. Mongo fds number ******"
    echo "Mongo process fds: (/proc/`pidof mongod`/fd/)"
    ls /proc/`pidof mongod`/fd/|wc -l
    echo
	echo "===========================next ========= record==============================="
	sleep 10
>>>>>>> 17989def7444710378d0ec1e1b41ac5119fb8211
}
while true;do	
	broker_info |tee -a broker-$start_time.log
done
