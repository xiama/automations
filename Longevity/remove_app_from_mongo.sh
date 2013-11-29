#!/bin/bash
uuids=`rhc domain show -predhat|grep SSH|awk -F'@' '{print $1}' |awk  '{print $2}'`
echo "uuids : $uuids"
for uuid in $uuids;do
expect -f - <<EOF
spawn mongo --ssl -u openshift -p mongopass localhost/openshift_broker
expect {
	"> "			{ send "db.applications.remove({'_id' : ObjectId('$uuid')})\r";exp_continue }		
	"> "			{ send "exit\r";exp_continue }		
}
eof
EOF
done
