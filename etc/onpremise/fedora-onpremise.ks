###########################################################################
#
# the following MD5 encrypted passwords can be generated using
#
#    openssl passwd -1 redhat
#
#  see "man sslpasswd" for more information
#
###########################################################################
rootpw redhat
bootloader --location=mbr --md5pass=$1$x.3x1cDe$ucwc8hTScWzfb5DYW6r25/


###############################################################
# point to a local installation server, or use "cdrom"
###############################################################
text        # you're not going to be standing there watching it, are you?
url --url http://download.fedoraproject.org/pub/fedora/linux/releases/17/Fedora/x86_64/


###############################################################
# partitioning
###############################################################
zerombr
clearpart --all --initlabel 
part /boot --fstype ext3 --size 128 
part / --fstype ext4 --size 4096 --grow --maxsize 8192
#part /var --fstype ext4 --size 4096 --grow --maxsize 8192 
part swap --recommended 

###############################################################
# network configuration
#   - the following is for the "recommended solution" outlined
#     in the Red Hat Academy Instructor's Guide
###############################################################
network --bootproto=dhcp --device=eth0
#network --bootproto=static --ip=192.168.0.254 --netmask=255.255.255.0 --device=eth1
#firewall --enabled --http --ftp --port=https:tcp --port=ipp:tcp
firewall --disabled


###############################################################
# environment 
###############################################################
lang en_US
timezone Europe/Bratislava
#timezone America/New_York
#timezone America/Chicago
#timezone America/Denver
#timezone America/Los_Angeles

###############################################################
# hardware 
###############################################################
keyboard us
#xconfig --defaultdesktop=GNOME --startxonboot


###############################################################
# misc
###############################################################
auth  --useshadow
reboot                  # reboot automatically when done
install                 # instead of "upgrade"

###############################################################
#
# New in RHEL-4: SELinux
#
###############################################################
#selinux --enforcing
selinux --permissive
#selinux --disabled

###############################################################
#
# Software
#
###############################################################
%packages
@ DNS Name Server
@ Network Servers
@ Development Tools
@ System Tools

%end

%post
###############################################################
#
# Post Script - the following script runs on the newly
# installed machine, immediately after installation
#
###############################################################

########################################################
# add entry to /etc/hosts, if necessary
########################################################
#echo "192.168.0.254      rha-server" >> /etc/hosts

########################################################
# turn on required services
########################################################

chkconfig httpd on
chkconfig mongodb on
#chkconfig vsftpd on

########################################################
# install red hat academy custom software
########################################################

#RHASRC=ftp://kickstart.example.com/pub/rha/RPMS/
#rpm -ihv $RHASRC/rha-base*.rpm $RHASRC/rha-classroom-rha*.rpm $RHASRC/rha-server-*.rpm  $RHASRC/fauxlp-*.rpm
#unset RHASRC

########################################################
# add proxy server to /etc/rha_server.conf, if necessary
########################################################

#echo "ExerciseReporterProxy  http://10.1.1.1:8080" >> /etc/rha_server.conf


########################################################
# mirror RHEL-4-ES distribution from remote server
########################################################

#lftp -c "mirror ftp://kickstart.example.com/pub/es4 /var/ftp/pub/es4"

########################################################
# ln anonymous FTP pub dir to Document Root
########################################################

#ln -s ../../ftp/pub /var/www/html/pub
# set SELinux context s.t. contents of pub directory available from web
#chcon -R --reference /var/www/html /var/ftp/pub

# add another nameserver
echo "nameserver 10.0.1.10" >> /etc/resolv.conf
echo "10.0.1.10		server.local	server" >> /etc/resolv.conf
#yum-config-manager --enable rhel-6-server-optional-rpms   

cat <<EOF >/etc/yum.repos.d/openshift.repo
[openshift]
name=OpenShift
baseurl=http://mirror.openshift.com/pub/crankcase/rhel-6/x86_64/ 
enabled=1
gpgcheck=0
EOF

wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins-ci.org/redhat/jenkins.repo 
rpm --import http://pkg.jenkins-ci.org/redhat/jenkins-ci.org.key

rpm -ivh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-7.noarch.rpm

yum install mcollective mcollective-qpid-plugin mongodb qpid-cpp-server rubygem-gearchanger-mcollective-plugin rubygem-swingshift-mongo-plugin rubygem-uplift-bind-plugin rhc stickshift-broker

setsebool -P httpd_unified=on httpd_can_network_connect=on httpd_can_network_relay=on named_write_master_zones=on allow_ypbind=on

semodule -i /usr/share/selinux/packages/rubygem-stickshift-common/stickshift.pp
semodule -d passenger
semodule -i /usr/share/selinux/packages/rubygem-passenger/rubygem-passenger.pp
fixfiles -R rubygem-passenger restore
fixfiles -R mod_passenger restore
restorecon -rv /var/run
restorecon -rv /usr/lib/ruby/gems/1.8/gems/passenger-*
restorecon -rv /usr/sbin/mcollectived /var/log/mcollective.log /run/mcollective.pid

service mongod start
mongo stickshift_broker_dev --eval 'db.addUser("stickshift", "mooo")'

#Configuring the Firewall and Other Services 
lokkit --service=ssh
lokkit --service=https
lokkit --service=http
lokkit --service=dns
lokkit --port=5672:tcp

chkconfig httpd on
chkconfig mongod on
chkconfig network on
chkconfig sshd on
chkconfig stickshift-proxy on
chkconfig named on
chkconfig qpidd on
chkconfig stickshift-broker on
chkconfig mcollective off

cat <<EOF >/etc/mcollective/client.cfg
topicprefix = /topic/
main_collective = mcollective
collectives = mcollective
libdir = /usr/libexec/mcollective
loglevel = debug
logfile = /var/log/mcollective-client.log

# Plugins
securityprovider = psk
plugin.psk = unset
connector = qpid
plugin.qpid.host=broker.example.com
plugin.qpid.secure=false
plugin.qpid.timeout=5

# Facts
factsource = yaml
plugin.yaml = /etc/mcollective/facts.yaml
EOF

#
#Configure the OpenShift Plug-ins 
#
cat <<EOF >> /var/www/stickshift/broker/Gemfile
gem 'gearchanger-mcollective-plugin'
gem 'uplift-bind-plugin'
gem 'swingshift-mongo-plugin'
EOF

%end
