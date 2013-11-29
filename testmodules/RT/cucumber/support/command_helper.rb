require 'timeout'
require 'fileutils'
require 'open3'

module CommandHelper
  def run_stdout(cmd)

    exit_code = -1
    output = nil

    # Don't let a command run more than 5 minutes
    Timeout::timeout(500) do
      output = `#{cmd} 2>&1`
      exit_code = $?.exitstatus
    end

    exit_code.should == 0
    return output
  end

  def run(cmd, outbuf=[], retries=0)

    exit_code = -1
    output = nil 
    # Don't let a command run more than 5 minutes
    Timeout::timeout(500) do
      output = `#{cmd} 2>&1`
      exit_code = $?.exitstatus
    end


    if exit_code != 0
      if retries < 3 && exit_code == 140 && cmd.start_with?("/usr/bin/rhc-") # No nodes available...  ugh
        sleep 5
        return run(cmd, outbuf, retries+1)
      end
    end

    # append the buffers if an array container is provided
    if outbuf
      outbuf << output
    end

    return exit_code
  end

  # run a command in an alternate SELinux context
  def runcon(cmd, user=nil, role=nil, type=nil, outbuf=nil)
    prefix = 'runcon'
    prefix += (' -u ' + user) if user
    prefix += (' -r ' + role) if role
    prefix += (' -t ' + type) if type
    fullcmd = prefix + " " + cmd

    output = `#{fullcmd} 2>&1`
    exit_code = $?.exitstatus

    # append the buffers if an array container is provided
    if outbuf
      outbuf << output
    end


    return exit_code
  end

  def rhc_create_domain(app)
    rhc_do('rhc_create_domain') do
      exit_code = run("#{$rhc_domain_script} create -n #{app.namespace} -l #{app.login} -p fakepw -d")
      app.create_domain_code = exit_code
      return exit_code == 0
    end
  end

  def rhc_update_namespace(app)
    rhc_do('rhc_update_namespace') do
      old_namespace = app.namespace
      if old_namespace.end_with?('new')
        app.namespace = new_namespace = old_namespace[0..-4]
      else
        app.namespace = new_namespace = old_namespace + "new"
      end
      old_hostname = app.hostname
      app.hostname = "#{app.name}-#{new_namespace}.#{$domain}"
      old_repo = app.repo
      app.repo = "#{$temp}/#{new_namespace}_#{app.name}_repo"
      FileUtils.mv old_repo, app.repo
      `sed -i "s,#{old_hostname},#{new_namespace},g" #{app.repo}/.git/config`
      if run("grep '#{app.name}-#{old_namespace}.dev.rhcloud.com' /etc/hosts") == 0
        run("sed -i 's,#{app.name}-#{old_namespace}.dev.rhcloud.com,#{app.name}-#{new_namespace}.dev.rhcloud.com,g' /etc/hosts")
      end
      old_file = app.file
      app.file = "#{$temp}/#{new_namespace}.json"
      FileUtils.mv old_file, app.file
      run("#{$rhc_domain_script} alter -n #{new_namespace} -l #{app.login} -p fakepw -d").should == 0
      app.persist
    end
  end

  def rhc_snapshot(app)
    rhc_do('rhc_snapshot') do
      app.snapshot="/tmp/#{app.name}-#{app.namespace}.tar.gz"
      FileUtils.rm_rf app.snapshot
      run("#{$rhc_app_script} snapshot save -l #{app.login} -a #{app.name} -f '#{app.snapshot}' -p fakepw -d").should == 0
      app.persist
    end
  end
  
  def rhc_restore(app)
    rhc_do('rhc_restore') do
      run("#{$rhc_app_script} snapshot restore -l #{app.login} -a #{app.name} -f '#{app.snapshot}' -p fakepw -d").should == 0
    end
  end
  
  def rhc_tidy(app)
    rhc_do('rhc_tidy') do
      run("#{$rhc_app_script} tidy -l #{app.login} -a #{app.name} -p fakepw -d").should == 0
    end
  end

  def rhc_create_app(app, use_hosts=true)
    rhc_do('rhc_create_app') do
      cmd = "#{$rhc_app_script} create -l #{app.login} -a #{app.name} -r #{app.repo} -t #{app.type} -p fakepw -d"

      # Short circuit DNS to speed up the tests by adding a host entry and skipping the DNS validation
      if use_hosts
        run("echo '127.0.0.1 #{app.name}-#{app.namespace}.dev.rhcloud.com  # Added by cucumber' >> /etc/hosts")
        cmd << " --no-dns"
      end

      output_buffer = []
      exit_code = run(cmd, output_buffer)

      # Update the application uid from the command output
      app.update_uid(output_buffer[0])
      
      # Update the application creation code
      app.create_app_code = exit_code

      return app
    end
  end

  def rhc_embed_add(app, type)
    rhc_do('rhc_embed_add') do
      result = run_stdout("#{$rhc_app_script} cartridge add -l #{app.login} -a #{app.name} -p fakepw -c #{type} -d")
      if type.start_with?('mysql-')
        app.mysql_hostname = /^Connection URL: mysql:\/\/(.*)\/$/.match(result)[1]
        app.mysql_user = /^ +Root User: (.*)$/.match(result)[1]
        app.mysql_password = /^ +Root Password: (.*)$/.match(result)[1]
        app.mysql_database = /^ +Database Name: (.*)$/.match(result)[1]

        app.mysql_hostname.should_not be_nil
        app.mysql_user.should_not be_nil
        app.mysql_password.should_not be_nil
        app.mysql_database.should_not be_nil
      end

      app.embed = type
      app.persist
      return app
    end
  end

  def rhc_embed_remove(app)
    rhc_do('rhc_embed_remove') do
      puts app.name
      run("#{$rhc_app_script} cartridge remove -l #{app.login} -a #{app.name} -p fakepw -c #{app.embed} -d").should == 0
      app.mysql_hostname = nil
      app.mysql_user = nil
      app.mysql_password = nil
      app.mysql_database = nil
      app.embed = nil
      app.persist
      return app
    end
  end

  def rhc_ctl_stop(app)
    rhc_do('rhc_ctl_stop') do
      run("#{$rhc_app_script} stop -l #{app.login} -a #{app.name} -p fakepw -d").should == 0
      run("#{$rhc_app_script} status -l #{app.login} -a #{app.name} -p fakepw  | grep '#{app.get_stop_string}'").should == 0
    end
  end

  def rhc_add_alias(app)
    rhc_do('rhc_add_alias') do
      run("#{$rhc_app_script} add-alias -l #{app.login} -a #{app.name} -p fakepw --alias '#{app.name}-#{app.namespace}.example.com' -d").should == 0
    end
  end

  def rhc_remove_alias(app)
    rhc_do('rhc_remove_alias') do
      run("#{$rhc_app_script} remove-alias -l #{app.login} -a #{app.name} -p fakepw --alias '#{app.name}-#{app.namespace}.example.com' -d").should == 0
    end
  end

  def rhc_ctl_start(app)
    rhc_do('rhc_ctl_start') do
      run("#{$rhc_app_script} start -l #{app.login} -a #{app.name} -p fakepw -d").should == 0
      run("#{$rhc_app_script} status -l #{app.login} -a #{app.name} -p fakepw | grep '#{app.get_stop_string}'").should == 1
    end
  end

  def rhc_ctl_restart(app)
    rhc_do('rhc_ctl_restart') do
      run("#{$rhc_app_script} restart -l #{app.login} -a #{app.name} -p fakepw -d").should == 0
      run("#{$rhc_app_script} status -l #{app.login} -a #{app.name} -p fakepw | grep '#{app.get_stop_string}'").should == 1
    end
  end

  def rhc_ctl_destroy(app, use_hosts=true)
    rhc_do('rhc_ctl_destroy') do
      run("#{$rhc_app_script} destroy -l #{app.login} -a #{app.name} -p fakepw -b -d").should == 0
      run("#{$rhc_app_script} status -l #{app.login} -a #{app.name} -p fakepw | grep 'does not exist'").should == 0
      run("sed -i '/#{app.name}-#{app.namespace}.dev.rhcloud.com/d' /etc/hosts") if use_hosts
      FileUtils.rm_rf app.repo
      FileUtils.rm_rf app.file
    end
  end

  def rhc_do(method, retries=2)
    i = 0
    while true
      begin
        yield
        break
      rescue Exception => e
        raise if i >= retries
        i += 1
      end
    end
  end

  #
  # useful methods to avoid duplicating effort
  #

  #
  # Count the number of processes owned by account with cmd_name
  #
  def num_procs acct_name, cmd_name

    ps_pattern = /^\s*(\d+)\s+(\S+)$/
    command = "ps --no-headers -o pid,comm -u #{acct_name}"

    stdin, stdout, stderr = Open3.popen3(command)

    stdin.close

    outstrings = stdout.readlines
    errstrings = stderr.readlines

    proclist = outstrings.collect { |line|
      match = line.match(ps_pattern)
      match and (match[1] if match[2] == cmd_name)
    }.compact

    found = proclist ? proclist.size : 0
    found
  end

  #
  # Count the number of processes owned by account that match the regex
  #
  def num_procs_like acct_name, regex
    command = "ps --no-headers -f -u #{acct_name}"

    stdin, stdout, stderr = Open3.popen3(command)

    stdin.close

    outstrings = stdout.readlines
    errstrings = stderr.readlines

    proclist = outstrings.collect { |line|
      line.match(regex)
    }.compact!

    found = proclist ? proclist.size : 0
    found
  end
end

World(CommandHelper)
