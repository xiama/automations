# contents of 'config.ru'
require 'rubygems'
require 'bundler'

Bundler.require

get '/' do
        "the time where this server lives is #{Time.now}
        <br /><br />check out your <a href=\"/agent\"> user_agent</a>"
end

get '/agent' do
     "you're using #{request.user_agent}"
end

get '/show' do
  response_body = ""

  command1 = "ls -l /tmp/rack_tmp_test 2>&1 && ls -l /var/tmp/rack_var_tmp_test 2>&1"
  response_body = response_body + "Command 1: #{command1}" + "\n"
  output = `#{command1}`
  ret1 = $? >> 8
  response_body = response_body + output + "\n"

  command = "ls -l /tmp 2>&1"
  response_body = response_body + "Command: %s" %(command) + "\n"
  output = `#{command}`
  ret_tmp = $? >> 8
  response_body = response_body + output + "\n"

  if ret1 == 0
      response_body = response_body + "RESULT=0\n"
  else
      response_body = response_body + "RESULT=1\n"
  end

  "#{response_body}"
end

get '/create' do
  response_body = ""

  command1 = "touch /tmp/rack_tmp_test 2>&1"
  response_body = response_body + "Command 1: #{command1}" + "\n"
  output = `#{command1}`
  ret1 = $? >> 8
  response_body = response_body + output + "\n"

  command2 = "touch /var/tmp/rack_var_tmp_test 2>&1"
  response_body = response_body + "Command 2: #{command2}" + "\n"
  output = `#{command2}`
  ret2 = $? >> 8
  response_body = response_body + output + "\n"

  command = "ls -l /tmp 2>&1"
  response_body = response_body + "Command: #{command}" + "\n"
  output = `#{command}`
  ret_tmp = $? >> 8
  response_body = response_body + output + "\n"

  if ret1 == 0 and ret2 == 0
    response_body = response_body + "RESULT=0\n"
  else
    response_body = response_body + "RESULT=1\n"
  end

  "#{response_body}"

end

run Sinatra::Application
