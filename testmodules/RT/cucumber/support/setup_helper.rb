require 'fileutils'
require 'logger'

#
# Define global variables
#
$domain = "dev.rhcloud.com"
$temp = "/tmp/rhc"

$client_config = "/etc/openshift/express.conf"

#
# Old RHC Client scripts
#
$create_app_script = "/usr/bin/rhc-create-app"
$create_domain_script = "/usr/bin/rhc-create-domain"
$ctl_app_script = "/usr/bin/rhc-ctl-app"
$user_info_script = "/usr/bin/rhc-domain-info"
$snapshot_script = "/usr/bin/rhc-snapshot"

#
# New RHC Client scripts
#
$rhc_app_script = "/usr/bin/rhc-app"
$rhc_domain_script = "/usr/bin/rhc-domain"
$rhc_sshkey_script = "/usr/bin/rhc-sshkey"

# RSA Key constants
$libra_pub_key = File.expand_path("~/.ssh/libra_id_rsa.pub")
$libra_priv_key = File.expand_path("~/.ssh/libra_id_rsa")
$test_priv_key = File.expand_path("../misc/libra_id_rsa", File.expand_path(File.dirname(__FILE__)))
$test_pub_key = File.expand_path("../misc/libra_id_rsa.pub", File.expand_path(File.dirname(__FILE__)))
$test_ssh_key = File.open($test_pub_key).gets.chomp.split(' ')[1]

module SetupHelper
  def self.setup
    # Create the temporary space
    FileUtils.mkdir_p $temp

    # Remove all temporary data
    #FileUtils.rm_rf Dir.glob(File.join($temp, "*"))
    
    # Setup the logger
    $logger = Logger.new(File.join($temp, "cucumber.log"))
    $logger.level = Logger::DEBUG
    $logger.formatter = proc do |severity, datetime, progname, msg|
        "#{$$} #{severity} #{datetime}: #{msg}\n"
    end

    # Setup the default keys if necessary
    FileUtils.cp $test_pub_key, $libra_pub_key if !File.exists?($libra_pub_key)
    FileUtils.cp $test_priv_key, $libra_priv_key if !File.exists?($libra_priv_key)
    FileUtils.chmod 0600, $libra_priv_key
  end
end
World(SetupHelper)