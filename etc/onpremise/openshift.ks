# This kickstart script configures a system that acts as either a node or
# a broker.
#
# TODO: Comment everything better.
#
# TODO: Figure out which commands in %post are unnecessary.
# XXX: Some commands are definitely unnecessary (e.g., some semanage
# commands that specify settings that are already default).  Should we
# keep these commands?
#
# TODO: Refactor things:
#
#  - yum-install commands in %post should go under %packages (but then
#    do we need redundant repo commands and repository configuration in
#    %post?);
#
#  - packages should include dependencies where reasonable so the
#    dependencies need not be explicitly installed;
#
#  - where possible, configuration should be moved to the relevant
#    packages, or those packages should be changed to facilitate brevity
#    in whatever configuration belongs here;
#
#  - some of the commands in %post might belong in the post-install
#    scripts for specific packages, although we want to avoid opacity in
#    how the broker and nodes ultimately end up in their configured
#    states, we want to avoid weird ordering dependencies in
#    configuration scripts, and we want to avoid creating packages that
#    only exist to perform configuration (e.g., the old
#    openshift-origin-broker and openshift-origin-node packages);
#
#  - and generally, we should use standard kickstart commands wherever
#    possible instead of commands in %post.
#
#version=DEVEL
install
text
skipx

# NB: Be sure to change the password.
rootpw  --iscrypted $6$QgevUVWY7.dTjKz6$jugejKU4YTngbFpfNlqrPsiE4sLJSj/ahcfqK8fE5lO0jxDhvdg59Qjk9Qn3vNPAUTWXOp9mchQDy6EV9.XBW1

lang en_US.UTF-8
keyboard us
timezone --utc America/New_York

# XXX: We could replace some of the network, firewall, and services
# configuration in %post by tweaks to the following rules.
services --enabled=ypbind,ntpd,network,logwatch
network --onboot yes --device eth0
firewall --service=ssh
authconfig --enableshadow --passalgo=sha512
selinux --enforcing

# XXX: Should we give OpenShift a higher or lower --cost than base?
# XXX: This doesn't work--apparently, the repo command only makes the
# repositories available during the installation process but does not
# set them up in /etc/yum.repos.d, so we must set the repositories up
# below in %post instead.
#repo --name="Extra Packages for Enterprise Linux 6" --mirrorlist="https://mirrors.fedoraproject.org/metalink?repo=epel-6&arch=x86_64"
#repo --name="OpenShift DevOps Alpha" --baseurl="http://download.lab.bos.redhat.com/rel-eng/OpenShift/Alpha/2012-08-09.2/DevOps/x86_64/os/"
#repo --name="OpenShift DevOps Alpha" --baseurl="http://download.lab.bos.redhat.com/rel-eng/OpenShift/Alpha/latest/DevOps/x86_64/os/"

url --url http://download.fedoraproject.org/pub/fedora/linux/releases/17/Fedora/x86_64/
bootloader --location=mbr --driveorder=vda --append=" rhgb crashkernel=auto quiet console=ttyS0"

zerombr
clearpart --all --initlabel
firstboot --disable
reboot

part /boot --fstype=ext4 --size=500
part pv.253002 --grow --size=1
volgroup vg_vm1 --pesize=4096 pv.253002
logvol / --fstype=ext4 --name=lv_root --vgname=vg_vm1 --grow --size=1024 --maxsize=51200
logvol swap --name=lv_swap --vgname=vg_vm1 --grow --size=2016 --maxsize=4032

%packages
@core
@server-policy
ntp
git
%end
# TODO: Move the yum install commands below up here.

%post --log=/root/anaconda-post.log

# You can use sed to extract just the %post section:
#    sed -e '0,/^%post/d;/^%end/,$d'

# Log the command invocations (and not merely output) in order to make
# the log more useful.
set -x

# Open a new VT that displays everything that's going on here in %post.
openvt tailf /mnt/sysimage/root/anaconda-post.log

########################################################################

# Synchronize the system clock to the NTP servers and then synchronize
# hardware clock with that.
synchronize_clock()
{
  # Synchronize the system clock using NTP.
  ntpdate clock.corp.redhat.com

  # Synchronize the hardware clock to the system clock.
  hwclock --systohc
}


# Install SSH keys.  We hardcode a key used for internal OpenShift
# development, but the hardcoded key can be replaced with another or
# with a wget command to download a key from elsewhere.
install_ssh_keys()
{
  mkdir /root/.ssh
  chmod 700 /root/.ssh
  cat >> /root/.ssh/authorized_keys << KEYS
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDkMc2jArUbWICi0071HXrt5uofQam11duqo5KEDWUZGtHuMTzuoZ0XEtzpqoRSidya9HjbJ5A4qUJBrvLZ07l0OIjENQ0Kvz83alVGFrEzVVUSZyiy6+yM9Ksaa/XAYUwCibfaFFqS9aVpVdY0qwaKrxX1ycTuYgNAw3WUvkHagdG54/79M8BUkat4uNiot0bKg6VLSI1QzNYV6cMJeOzz7WzHrJhbPrgXNKmgnAwIKQOkbATYB+YmDyHpA4m/O020dWDk9vWFmlxHLZqddCVGAXFyQnXoFTszFP4wTVOu1q2MSjtPexujYjTbBBxraKw9vrkE25YZJHvbZKMsNm2b libra_onprem
KEYS
}


# Set up the yum repositories for RHEL, OpenShift, and EPEL.
configure_yum_repos()
{
  yum-config-manager --enable rhel-6-server-optional-rpms

  # Enable the EPEL.
  rpm -ivh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-7.noarch.rpm

  # Enable the jenkins repo.
  wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins-ci.org/redhat/jenkins.repo
  rpm --import http://pkg.jenkins-ci.org/redhat/jenkins-ci.org.key
}


# Install packages that are common to the broker and the node.
#
# TODO: stickshift-broker and rubygem-stickshift-node should depend on
# the other packages.  For now, the other packages must be explicitly
# installed.
install_common_pkgs()
{
  # Kickstart doesn't handle line continuations.
  pkgs="mcollective mcollective-qpid-plugin mongodb"

  yum install -y $pkgs
}

# Install broker-specific packages.
install_broker_pkgs()
{
  # Kickstart doesn't handle line continuations.
  pkgs="qpid-cpp-server rubygem-gearchanger-mcollective-plugin"
  pkgs="$pkgs rubygem-swingshift-mongo-plugin rubygem-uplift-bind-plugin"
  pkgs="$pkgs rhc stickshift-broker"

  yum install -y $pkgs
}

# Install node-specific packages.
install_node_pkgs()
{
  pkgs="stickshift-mcollective-agent mcollective-client"
  pkgs="$pkgs stickshift-port-proxy rubygem-passenger-native"
  pkgs="$pkgs rubygem-stickshift-node"
  yum install -y $pkgs
}

# Install any cartridges developers may want.
install_cartridges()
{
  :
  # Following are cartridge rpms that one may want to install here:

  # 10gen MMS agent for performance monitoring of MongoDB.
  #yum install cartridge-10gen-mms-agent -y

  # Embedded cron support.
  yum install cartridge-cron-1.4 -y

  # diy app.
  #yum install cartridge-diy-0.1 -y

  # haproxy-1.4 support.
  #yum install cartridge-haproxy-1.4 -y

  # JBossAS7 support.
  #yum install cartridge-jbossas-7 -y

  # JBossEAP6.0 support.
  #yum install cartridge-jbosseap-6.0 -y

  # Jenkins server for continuous integration.
  #yum install cartridge-jenkins-1.4 -y

  # Embedded jenkins client.
  #yum install cartridge-jenkins-client-1.4 -y

  # Embedded metrics support.
  #yum install cartridge-metrics-0.1 -y

  # Embedded MongoDB.
  #yum install cartridge-mongodb-2.0 -y

  # Embedded MySQL.
  #yum install cartridge-mysql-5.1 -y

  # NodeJS support.
  #yum install cartridge-nodejs-0.6 -y

  # mod_perl support.
  #yum install cartridge-perl-5.10 -y

  # PHP 5.3 support.
  yum install cartridge-php-5.3 -y

  # Embedded phpMoAdmin.
  #yum install cartridge-phpmoadmin-1.0 -y

  # Embedded phpMyAdmin.
  #yum install cartridge-phpmyadmin-3.4 -y

  # Embedded PostgreSQL.
  #yum install cartridge-postgresql-8.4 -y

  # Python 2.6 support.
  #yum install cartridge-python-2.6 -y

  # Embedded RockMongo support.
  #yum install cartridge-rockmongo-1.1 -y

  # Ruby Rack support running on Phusion Passenger (Ruby 1.8).
  #yum install cartridge-ruby-1.8 -y

  # Ruby Rack support running on Phusion Passenger (Ruby 1.9).
  #yum install cartridge-ruby-1.9 -y
}


# Fix up SELinux policy on the broker.
configure_selinux_policy_on_broker()
{
  # We combine these setsebool commands into a single semanage command
  # because separate commands take a long time to run.
  (
    # Allow the broker to write files in the http file context.
    echo boolean -m --on httpd_unified

    # Allow the broker to access the network.
    echo boolean -m --on httpd_can_network_connect
    echo boolean -m --on httpd_can_network_relay

    # XXX: The above httpd_* settings are on by default.  Do we need to
    # enable them explicitly?

    # Allow the broker to configure DNS.
    echo boolean -m --on named_write_master_zones

    # Allow ypbind so that the broker can communicate directly with the name
    # server.
    echo boolean -m --on allow_ypbind

    # Load the OpenShift policy file.
    echo module -a /usr/share/selinux/packages/rubygem-stickshift-common/stickshift.pp

    # Delete the old passenger policy and load the OpenShift policy for passenger.
    echo module -d passenger
    echo module -a /usr/share/selinux/packages/rubygem-passenger/rubygem-passenger.pp
  ) | semanage -i -
}

# Fix up SELinux policy on the node.
configure_selinux_policy_on_node()
{
  # We combine these setsebool commands into a single semanage command
  # because separate commands take a long time to run.
  (
    # Allow the node to access the network.
    echo boolean -m --on httpd_can_network_connect
    echo boolean -m --on httpd_can_network_relay

    # Allow the node to access apps.
    echo boolean -m --on httpd_read_user_content
    echo boolean -m --on httpd_enable_homedirs

    # XXX: The above httpd_* settings are on by default.  Do we need to
    # enable them explicitly?

    # Load the OpenShift policy file.
    echo module -a /usr/share/selinux/packages/rubygem-stickshift-common/stickshift.pp

    # Delete the old passenger policy and load the OpenShift policy for passenger.
    echo module -d passenger
    echo module -a /usr/share/selinux/packages/rubygem-passenger/rubygem-passenger.pp
  ) | semanage -i -
}

fix_selinux_contexts()
{
  fixfiles -R rubygem-passenger restore
  fixfiles -R mod_passenger restore

  restorecon -R -v /var/run
  restorecon -rv /usr/lib/ruby/gems/1.8/gems/passenger-*
  restorecon -r /usr/sbin/mcollectived /var/log/mcollective.log /run/mcollective.pid
  node && restorecon -r /var/lib/stickshift /etc/stickshift/stickshift-node.conf /etc/httpd/conf.d/stickshift
}


# Turn some sysctl knobs.
configure_sysctl_on_node()
{
  # Increase kernel semaphores to accomodate many httpds.
  echo "kernel.sem = 250  32000 32  4096" >> /etc/sysctl.conf

  # Move ephemeral port range to accommodate app proxies.
  echo "net.ipv4.ip_local_port_range = 15000 35530" >> /etc/sysctl.conf

  # Increase the connection tracking table size.
  echo "net.netfilter.nf_conntrack_max = 1048576" >> /etc/sysctl.conf

  # Reload sysctl.conf to get the new settings.
  #
  # Note: We could add -e here to ignore errors that are caused by
  # options appearing in sysctl.conf that correspond to kernel modules
  # that are not yet loaded.  On the other hand, adding -e might cause
  # us to miss some important error messages.
  sysctl -p /etc/sysctl.conf
}


# Configure sshd to pass the GIT_SSH environment variable through.
# XXX: Should GIT_SSH be passed through on the broker?
passthrough_git_ssh_env()
{
  echo 'AcceptEnv GIT_SSH' >> /etc/ssh/sshd_config
}


# Up the limits on the number of connections to a given node.
increase_ssh_limits_on_node()
{
  perl -p -i -e "s/^#MaxSessions .*$/MaxSessions 40/" /etc/ssh/sshd_config
  perl -p -i -e "s/^#MaxStartups .*$/MaxStartups 40/" /etc/ssh/sshd_config
}


# Establish a symlink for developer SSH logins.
# Note: This symlink should be a part of the rubygem-stickshift-node
# package.
add_rhcsh_symlink_on_node()
{
  ln -s /usr/bin/sssh /usr/bin/rhcsh
}


# Configure MongoDB.
configure_mongodb()
{
  # Require authentication.
  perl -p -i -e "s/^#auth = .*$/auth = true/" /etc/mongodb.conf

  # Use a smaller default size for databases.
  if [ "x`fgrep smallfiles=true /etc/mongodb.conf`x" != "xsmallfiles=truex" ]
  then
    echo 'smallfiles=true' >> /etc/mongodb.conf
  fi

  # Start mongod so we can perform some administration now.
  service mongod start

  # The init script is broken as of version 2.0.2-1.el6_3: The start and
  # restart actions return before the daemon is ready to accept
  # connections (it appears to take time to initialize the journal).  Thus
  # we need the following hack to wait until the daemon is ready.
  echo "Waiting for MongoDB to start ($(date +%H:%M:%S))..."
  while :
  do
    echo exit | mongo && break
    sleep 5
  done
  echo "MongoDB is finally ready! ($(date +%H:%M:%S))"

  # Set the password.
  # XXX: Parameterize the password.
  mongo stickshift_broker_dev --eval 'db.addUser("stickshift", "mooo")'
  #sed -i -e '/:password => "mooo"/s/mooo/<password>/' /var/www/stickshift/broker/config/environments/development.rb

  # Add user "admin" with password "admin" for ss-register-user and such.
  mongo stickshift_broker_dev --eval 'db.auth_user.update({"_id":"admin"}, {"_id":"admin","user":"admin","password":"2a8462d93a13e51387a5e607cbd1139f"}, true)'
}


# Open up services required on the broker.
configure_firewall_on_broker()
{
  # We use --nostart below because activating the configuration here will
  # produce errors.  Anyway, we only need the configuration activated
  # after Anaconda reboots, so --nostart makes sense in any case.

  lokkit --nostart --service=ssh
  lokkit --nostart --service=https
  lokkit --nostart --service=http
  lokkit --nostart --service=dns
  lokkit --nostart --port=5672:tcp
}


# Open up services required on the node for apps and developers.
configure_firewall_on_node()
{
  lokkit --nostart --service=ssh
  lokkit --nostart --service=https
  lokkit --nostart --service=http
  lokkit --nostart --port=35531-65535:tcp
}


# Enable services to start on boot for the node.
enable_services_on_node()
{
  chkconfig httpd on
  chkconfig mcollective on
  chkconfig network on
  chkconfig sshd on
}


# Enable services to start on boot for the broker.
enable_services_on_broker()
{
  chkconfig httpd on
  chkconfig network on
  chkconfig sshd on
  chkconfig mongod on
  chkconfig named on
  chkconfig qpidd on
  chkconfig stickshift-broker on
}


# Configure mcollective.
configure_mcollective_on_broker()
{
  cat <<EOF > /etc/mcollective/client.cfg
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
plugin.qpid.host=${broker_hostname}.${domain}
plugin.qpid.secure=false
plugin.qpid.timeout=5

# Facts
factsource = yaml
plugin.yaml = /etc/mcollective/facts.yaml
EOF

  cat <<EOF > /etc/mcollective/server.cfg
topicprefix = /topic/
main_collective = mcollective
collectives = mcollective
libdir = /usr/libexec/mcollective
logfile = /var/log/mcollective.log
loglevel = debug
daemonize = 1
direct_addressing = n

# Plugins
securityprovider = psk
plugin.psk = unset
connector = qpid
plugin.qpid.host=${broker_hostname}.${domain}
plugin.qpid.secure=false
plugin.qpid.timeout=5

# Facts
factsource = yaml
plugin.yaml = /etc/mcollective/facts.yaml
EOF
}


# Configure qpid.
configure_qpid()
{
  if [[ "x`fgrep auth= /etc/qpidd.conf`" == xauth* ]]
  then
    sed -i -e 's/auth=yes/auth=no/' /etc/qpidd.conf
  else
    echo "auth=no" >> /etc/qpidd.conf
  fi
}


# Configure BIND.
configure_named_on_broker()
{
  # $keyfile will contain a new DNSSEC key for our domain.
  keyfile=/var/named/${domain}.key

  # Generate the new key for the domain.
  # XXX: Do we use USER or HOST?
  # https://openshift.redhat.com/community/wiki/local-dynamic-dns-service#Integrated_Local_DNS_Service
  # uses USER, but ss-setup-bind uses HOST.
  rm -f /var/named/K${domain}*
  pushd /var/named
  dnssec-keygen -a HMAC-MD5 -b 512 -n USER -r /dev/urandom ${domain}
  KEY="$(grep Key: K${domain}*.private | cut -d ' ' -f 2)"
  popd

  # Ensure we have a key for the broker to communicate with BIND.
  # XXX: Do we need the if-then statement? Either the key should always
  # be there or it will never be there.
  if [[ ! -f /etc/rndc.key ]]
  then
    rndc-confgen -a -r /dev/urandom
  fi
  restorecon /etc/rndc.* /etc/named.*
  chown root:named /etc/rndc.key
  chmod 640 /etc/rndc.key

  # Set up DNS forwarding.
  # XXX: Read from resolv.conf?
  cat <<EOF > /var/named/forwarders.conf
forwarders { ${nameservers} } ;
EOF
  restorecon /var/named/forwarders.conf
  chmod 755 /var/named/forwarders.conf

  # Install the configuration file for the OpenShift On-Premise domain
  # name.
  rm -rf /var/named/dynamic
  mkdir -p /var/named/dynamic

  uplift="$(rpm -q rubygem-uplift-bind-plugin --qf '%{NAME}-%{VERSION}')"
  sed "s/example.com/${domain}/g" < /usr/lib/ruby/gems/1.8/gems/${uplift#rubygem-}/doc/examples/example.com.db > /var/named/dynamic/${domain}.db

  # Install the key for the OpenShift On-Premise domain.
  cat <<EOF > /var/named/${domain}.key
key ${domain} {
  algorithm HMAC-MD5;
  secret "${KEY}";
};
EOF

  chown named:named -R /var/named
  restorecon -R /var/named

  # Update named.conf.
  sed "s/example.com/${domain}/g" < /usr/share/doc/${uplift}/examples/named.conf > /etc/named.conf
  chown root:named /etc/named.conf
  /usr/bin/chcon system_u:object_r:named_conf_t:s0 -v /etc/named.conf

  # Start named so we can perform some updates immediately.
  service named start

  # Tell BIND about the broker.
  nsupdate -k ${keyfile} <<EOF
server 127.0.0.1
update delete ${broker_hostname}.${domain} A
update add ${broker_hostname}.${domain} 180 A ${broker_ip_addr}
send
EOF
}


# Make resolv.conf point to localhost to use the newly configured named
# on the broker.
update_resolv_conf_on_broker()
{
  # Update resolv.conf to use the local BIND instance.
  # XXX: ss-setup-broker throws in the same DNS servers from
  # forwarders.conf, but isn't that redundant?
  cat <<EOF > /etc/resolv.conf
nameserver 127.0.0.1
EOF
}


# Make resolv.conf point to the broker, which will resolve the host
# names used in this installation of OpenShift.  The broker will forward
# other requests to some other DNS servers.
# on the broker.
update_resolv_conf_on_node()
{
  # Update resolv.conf to use the broker.
  cat <<EOF > /etc/resolv.conf
nameserver ${broker_ip_addr}
EOF
}


# Configure the broker to use the MongoDB authentication plugin, the
# Uplift BIND plugin, and the mcollective RPC plugin.
configure_swingshift_plugins()
{
  # Use MongoDB for authentication.
  sed -i -e "s/^# Add plugin gems here/# Add plugin gems here\ngem 'swingshift-mongo-plugin'\n/" /var/www/stickshift/broker/Gemfile
  echo "require File.expand_path('../plugin-config/swingshift-mongo-plugin.rb', __FILE__)" >> /var/www/stickshift/broker/config/environments/development.rb

  # Use BIND for DNS.
  sed -i -e "s/^# Add plugin gems here/# Add plugin gems here\ngem 'uplift-bind-plugin'\n/" /var/www/stickshift/broker/Gemfile
  echo "require File.expand_path('../plugin-config/uplift-bind-plugin.rb', __FILE__)" >> /var/www/stickshift/broker/config/environments/development.rb
  pushd /usr/share/selinux/packages/rubygem-uplift-bind-plugin/ && make -f /usr/share/selinux/devel/Makefile ; popd
  semodule -i /usr/share/selinux/packages/rubygem-uplift-bind-plugin/dhcpnamedforward.pp

  mkdir -p /var/www/stickshift/broker/config/environments/plugin-config
  cat <<EOF > /var/www/stickshift/broker/config/environments/plugin-config/uplift-bind-plugin.rb
Broker::Application.configure do
  config.dns = {
    :server => "127.0.0.1",
    :port => 53,
    :keyname => "${domain}",
    :keyvalue => "${KEY}",
    :zone => "${domain}"
  }
end
EOF
  perl -p -i -e "s/.*:domain_suffix.*/    :domain_suffix => \"${domain}\",/" /var/www/stickshift/broker/config/environments/*.rb
  # */ # What the heck, VIM syntax highlighting? Kickstart scripts do not use
  #  C-style comments.
  chown apache:apache /var/www/stickshift/broker/config/environments/plugin-config/uplift-bind-plugin.rb
  restorecon /var/www/stickshift/broker/config/environments/plugin-config/uplift-bind-plugin.rb

  # Use mcollective for RPC.
  sed -i -e "s/^# Add plugin gems here/# Add plugin gems here\ngem 'gearchanger-mcollective-plugin'\n/" /var/www/stickshift/broker/Gemfile
  echo "require File.expand_path('../plugin-config/gearchanger-mcollective-plugin.rb', __FILE__)" >> /var/www/stickshift/broker/config/environments/development.rb
}


# Configure IP address and hostname.
configure_network()
{
  # Append some stuff to the DHCP configuration.
  cat <<EOF >> /etc/dhcp/dhclient-eth0.conf

prepend domain-name-servers ${broker_ip_addr};
supersede host-name "${hostname}";
supersede domain-name "${domain}";
EOF

  # Set the hostname.
  sed -i -e "s/HOSTNAME=.*/HOSTNAME=${hostname}.${domain}/" /etc/sysconfig/network
  hostname "${hostname}"
}


# Set some parameters in the OpenShift node configuration file.
configure_node()
{
  perl -p -i -e "s/^PUBLIC_IP=.*$/PUBLIC_IP=${node_ip_addr}/" /etc/stickshift/stickshift-node.conf
  perl -p -i -e "s/^CLOUD_DOMAIN=.*$/CLOUD_DOMAIN=${domain}/" /etc/stickshift/stickshift-node.conf
  perl -p -i -e "s/^PUBLIC_HOSTNAME=.*$/PUBLIC_HOSTNAME=${hostname}.${domain}/" /etc/stickshift/stickshift-node.conf
  perl -p -i -e "s/^BROKER_HOST=.*$/BROKER_HOST=${broker_ip_addr}/" /etc/stickshift/stickshift-node.conf
}


# Run the cronjob installed by stickshift-mcollective-agent immediately
# to regenerate facts.yaml.
update_stickshift_facts_on_node()
{
  /etc/cron.minutely/stickshift-facts
}

# This is a hack to make Bundle work properly.
fix_gemfile_lock()
{
  pushd /var/www/stickshift/broker
  wget https://raw.github.com/openshift/crankcase/master/stickshift/broker/Gemfile.lock
  sed -i -e '/stickshift-\(controller\|node\) (/d' Gemfile.lock
  bundle --local
  popd
}


########################################################################

#
# Parse the kernel command-line, define variables with the parameters
# specified on it, and define functions broker() and node(), which
# return true or false as appropriate based on whether we are
# configuring the host as a broker or as a node.
#

for word in $(cat /proc/cmdline)
do
  key="${word%%\=*}"
  case "$word" in
    (*=*) val="${word#*\=}" ;;
    (*) val=true ;;
  esac
  export CONF_${key^^}="$val"
done

# Define broker and node functions which return true or false as
# appropriate based on whether we are configuring the host as a broker
# or as a node.
[[ $CONF_INSTALL_BROKER =~ (1|true) ]] && broker() { :; } || broker() { false; }

[[ $CONF_INSTALL_NODE =~ (1|true) ]] && node() { :; } || node() { false; }

# If neither node nor broker is specified, define both broker and node
# to true so we install everything.
node || broker || { broker() { :; }; node() { :; }; }

node && echo Installing node components.
broker && echo Installing broker components.

#
# Following are some settings used in subsequent steps.
#

# The domain name for this OpenShift On-Premise installation.
domain="${CONF_DOMAIN:-example.com}"

# The hostname of the broker.
broker_hostname="${CONF_BROKER_HOSTNAME:-broker}"

# The hostname of the node.
node_hostname="${CONF_NODE_HOSTNAME:-node}"

# The hostname name for this host.
node && hostname="$node_hostname"
broker && hostname="$broker_hostname"

# The IP address of the broker.  If no IP address is given on the kernel
# command-line, the IP address of the current host is used.
broker_ip_addr="${CONF_BROKER_IP_ADDR:-$(/sbin/ip addr show dev eth0 | awk '/inet / { split($2,a,"/"); print a[1]; }')}"

# The IP address of the node.  If no IP address is given on the kernel
# command-line, the IP address of the current host is used.
node_ip_addr="${CONF_NODE_IP_ADDR:-$(/sbin/ip addr show dev eth0 | awk '/inet / { split($2,a,"/"); print a[1]; }')}"

broker && ip_addr="$broker_ip_addr"
ip_addr=${ip_addr:-$node_ip_addr}

# The nameservers to which named on the broker will forward requests.
# This should be a list of IP addresses with a semicolon after each.
nameservers="$(awk '/nameserver/ { printf "%s; ", $2 }' /etc/resolv.conf)"

########################################################################

if [[ ! x$CONF_NO_NTP =~ x(1|true) ]]
then
  synchronize_clock
fi

if [[ ! x$CONF_NO_SSH_KEYS =~ x(1|true) ]]
then
  install_ssh_keys
fi

configure_yum_repos

yum update -y

install_common_pkgs

broker && install_broker_pkgs
node && install_node_pkgs
node && install_cartridges

broker && configure_selinux_policy_on_broker

node && configure_selinux_policy_on_node

fix_selinux_contexts

node && configure_sysctl_on_node

passthrough_git_ssh_env

node && increase_ssh_limits_on_node

node && add_rhcsh_symlink_on_node

broker && configure_mongodb

node && configure_firewall_on_node
broker && configure_firewall_on_broker

node && enable_services_on_node
broker && enable_services_on_broker

configure_mcollective_on_broker

broker && configure_qpid

broker && configure_named_on_broker

broker && update_resolv_conf_on_broker

node && update_resolv_conf_on_node

broker && configure_swingshift_plugins

configure_network

node && configure_node

node && update_stickshift_facts_on_node

broker && fix_gemfile_lock

# TODO: We should have an irc-bot that posts the IP address of the VM.

%end
