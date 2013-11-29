#!/usr/bin/env ruby
require 'rubygems'
require 'bundler'
require 'mysql'

Bundler.require


get '/' do
    "[rhc-cartridge]snapshot/restore big mysql data to existing app<br />[rhc-cartridge]snapshot/restore big mysql data to new app<br />"
end

get '/mysql' do
    dbh = Mysql.real_connect("#host","#user","#passwd","#dbname",port=#port)
    dbh.query("CREATE TABLE IF NOT EXISTS info(id INT NOT NULL AUTO_INCREMENT, data CHAR(200), PRIMARY KEY (id));")
    dbh.query("COMMIT;")
    action = request.params().fetch("action", "")
    size = request.params().fetch("size", "5000")
    if action == "insert"
        dbh.query("SET autocommit=0;")
        for i in 1..size.to_i()
            dbh.query("INSERT INTO info VALUES(NULL, 'This is testing data for testing snapshoting and restoring big data in mysql database.This is testing data for testing snapshoting and restoring big data in mysql database.');")
        end
        dbh.query("COMMIT;")
        dbh.query("SET autocommit=1;")
        response_body = [200, "Gear DNS: #{ENV['OPENSHIFT_GEAR_DNS']}<br />" + size + " records have been inserted into mysql<br />"]
    elsif action == "delete"
        dbh.query("DELETE FROM info;")
        response_body = [200, "Gear DNS: #{ENV['OPENSHIFT_GEAR_DNS']}<br />All the records have been deleted from mysql database<br />"]
    elsif action == "show"
        res = dbh.query("SELECT COUNT(*) FROM info;")
        count = res.fetch_row()[0]
        if count.to_i() == 0
            response_body = [200, "Gear DNS: #{ENV['OPENSHIFT_GEAR_DNS']}<br />There is no record in database<br />"]
        else
            response_body = [200, "Gear DNS: #{ENV['OPENSHIFT_GEAR_DNS']}<br />There are " + count + " records in database<br />"]
        end
        if count.to_i() != 0
            res = dbh.query("SELECT * FROM info LIMIT 0, 1;")
            row = res.fetch_row()
            response_body[1] += "Here is one row: " + row[1]
        end
    else
        response_body = "[rhc-cartridge]snapshot/restore big mysql data to existing app<br />[rhc-cartridge]snapshot/restore big mysql data to new app<br />"
    end
    dbh.query("COMMIT;")
    dbh.close()
    return response_body
end


run Sinatra::Application
