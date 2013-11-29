#!/bin/bash
#
# mzimen@redhat.com 2012
#
#
# This script helps to have multiple accounts which can run only ONE job per time 
#   - because of conflicts with .openshift/express.conf
# Just run it locally with new_username and remote_host as arguments.

####################################################################################3
####################################################################################3
####################################################################################3
#1. scp this job to remote station
####################################################################################3
####################################################################################3
####################################################################################3


if [ -z "$2" ]; then
    echo "Usage: $0 <USER> <REMOTE_HOST>"
    exit 2
fi

SSH_KEY=jenkins.pub
if [ ! -f ~/.ssh/$SSH_KEY ]; then
    echo "Missing SSH key ~/.ssh/$SSH_KEY for accessing this node..."
    exit 3
fi

HOST=$2
: ${HOST:=localhost}
SCRIPT_NAME=setup_testing_account.sh
SCRIPT=/tmp/$SCRIPT_NAME
cat <<JOB >$SCRIPT
echo "Creating a OpenShift QA testing user $1 ..."

#set -e

if [ "\$UID" != "0" ]; then
    echo "You must be ROOT to run this script"
    exit 2
fi

adduser $1 || exit
echo "setup 'redhat' password..."
mkdir -p /home/$1
chown $1:$1 /home/$1
expect <<PASSWD
spawn passwd $1
expect {
    password: {send "redhat\r" ; exp_continue}
    eof exit
}
PASSWD

cat <<'EOF' >/home/$1/run_as_user.sh
#!/bin/sh

cd /home/$1

mkdir -p /home/$1/.ssh
mkdir -p /home/$1/.openshift || exit
export RHTEST_HOME=/home/$1/openshift/
echo "Setting RHTEST_HOME to \$RHTEST_HOME"
cp /tmp/.awscred /home/$1/.awscred
#
#OpenShift
#
cat <<'EOF0' >/home/$1/.openshift/express.conf
libra_server=int.openshift.redhat.com
# Default rhlogin to use if none is specified
default_rhlogin=jenkins+$1@redhat.com
EOF0

cat <<'EOF1' >/home/$1/.openshiftrc
export RHTEST_HOME=/home/$1/openshift/
export PYTHONPATH=\${RHTEST_HOME}/lib/supports:\${RHTEST_HOME}/lib:\${RHTEST_HOME}/testmodules
export PATH=\${RHTEST_HOME}/bin:\$PATH
export OPENSHIFT_libra_server='int.openshift.redhat.com'
export OPENSHIFT_user_email=jenkins+$1@redhat.com
export OPENSHIFT_user_passwd=redhat
EOF1

echo "SSH setup..."
cat <<EOF2 >/home/$1/.ssh/config

Host *.rhcloud.com
    IdentityFile ~/.ssh/id_rsa
    VerifyHostKeyDNS yes
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/openshift_known_hosts

EOF2

cat /tmp/$SSH_KEY >>/home/$1/.ssh/authorized_keys
chmod 600 /home/$1/.ssh/config

echo "GIT setup..."
git config --global user.name  "jenkins+$1"
git config --global user.email "jenkins+$1@redhat.com"

#echo "CRON setup..."
#echo "* * * * * /usr/local/bin/whatever.sh" | crontab -

echo "RHTEST setup..."
URL="git://qe-git.englab.nay.redhat.com/hss-qe/openshift/openshift-express/automation"
mkdir -p \$RHTEST_HOME
git clone \$URL \$RHTEST_HOME
EOF

cp ~/.ssh/$SSH_KEY /tmp
chmod +x /home/$1/run_as_user.sh
echo "Run as the '$1' user..."
pushd /home/$1
sudo -u $1 /home/$1/run_as_user.sh
rm -f /home/$1/run_as_user.sh
popd

[ -f /home/$1/.ssh/authorized_keys ] || echo "Warning: Missing authorized_keys file"

echo "Add wheel group to sudoers"
sed -i -e 's/#.*%wheel.*$/%wheel  ALL=(ALL)       NOPASSWD: ALL/' /etc/sudoers
echo "Add user to wheel group"
usermod -aG wheel $1

JOB
echo "Copying the ssh key"
scp ~/.ssh/$SSH_KEY root@$HOST:
echo "Copying the script..."
scp $SCRIPT root@$HOST:$SCRIPT

####################################################################################3
####################################################################################3
####################################################################################3
#2. Run this script
####################################################################################3
####################################################################################3
####################################################################################3

echo "Run 'chmod +x ...'"
ssh root@$HOST chmod +x $SCRIPT
echo "Run the script..."
ssh -t root@$HOST $SCRIPT

