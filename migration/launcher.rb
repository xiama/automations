#! /usr/bin/env ruby
require 'rubygems'
require 'getopt/long'
require 'net/ssh'
require 'yaml'
require 'active_support/ordered_hash'


def create_domain(rhlogin, password, domain, server)
  cmd = "rhc domain-create #{domain} -k -l #{rhlogin} -p #{password} --server #{server}"
  puts "Creating domain #{domain} as #{rhlogin} with command \'#{cmd}\'\n"
  puts `#{cmd}`
  cmd = "rhc sshkey-add default ~/.ssh/id_rsa.pub -k -l #{rhlogin} -p #{password} --server #{server}"
  puts "Adding sshkey key with command \'#{cmd}\'\n"
  puts `#{cmd}`
end


def add_capacities(rhlogin, capacities, server)
  puts "Adding capacities for #{rhlogin}\n"
  Net::SSH.start(server, "root", :keys => ["~/.ssh/libra.pem"]) do |ssh|
    puts ssh.exec!("oo-admin-ctl-user -l #{rhlogin} #{capacities}")
  end
end

def change_plan(rhlogin, password, server, plan)
  cmd = %Q|curl -s -k -H "Content-Type: Application/json" -u #{rhlogin}:#{password} https://#{server}/broker/rest/user -X PUT -d '{"plan_id":"#{plan}"}'|
  begin
    puts "Updating plan to #{plan}\n"
    puts cmd
    puts `#{cmd}`
  rescue Exception => e
    puts e.message
  end
  return 0
end

def create_c9_subaccount(rhlogin, password, server, sub_account, sub_domain)
  cmd = %Q|curl -k -s -X POST -H "Accept: Application/xml" -H "X-Impersonate-User: #{sub_account}" -d name=#{sub_domain} --user #{rhlogin}:#{password} https://#{server}/broker/rest/domains|
  puts "Creating c9 subaccount and subdomain\n"
  puts cmd
  puts `#{cmd}`
end

def create_c9_app(rhlogin, password, server, sub_account, sub_domain, conf)
  apps = YAML.load(File.read(conf))
  apps.each do |key, value|
    appname = key
    first_cartridges = value["Cartridge"]
    cartridge = first_cartridges[0]
    cmd = %Q|curl -k -s -X POST -H 'Accept: application/xml' -H "X-Impersonate-User: #{sub_account}" -d name=#{appname} -d cartridge=#{cartridge} -d gear_profile=c9 --user #{rhlogin}:#{password} https://#{server}/broker/rest/domains/#{sub_domain}/applications |
    puts "Creating c9 app #{appname}\n"
    puts cmd
    puts `#{cmd}`
  end
end

def fork_instance(fork_ami)

	Net::SSH.start("#{fork_ami}", "root", :keys => ["~/.ssh/libra.pem"]) do |ssh|

		puts "Copying local packages"
		ssh.exec!("scp -i ~/libra.pem #{$sshopt} -r /root/devenv-local root@#{$server}:~/")

		puts "Copying local.repo"
		ssh.exec!("scp -i ~/libra.pem #{$sshopt} /etc/yum.repos.d/local.repo root@#{$server}:/etc/yum.repos.d/")

	end

end


def stage_instance(stage)

	Net::SSH.start("#{stage}", "root", :keys => ["~/.ssh/libra.pem"]) do |ssh|

		ssh.exec!("sed -i 's/stage/candidate/g' /etc/yum.repos.d/devenv.repo")
		ssh.exec!("sed -i 's/enabled=0/enabled=1/g' /etc/yum.repos.d/local.repo")
		ssh.exec!("git clone git@github.com:openshift/li.git")
		ssh.exec!("yum -y install yum-priorities")
		ssh.exec!("yum -y install yum-downloadonly")
		ssh.exec!("yum -y clean all")

		puts "Downloading upgrade packages"
		ssh.exec!("yum -y update --downloadonly | tee -a download.log")

	end
end



def create_migration_data(rhlogin, password, server, conf) # conf refers to the yaml config file
  apps = YAML.load(File.read(conf))
  opt = " -k --no-git --no-dns -l #{rhlogin} -p #{password} --server #{server}"
  cart_opt = "-k -l #{rhlogin} -p #{password} --server #{server}"

  apps.each do |key, value|
    appname = key
    first_cartridges = value["Cartridge"]
    web_cartridge = first_cartridges[0]
    added_cartridge = value["embed"]
    scale = (value["scale"]? " -s" : nil)
    app_alias = value["alias"]
    from_code = (value["from-code"]? " --from-code #{value["from-code"]}" : nil)
    min, max = value["min"], value["max"] if scale
    action = value["action"] if value["action"]
    gearsize = value["size"] if value["size"]
    ssl = value["ssl"] if value["ssl"]
    storage = value["storage"] if value["storage"]


    if gearsize
      cmd = "rhc app-create #{appname} -g #{gearsize}"
    else
      cmd = "rhc app-create #{appname}"
    end

    first_cartridges.each do |cart|
       cmd += " #{cart}"
    end

    cmd = cmd + scale.to_s + from_code.to_s + opt.to_s
    puts cmd
    puts `#{cmd}`

    if added_cartridge
      added_cartridge.each do |cart|
        cmd = "rhc cartridge-add #{cart} -a #{appname} #{cart_opt}"
        #puts cmd
        puts `#{cmd}`

        if storage
          cmd = "rhc cartridge-storage --set #{storage} #{cart} -a #{appname} #{cart_opt}"
          #puts cmd
          puts `#{cmd}`
        end
      end
    end



    if app_alias
      app_alias.each do |al|
        cmd = "rhc alias-add #{appname} #{al} #{cart_opt}"
        #puts cmd
        puts `#{cmd}`
        if ssl
          cmd = "rhc alias update-cert #{appname} #{al} --certificate ~/workspace/OpenShift-Migration/migration/server.crt --private-key ~/workspace/OpenShift-Migration/migration/server.key --passphrase aaaa #{cart_opt}"
          #puts cmd
          puts `#{cmd}`
        end
      end
    end


    if min and max
      cmd = "rhc cartridge-scale #{web_cartridge} -a #{appname} --min #{min} --max #{max} #{cart_opt}"
      #puts cmd
      puts `#{cmd}`
    end


    if action
      cmd = "rhc app-#{action} #{appname} #{cart_opt}"
      #puts cmd
      puts `#{cmd}`
    end

    puts
  end
end

def upgrade_instance(server)
  puts "Start upgrading server\n"
  Net::SSH.start(server, "root", :keys => ["~/.ssh/libra.pem"]) do |ssh|

    # Generate pending ops
    # Delete this and delete the config script in jenkins job after this test has passed
    ssh.exec!("ruby /root/pending_ops_creator.rb")

    # set iptable rules before upgrade
    # for sprint 34 changes
    # delete this code block when this has been pushed to prod
    # begin of iptable code block
    sysctl_conf = ["echo net.ipv4.ip_forward = 1 >> /etc/sysctl.conf", "echo net.ipv4.conf.all.route_localnet = 1 >> /etc/sysctl.conf", "sysctl -w net.ipv4.ip_forward=1", "sysctl -w net.ipv4.conf.all.route_localnet=1"]
    sysctl_conf.each { |c| puts ssh.exec!("#{c}") }

    iptable_rules = ["-N rhc-app-comm", "-A INPUT -j rhc-app-comm", "-A OUTPUT -j rhc-app-comm"]
    iptable_rules.each { |r| puts ssh.exec!("/sbin/iptables #{r}") }
    puts ssh.exec!("/etc/init.d/iptables save")
    puts ssh.exec!("/etc/init.d/iptables restart")
    # end of iptable code block

    # Add/Remove mongodb indexes
    # Delete after this feature is pushed to prod
    mongo_idx_cmds = [%q/echo "db.applications.dropIndex({ 'created_at' : 1 })" | mongo openshift_broker_dev/, %q/echo "db.cloud_users.dropIndex({ 'created_at' : 1 })" | mongo openshift_broker_dev/, %q/echo "db.cloud_users.ensureIndex({ 'pending_ops.created_at' : 1 })" | mongo openshift_broker_dev/, %q/echo "db.applications.ensureIndex({ 'pending_op_groups.created_at' : 1 })" | mongo openshift_broker_dev/]
    mongo_idx_cmds.each { |c| puts ssh.exec!("#{c}") }
    # end



    output = ssh.exec!("yum -y update --nogpgcheck && echo true || echo false")
    puts output
    if output.split("\n")[-1].chomp.to_s == "true"
      $upgrade_success = true 
    else 
      $upgrade_success = false
    end
    puts "upgrade_success = #{$upgrade_success}"
  end
end

def migrate(server, version)
  puts "Start migration"
  Net::SSH.start(server, "root", :keys => ["~/.ssh/libra.pem"]) do |ssh|
    ssh.exec!("git clone git@github.com:openshift/li.git")
    puts ssh.exec!("/etc/init.d/rhc-datastore restart")
    puts ssh.exec!("/root/li/misc/maintenance/bin/migrate_port_proxy web_only")
    puts ssh.exec!("/root/li/misc/maintenance/bin/migrate_port_proxy db_only")
    puts ssh.exec!("yum remove -y openshift-origin-port-proxy")
    puts ssh.exec!("oo-admin-broker-cache -c")
    puts ssh.exec!("/etc/init.d/rhc-broker restart")
    puts ssh.exec!("/etc/init.d/ruby193-mcollective restart")

    puts "Start pre-release migration..."
    puts ssh.exec!("/usr/bin/rhc-admin-migrate-datastore --prerelease --version #{version}")
    puts "Start compatible migrating datastore..."
    puts ssh.exec!("/usr/bin/rhc-admin-migrate-datastore --compatible --version #{version}")
    puts "Start non-compatible migrating datastore..."
    puts ssh.exec!("/usr/bin/rhc-admin-migrate-datastore --non-compatible --version #{version}")
    puts "Start pos-release migration..."
    puts ssh.exec!("/usr/bin/rhc-admin-migrate-datastore --postrelease --version #{version}")

    puts ssh.exec!("oo-admin-broker-cache -c")
    puts "Migrating node...\n"
    puts ssh.exec!("/usr/sbin/oo-admin-upgrade upgrade-node --version #{version} --ignore-cartridge-version")
    puts "Migration Done, check /root/migrate.log for details\n"
  end
end

def get_base_dns(server)
  base_dns = ""
  case server
  when "int.openshift.redhat.com"
    base_dns = "int.rhcloud.com"
  when "stg.openshift.redhat.com"
    base_dns = "stg.rhcloud.com"
  when "openshift.redhat.com"
    base_dns = "rhcloud.com"
  else
    base_dns = "dev.rhcloud.com"
  end
  return base_dns
end

def access_migrated_app(appname, domain, base_dns)
  # Get base dns 
  app_url = "http://#{appname}-#{domain}.#{base_dns}"
  app_ssl_url = "https://#{appname}-#{domain}.#{base_dns}"

  status_code = 0
  retry_cnt = 0
	ENV['http_proxy']="http://file.rdu.redhat.com:3128"
	ENV['https_proxy']="https://file.rdu.redhat.com:3128"

  begin
    status_code = `curl -s -I #{app_url} | sed -n 1p | cut -d ' ' -f 2`.chomp.to_i
    raise if status_code != 200 and retry_cnt < 3
  rescue
    retry_cnt += 1
    retry
  end

  printf("%10s\t%50s\t%11s\t%1s\n", appname, app_url, status_code.to_s, retry_cnt.to_s)

end

def operate_app(appname, rhlogin, password, server)
  ops = ["stop", "start", "restart", "reload", "force-stop", "start", "show --status"]
  op_status = "ok"
  ops.each do |op|
    cmd = "rhc app-#{op} #{appname} -k -l #{rhlogin} -p #{password} --server #{server}"
    result = `#{cmd}`
    unless $?.success?
      op_status = "error"
      puts "#{op} operation failed against #{appname}"
			puts result.chomp.to_s
      break
    end
  end

  puts "All operations against #{appname} are successful" if op_status == "ok"
end

def p_usage
  puts <<EOF

Usage: launcher.rb launch automation upgrade and migration against target instance

  -s, --server       target broker host, this argument is required
  -c, --config       read accounts details from the configration file, this argument is required
  -a, --upgrade-account  upgrade test account before start creating applications
  -u, --upgrade      upgrade instance after apps are created
  -f, --to-fork      upgrade to a fork ami version
  -p, --prepare-data     Create applications
  -m, --migrate      execute migration after upgrade, when this option is specified, the migration version must be provided
  -t, --test         Launches test suite against your migration data, you can also use this option to perform only test
  -h, --help         show the usage info

EOF
end

opt = Getopt::Long.getopts(
  ["-s", "--server", Getopt::REQUIRED],
  ["-c", "--config", Getopt::REQUIRED],
  ["-a", "--upgrade-account", Getopt::BOOLEAN],
  ["-u", "--upgrade", Getopt::BOOLEAN],
  ["-f", "--to-fork", Getopt::REQUIRED],
  ["-m", "--migrate", Getopt::REQUIRED],
  ["-p", "--prepare-data", Getopt::BOOLEAN],
  ["-t", "--test", Getopt::BOOLEAN],
  ["-h", "--help", Getopt::BOOLEAN]
)


if opt["h"]
  p_usage
  exit 0
end

unless opt["s"] and opt["c"]
  p_usage
  exit 1
end


$server = opt["s"]
$config_file = opt["c"]
$rhlogins = YAML.load(File.read($config_file))
$fork_ami = opt["f"] if opt["f"]
$upgrade_success = true



$rhlogins.each do |key, value|
  rhlogin = key
  password = value["password"]
  domain = value["domain"]
  capacities = value["capacities"] if value["capacities"]
  supported_env = value["env"]
  supported = false
  data_file = File.expand_path(value["data"])
  plan = value["plan"]
  c9, sub_account, sub_domain = value["c9"], value["sub_account"], value["sub_domain"] if value["c9"]

  supported_env.each do |env|
    if $server.include?(env)
      supported = true
      break
    end
  end

  if supported and opt["p"]
    create_domain(rhlogin, password, domain, $server)
    add_capacities(rhlogin, capacities, $server) if opt["a"] and capacities
    change_plan(rhlogin, password, $server, plan) if plan
    if c9
      create_c9_subaccount(rhlogin, password, $server, sub_account, sub_domain)
      puts "\nStart creating c9 applications as #{rhlogin}"
      create_c9_app(rhlogin, password, $server, sub_account, sub_domain, data_file)
    else
      puts "\nStart creating applications as #{rhlogin}\n"
      create_migration_data(rhlogin, password, $server, data_file) 
    end
  end

end

# Prepare for fork ami upgrade
if $fork_ami
  puts "\nUpgrading server to fork_ami/target_devenv\n"
  $sshopt = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
  `scp -i ~/.ssh/libra.pem #{$sshopt} ~/.ssh/libra.pem root@#{$server}:~/`
  `scp -i ~/.ssh/libra.pem #{$sshopt} ~/.ssh/libra.pem root@#{$fork_ami}:~/`
  fork_instance($fork_ami)
  stage_instance($server)
end


# Upgrade instance to latest
if opt["u"]
  upgrade_instance($server)
end

if opt["m"] and $upgrade_success == true
  migrate($server, opt["m"]) 
else
  puts "\nWill not perform migration because upgrade caught an error\n"
end


if opt["t"] 
  puts "Testing app status\n"
  puts "Please make sure your http_proxy env var is set properly\n"
  printf("%10s\t%50s\t%11s\t%1s\n", "app", "url", "status_code", "retry_times")
  $rhlogins.each do |key, value|
    rhlogin = key
    domain = value["domain"]
    data_file = File.expand_path(value["data"])
    c9, sub_account, sub_domain = value["c9"], value["sub_account"], value["sub_domain"] if value["c9"]
    apps = YAML.load(File.read(data_file))
    supported = false
    value["env"].each do |env|
      if $server.include?(env)
        supported = true
        break
      end
    end

    if supported
      base_dns = get_base_dns($server)
      domain = sub_domain if c9
      apps.each do |k, v|
        app = k
        access_migrated_app(app, domain, base_dns)
      end
    end
  end

  
  puts "Testing app oprations\n"
  $rhlogins.each do |key, value|
    rhlogin = key
    password = value["password"]
    data_file = File.expand_path(value["data"])
    apps = YAML.load(File.read(data_file))
    supported = false
    value["env"].each do |env|
      if $server.include?(env)
        supported = true
        break
      end
    end
    
    if supported
      apps.each do |k, v|
        app = k
        next if app.include?("c9")
        operate_app(app, rhlogin, password, $server)
      end
    end

  end
end
