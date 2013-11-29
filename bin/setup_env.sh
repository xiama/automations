#!/bin/sh


if [ -z "$1"  ]; then
    echo "ERROR: Missing argument."
    echo "Usage: $0 <RHTEST_HOME directory>"
    exit 2
fi

echo "Please note this script won't be able to install rhc on Fedora 17"
echo "Warning: This script will change your kerberos configuration, bashrc, bash_profile and ssh configuration."
echo "Continue?(yes/no)"
read answer
if [ "$answer" != "yes" ];then
    exit 1
fi


RHTEST_HOME=$1
TEST_USER=$USER
PACKAGES_TO_INSTALL="git rhc pexpect python-sqlobject expect firefox chromium postgresql postgresql-devel rubygem-rails perl-ExtUtils-MakeMaker perl-Module-Build maven3 gcc-c++ rubygem-sqlite3 rubygem-rack-mount sqlite-devel rubygem-pg mongodb krb5-workstation httpd-tools python-pip python-paramiko python-kerberos python-selenium python-httplib2 java-1.7.0-openjdk ruby-devel python-devel perl-devel mysql-devel spawn make"

#if [ "root" == "$TEST_USER" ]; then
#    echo "ERROR: You must not be the superuser. "
#    exit 3;
#fi

sudo touch /tmp || ( echo "ERROR: SUDO is not configured properly for this user."; exit 3; )

set -e

########################
### APP/LIBS setup   ###
########################
sudo cp $RHTEST_HOME/etc/repo_key/li.repo /etc/yum.repos.d/
sudo cp $RHTEST_HOME/etc/repo_key/client-cert.pem /var/lib/yum/client-cert.pem
sudo cp $RHTEST_HOME/etc/repo_key/client-key.pem /var/lib/yum/client-key.pem

### install all necessary libraries ###
sudo yum -y --skip-broken update 
sudo yum -y --skip-broken install $PACKAGES_TO_INSTALL
sudo pip-python install itimer mysql-python sqlobject

########################
### setup SSH config ###
########################

mkdir -p $HOME/.ssh
cp -f $RHTEST_HOME/etc/libra.pem $HOME/.ssh/
SSH_CONFIG=$HOME/.ssh/config
touch $SSH_CONFIG
if [ -z "$(grep OPENSHIFT_SETUP $SSH_CONFIG)" ];  then
    cat <<'EOF' >> $SSH_CONFIG
### OPENSHIFT_SETUP ###
Host *.amazonaws.com
    User root
    IdentityFile ~/.ssh/libra.pem

Host *.dev.rhcloud.com
    IdentityFile ~/.ssh/id_rsa
    VerifyHostKeyDNS yes
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/dev_rhcloud_known_hosts

Host *.rhcloud.com
    VerifyHostKeyDNS yes
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/rhcloud_known_hosts

EOF
chmod 0600 $SSH_CONFIG
fi

########################
### Kerberos setup #####
########################

sudo cp -f /etc/krb5.conf{,_backup}
sudo cp -f $RHTEST_HOME/etc/krb5.conf_example /etc/krb5.conf

########################
### FRAMEWORK setup ####
########################
RUBY_VER=`ruby -v | cut -d' ' -f 2 | cut -d '.' -f 1-2 | tr -d '\n'`
GEM_HOME="/usr/lib/ruby/gems/$RUBY_VER"
touch $HOME/.bash_profile
if [ -z "$(grep OPENSHIFT_SETUP $HOME/.bash_profile)" ];  then
    echo "GEM_HOME=$GEM_HOME" >> $HOME/.bash_profile
    echo 'RHTEST_HOME=$RHTEST_HOME' >> $HOME/.bash_profile
    echo 'PYTHOPATH=$RHTEST_HOME/lib:$RHTEST_HOME/lib/supports:$RHTEST_HOME/testmodules/' >> $HOME/.bash_profile
    echo 'PATH=$PATH:$RHTEST_HOME/bin' >> $HOME/.bash_profile
fi

RESULTS_DIR=/var/www/html/testresults/
sudo mkdir -p $RESULTS_DIR
sudo chmod 777 $RESULTS_DIR
sudo setfacl -d -m other::rwx $RESULTS_DIR

########################
### OPENSHIFT setup ####
########################
if [ ! -f $HOME/.openshift/express.conf ]; then
    mkdir -p $HOME/.openshift
    cat <<EOF >$HOME/.openshift/express.conf

libra_server=stg.openshift.redhat.com

EOF

fi

sudo gem install bundle
#REDIS dependencies
sudo gem install mail -v '2.2.19'
sudo gem install rack -v '1.4.1'
sudo gem install therubyracer
sudo gem install execjs
sudo gem install rack-mount -v '0.8.3'
sudo gem install pg
sudo gem install redis -v '3.0.1'
#sudo gem install thread-dump -v '0.0.5'

#
#for jenkins working with sudo we must disable using `requiretty` in /etc/sudoers
#
sudo sed -i -e 's/^\(Defaults\s\+requiretty\)/#\1/' /etc/sudoers
exit 0
