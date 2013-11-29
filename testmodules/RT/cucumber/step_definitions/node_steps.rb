# 
# 
# Steps that can be used to check applications installed on a server (node)
#
#require 'etc'

require 'openshift'
require 'resolv'
include OpenShift

# Controller cartridge command paths
$cartridge_root = '/usr/libexec/li/cartridges'
$controller_config_path = "cdk-app-create"
$controller_config_format = "#{$controller_config_path} -c '%s'"
$controller_deconfig_path = "cdk-app-destroy"
$controller_deconfig_format = "#{$controller_deconfig_path} -c '%s'"
$home_root = "/var/lib/libra"
# --------------------------------------------------------------------------
# Account Checks
# --------------------------------------------------------------------------
# These must run after server_steps.rb: I create a <name> app for <framework>

# These depend on test data of this form:
#    And the following test data
#      | accountname 
#      | 00112233445566778899aabbccdde000


# Convert a unix UID to a hex string suitable for use as a tc(1m) class value
def netclass uid
  "%04x" % uid
end

# copied from server-common/openshift/user.rb 20110630
def gen_small_uuid()
    # Put config option for rhlogin here so we can ignore uuid for dev environments
    %x[/usr/bin/uuidgen].gsub('-', '').strip
end

Given /^a new guest account$/ do
  # generate a random account name and use the stock SSH keys
  # generate a random UUID and use the stock keys
  acctname = gen_small_uuid
  @account = {
    'accountname' => acctname,
  }
  command = $controller_config_format % [acctname]
  puts "******", command
  run command
  puts "&&&&&&", command
  # get and store the account UID's by name
  @account['uid'] = Etc.getpwnam(acctname).uid
end

Given /^the guest account has no application installed$/ do
  # Assume this is true
end

When /^I create a guest account$/ do
  # call /usr/libexec/li/cartridges  @table.hashes.each do |row|
  # generate a random account name and use the stock SSH keys
  # generate a random UUID and use the stock keys
  acctname = gen_small_uuid
  @account = {
      'accountname' => acctname,
    }
  command = $controller_config_format % [acctname]
  run command
  # get and store the account UID's by name
  @account['uid'] = Etc.getpwnam(acctname).uid
end

When /^I delete the guest account$/ do
  # call /usr/libexec/li/cartridges  @table.hashes.each do |row|
  
  command = $controller_deconfig_format % [@account['accountname']]
  run command
end

When /^I create a new namespace$/ do
  ec = run("#{$rhc_domain_script} create -n vuvuzuzufukuns -l vuvuzuzufuku -p fakepw -d")
end

When /^I delete the namespace$/ do
  ec = run("#{$rhc_domain_script} destroy -n vuvuzuzufukuns -l vuvuzuzufuku -p fakepw -d")
  # FIXME: Need to fix this test to work w/ mongo -- need unique name per run.
  #ec.should be == 0
end

Then /^a namespace should get deleted$/ do
  ec = run("host vuvuzuzufukuns.dev.rhcloud.com | grep \"not found\"")
  #ec.should be == 0
end

Then /^an account password entry should( not)? exist$/ do |negate|
  # use @app['uuid'] for account name
  
  begin
    @pwent = Etc.getpwnam @account['accountname']
  rescue
    nil
  end

  if negate
    @pwent.should be_nil      
  else
    @pwent.should_not be_nil
  end
end

Then /^an account PAM limits file should( not)? exist$/ do |negate|
  limits_dir = '/etc/security/limits.d'
  @pamfile = File.exists? "#{limits_dir}/84-#{@account['accountname']}.conf"

  if negate
    @pamfile.should_not be_true
  else
    @pamfile.should be_true
  end
end

Then /^an HTTP proxy config file should( not)? exist$/ do |negate|

end

Then /^an account cgroup directory should( not)? exist$/ do |negate|
  cgroups_dir = '/cgroup/all/libra'
  @cgdir = File.directory? "#{cgroups_dir}/#{@account['accountname']}"

  if negate
    @cgdir.should_not be_true
  else
    @cgdir.should be_true
  end
end

Then /^an account home directory should( not)? exist$/ do |negate|
  @homedir = File.directory? "#{$home_root}/#{@account['accountname']}"
    
  if negate
    @homedir.should_not be_true
  else
    @homedir.should be_true
  end
end

Then /^selinux labels on the account home directory should be correct$/ do
  homedir = "#{$home_root}/#{@account['accountname']}"
  @result = `restorecon -v -n #{homedir}`
  @result.should be == "" 
end

Then /^disk quotas on the account home directory should be correct$/ do

  # EXAMPLE

  # no such user
  # quota: user 00112233445566778899aabbccdde001 does not exist.

  # no quotas on user
  # Disk quotas for user root (uid 0): none

  # Disk quotas for user 00112233445566778899aabbccdde000 (uid 501): 
  #    Filesystem  blocks   quota   limit   grace   files   quota   limit   grace
  #     /dev/xvde      24       0  131072               7       0   10000        


  @result = `quota -u #{@account['accountname']}`
    
  @result.should_not match /does not exist./
  @result.should_not match /: none\s*\n?/
  @result.should match /Filesystem  blocks   quota   limit   grace   files   quota   limit   grace/
end


Then /^a traffic control entry should( not)? exist$/ do |negate|
  acctname = @account['accountname']
  tc_format = 'tc -s class show dev eth0 classid 1:%s'
  tc_command = tc_format % (netclass @account['uid'])
  @result = `#{tc_command}`
  if negate
    @result.should be == ""
  else
    @result.should_not be == ""
  end
end

# ===========================================================================
# Generic App Checks
# ===========================================================================

# ===========================================================================
# PHP App Checks
# ===========================================================================

# ===========================================================================
# WSGI App Checks
# ===========================================================================

# ===========================================================================
# Rack App Checks
# ===========================================================================
