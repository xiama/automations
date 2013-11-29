require 'rack/lobster'

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
  env_vars = ""
  ENV.to_hash.each do |key, value|
    env_vars += "#{key} "
  end
  welcome = proc do |env|
    [200, { "Content-Type" => "text/html" }, ["#{env_vars}
"]]
  end
  run welcome
end
