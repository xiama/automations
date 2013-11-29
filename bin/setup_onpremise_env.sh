#!/bin/bash

source setup_onpremise_env.rc

export FEDORA_VERSION=16
export DEBIAN_VERSION=wheezy
export UBUNTU_VERSION=quantal
export RHEL_VERSION=6.3
export CENTOS_VERSION=6.3
#host with kickstarts files and auto setup configuration
#export KICKSTART_HOST="http://file.rdu.redhat.com/~mmasters/"
export KICKSTART_HOST="https://github.com/openshift/enterprise/blob/enterprise-1.0/"
export KICKSTART_HOST="http://file.brq.redhat.com/~mzimen/"
export KICKSTART="${KICKSTART_HOST}/openshift.ks"
export DISK_SIZE="8"   #size in GB
export RAM_SIZE=1024

echo "Using RHEL $RHEL_VERSION now..."
create_guest_rhel

exit 0

set -e
if ! $(rpm -q nmap 2>&1 >/dev/null); then
    echo "please install nmap"
    exit 1
fi
current_dir=$(pwd)
echo "Current Dir: $(pwd)" 
# realpath is available on F16, not on rhel6.2
#script_real_path=$(realpath $0)
# start_with shell tips
#if [[ "$0" = /* ]]; then
#    root_dir=$(dirname $script_dir)
script_dir=$(dirname $0)
pushd $script_dir && script_real_dir=$(pwd) && popd
root_dir=$(dirname $script_real_dir)
# For jenkins integration source using
if [ ! -f ${root_dir}/etc/onpremise/vm-template.xml ]; then
    root_dir=$(pwd)
fi

img_path="http://fileshare.englab.nay.redhat.com/pub/libra/OnPremise/CleanImage/RHEL_6.3_x86_64.qcow2"
vm_img_dir="/var/lib/libvirt/images"
vm_template_xml="${root_dir}/etc/onpremise/vm-template.xml"
parent_vm_name="parent_node"
parent_vm_img="${vm_img_dir}/${parent_vm_name}.qcow2"

vm_username="root"
vm_password="redhat"
ssh_key_file="${HOME}/.ssh/mykey"
boot_timeout="90"

target_repo_file="/etc/yum.repos.d/openshift_devops.repo"

domain_name="devops.example.com"
broker_name="broker"





########### CONFIGURATION ####################
#
#  [BROKER]
#     |
#     +----[NODE0]
#     |
#     +----[NODE1]
#
###############################################


# 1. Create BROKER from scratch if doesn't exist (use kickstart)
# 2. Create 2 NODES from scratch if they don't exist (use kickstart)
# 3. Do the testing




# MAIN
#prepare_parent_img "http://download.lab.bos.redhat.com/rel-eng/OpenShift/Alpha/latest/DevOps/x86_64/os/"
#prepare_parent_img "http://buildvm-devops.usersys.redhat.com/puddle/build/OpenShift/Alpha/2012-08-28.3/DevOps/x86_64/os/" 1
#create_broker "${parent_vm_img}" "${broker_name}" 1
#add_node "${parent_vm_img}" "node0" "${broker_ip}" 1

#broker_ip="10.66.9.141"
#add_node "${parent_vm_img}" "node1" "$broker_ip" 1



