#!/bin/sh

cd /home/automation/bin
export OPENSHIFT_user_email=yujzhang
export OPENSHIFT_user_passwd=111111
export TCMS_USER=yujzhang
export TCMS_PASSWORD=Zhangyj_1986

python launcher.py -a stg.openshift.redhat.com -i 44553
