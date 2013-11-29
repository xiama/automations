# contents of 'config.ru'
require 'rubygems'
require 'bundler'
require 'pg'

Bundler.require

#conn_str = "dbname=#pgsql_dbname# user=#pgsql_user# password=#pgsql_passwd# host=#pgsql_host# port=#pgsql_port#"

conn_str = "dbname=#{ENV['OPENSHIFT_APP_NAME']} user=#{ENV['OPENSHIFT_POSTGRESQL_DB_USERNAME']} password=#{ENV['OPENSHIFT_POSTGRESQL_DB_PASSWORD']} host=#{ENV['OPENSHIFT_POSTGRESQL_DB_HOST']} port=#{ENV['OPENSHIFT_POSTGRESQL_DB_PORT']}"

get '/' do
        "the time where this server lives is #{Time.now}
        <br /><br />check out your <a href=\"/agent\"> user_agent</a>"
end

get '/show.rb' do

  begin
    conn = PGconn.open(conn_str)
    res = conn.exec("SELECT data from info;")
    response_body = res.getvalue(0,0)
    conn.finish()
  end

  "#{response_body}"
end

get '/data1.rb' do

  begin
    conn = PGconn.open(conn_str)
    res = conn.exec("DROP TABLE IF EXISTS info;")
    res = conn.exec("CREATE TABLE info(id integer PRIMARY KEY, data text);")
    res = conn.exec("INSERT INTO info VALUES(1, '#str_random1#');")
    response_body = "Please visit /show.rb to see the data"
    conn.finish()
  end

  "#{response_body}"
end

get '/data2.rb' do

  begin
    conn = PGconn.open(conn_str)
    res = conn.exec("DROP TABLE IF EXISTS info;")
    res = conn.exec("CREATE TABLE info(id integer PRIMARY KEY, data text);")
    res = conn.exec("INSERT INTO info VALUES(1, '#str_random2#');")
    response_body = "Please visit /show.rb to see the data"
    conn.finish()
  end 

  "#{response_body}"
end

run Sinatra::Application
