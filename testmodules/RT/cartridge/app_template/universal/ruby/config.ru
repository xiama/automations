require 'rack/lobster'
if RUBY_VERSION.include?("1.8.")
  require 'thread-dump'
elsif RUBY_VERSION.include?("1.9.")
  require './thread-dumper'
end
require 'mysql'

map '/health' do
  health = proc do |env|
    [200, { "Content-Type" => "text/html" }, ["1"]]
  end
  run health
end

map '/lobster' do
  run Rack::Lobster.new
end

map '/' do
  welcome = proc do |env|
    [200, { "Content-Type" => "text/plain" }, ["Usage: #{ENV['OPENSHIFT_APP_DNS']}/<group>\nValid groups are 'shell','env','mysql'"]]
  end
  run welcome
end

map '/env' do
  env = proc do |env|
    result = String.new
    ENV.to_hash.each do |key, value|
      result << "#{key}=#{value}\n"
    end
    [200, { "Content-Type" => "text/plain" }, [result]]
  end
  run env
end
