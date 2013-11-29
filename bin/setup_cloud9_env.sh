#!/bin/bash
#
#
# Generated from https://hosted.englab.nay.redhat.com/issues/11904
#
# mzimen@redhat.com
#

set -e

if [ -z "$2" ]; then
    echo "Usage: $0 <Broker IP> <Openshift login>"
    exit 2
fi

BROKER=$1
LOGIN=$2

ssh root@$BROKER<<EOF
cd /etc/openshift
rm -f resource_limits.conf
ln -s resource_limits.conf.c9 resource_limits.conf
/usr/libexec/mcollective/update_yaml.rb /etc/mcollective/facts.yaml
rhc-admin-ctl-user -l $LOGIN --allowsubaccounts true
rhc-admin-ctl-user -l $LOGIN --addgearsize c9
rhc-admin-ctl-user -l $LOGIN --inheritgearsize true
EOF
