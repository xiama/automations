#!/bin/bash
#
#
# Generated from https://hosted.englab.nay.redhat.com/issues/11110
#
# mzimen@redhat.com
#

#set -e

function usage(){
    echo "Usage: $0 <tag> [size=2] [node profiles list]"
}

function set_profile(){
    node=$1
    profile=$2
    config_file="/etc/openshift/resource_limits.conf"
    profile_file="${config_file}.${profile}"
    ssh -i $HOME/.ssh/libra.pem root@$node <<EOF
    cd /etc/openshift
    rm -f $config_file 
    ln -v -s $profile_file $config_file
    /usr/libexec/mcollective/update_yaml.rb /etc/mcollective/facts.yaml
EOF
}

function add_node2district(){
    DISTRICT_NAME=$1
    NODE=$2
    ssh -i $HOME/.ssh/libra.pem root@verifier <<EOF
    rhc-admin-ctl-district -c add-node -n $DISTRICT_NAME -i $NODE
EOF
}

function create_district(){
    DISTRICT_NAME=$1
    PROFILE=$2
       #(small(default)|jumbo|exlarge|large|medium|micro|c9) Only needed for create
    ssh -i $HOME/.ssh/libra.pem root@verifier <<EOF
    rhc-admin-ctl-district -c create -n $DISTRICT_NAME -p $PROFILE
EOF
}

if [ -z "$1" ]; then
    usage;
    exit 2
fi

TAG=$1
SIZE=$2
: ${SIZE:=2}
shift 2
PROFILES=$*

TMP=$(mktemp -d) 
cd $TMP
git clone git@github.com:openshift/li.git li
if [ ! -f ./li/build/devenv ]; then
    echo "Unable to locate LI repository"
    exit 3;
fi

#clean .ssh/config from old verifier*
sed -e "/verifier/,+3d" -i  $HOME/.ssh/config
sed -e "/werifier/,+3d" -i  $HOME/.ssh/config

#1. Prepare two devenv instances, assume their name is "node1" and "node2".
for i in `seq 1 $SIZE`; do
    echo "Building node#$i"
    ./li/build/devenv launch ${TAG}${i} --express_server --ssh_config_verifier 
    IP=$(ssh verifier ip a ls dev eth0 | awk '/inet/{split($2,a,"/");print a[1]}') 
    echo "IP_$i: $IP"
    sleep 3
    eval "NODE${i}_IP=$IP"
    sed -e "s/verifier$/werifier$i/" -i  $HOME/.ssh/config
done


echo "Setting BROKER_HOST on $NODE1_IP"
sed -e "s/werifier1/verifier/" -i  $HOME/.ssh/config
sed -e "s/werifier/verifier/" -i  $HOME/.ssh/config
ssh root@verifier <<EOF
sed -i -e "s/BROKER_HOST=.*/BROKER_HOST=$NODE1_IP/" /etc/openshift/openshift-node.conf
cat /etc/openshift/openshift-node.conf | grep BROKER_HOST
EOF
echo "done."

for i in `seq 1 $SIZE`; do
    if [ "$i" == "1" ]; then 
        echo "Setup multi node broker..."
        ./li/build/devenv setup_multi_node_broker --verbose
    else
        echo "Adding node#$i ..."
        ./li/build/devenv add_multi_node_devenv verifier$i --verbose
    fi
    
done

i=""
for profile in $PROFILES; do
    host="verifier$i"
    echo "Setting profile to $profile on $host ..."
    set_profile $host $profile
    if [ "$i" == "" ]; then
        i=1
    fi
    #setup district per each node profile...
    DISTRICT_NAME="qa$profile"
    echo "Creating/Updating district: $DISTRICT_NAME"  #per each node profile...
    if [ "$SIZE" -gt 1 ]; then
        create_district $DISTRICT_NAME $profile || true #it might fail/ignore it
        eval "ref=NODE${i}_IP"
        eval "IP=\$$ref"
        add_node2district $DISTRICT_NAME $IP
    fi
    i=$(( $i+1 ))
done

#Cleaning up the LI repository
rm -rf $TMP

echo "\nConfiguration:"
for i in `seq 1 $SIZE`; do
    eval "ref=NODE${i}_IP"
    eval "IP=\$$ref"
    echo -e "\tIP[$i]: $IP"
done

exit 0

======================================AUTO======================================

#1. Prepare two devenv instances, assume their name is "node1" and "node2".


E.g:

node1's IP: 10.113.42.21 (QPID server, Broker Server and a common Node)


node2's IP: 10.2.187.186 (a common Node)


#2. Add the following to ~/.ssh/config in your local machine


Host verifier
   User root
   IdentityFile <path-to>/libra.pem
   HostName <node1.public.hostname>


Host verifier2
   User root
   IdentityFile <path-to>/libra.pem
   HostName <node2.public.hostname>


#3. Git clone li repo. Firstly you need access permission to li repo, if you have not, you can run the following command on a instance without any access permission, then cp all file to your local machine using scp command.


$ git clone git://git1.ops.rhcloud.com/li.git


#4. On node1, edit /etc/openshift/openshift-node.conf.

# vi /etc/openshift/openshift-node.conf

BROKER_HOST=10.113.42.21


#5. Run the following command to setup broker node.

$ cd <li.repo>/build

$ ./devenv setup_multi_node_broker --verbose


#6. Run the following command to add a common node.

#$ ./devenv add_multi_node_devenv verifier2 --verbose

