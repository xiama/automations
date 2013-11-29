#!/bin/bash

rhlogin="xx"
passwd="redhat"

app_info=`rhc domain show -l ${rhlogin} -p ${passwd}`
for i in `echo "${app_info}" | grep ssh | awk -F'Git URL: ' '{print $2}'`; do
    echo "Git cloning $i"
    rm -rf $i
    git clone $i
    echo "============"
done
