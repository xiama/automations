#!/usr/bin/env ruby
#
# Username must be root
#username = `whoami`
#if username != 'root'
#  puts "This script can only be executed by root"
#  exit 255
#end

module Setup
  RHTEST_HOME = File.expand_path(File.dirname(__FILE__)) + File::SEPARATOR + ".." + File::SEPARATOR
  OS_HASH = { :fedora17 => /fedora.*17/i,
              :fedora16 => /fedora.*16/i,
              :rhel     => /Red Hat Enterprise Linux/i,
              :ubuntu12   => /ubuntu.*12/i,}
  YUM_PACKAGES = "git python-sqlobject expect firefox chromium postgresql postgresql-devel rubygem-rails perl-ExtUtils-MakeMaker perl-Module-Build maven3 gcc gcc-c++ rubygem-sqlite3 rubygem-rack-mount sqlite-devel rubygem-pg mongodb krb5-workstation httpd-tools python-pip python-paramiko python-kerberos python-selenium java-1.7.0-openjdk ruby-devel python-devel perl-devel mysql-devel spawn patch readline readline-devel zlib zlib-devel libyaml-devel libffi-devel openssl-devel make bzip2 autoconf automake libtool bison iconv-devel"
  RUBY_VERSIONS = ["1.8.7", "1.9.3"]

  def setup_env_var
    ENV['RHTEST_HOME'] = Setup::RHTEST_HOME
  end

  def detect_os
    file = File.new('/etc/issue', 'r')
    content = file.read
    file.close
    Setup::OS_HASH.each do |key, value|
      match = value.match(content)
      if Regexp.last_match
        return key
      end
    end
    return nil
  end

  def install_packages(os_type)
    puts "Install packages using yum/apt-get"
    if os_type == :fedora16
      packages = Setup::YUM_PACKAGES
      packages += " rhc"
    elsif os_type == :fedora17
      packages = Setup::YUM_PACKAGES
    end
    if os_type == :fedora16 or os_type == :fedora17
      output = `yum install -y #{packages}`
    end
    if $?.exitstatus != 0
      puts "Failed to install yum packages"
      return false
    else
      return true
    end
  end

  def setup_rvm
  end

  def setup_python_virtualenv
  end
end


include Setup
# Setup environment variables
Setup::setup_env_var
# Detect OS type
os_type = Setup::detect_os
if os_type
  puts "Your OS type is: #{os_type}"
else
  puts "Failed to detect your OS type"
end
