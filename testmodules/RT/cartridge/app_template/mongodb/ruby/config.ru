require 'rubygems'
require 'bundler'
require 'mongo'

Bundler.require


get '/' do
    "Welcome to OpenShift\n"
end

get '/mongo' do
    action = request.params().fetch("action", "")
    size = request.params().fetch("size", "500000")
    conn = Mongo::Connection.new(ENV['OPENSHIFT_MONGODB_DB_HOST'], ENV['OPENSHIFT_MONGODB_DB_PORT'])
    db = conn.db(ENV['OPENSHIFT_APP_NAME'])
    auth = db.authenticate(ENV['OPENSHIFT_MONGODB_DB_USERNAME'], ENV['OPENSHIFT_MONGODB_DB_PASSWORD'])
    if auth == false
        response_body = [200, "Mongo authentication failed"]
        conn.close
        return response_body
    end
    coll = db.collection("info")
    if action == "insert"
        for i in 1..size.to_i()
            doc = {"data" => "This is testing data for testing snapshoting and restoring big data in mongodb database.This is testing data for testing snapshoting and restoring big data in mongodb database."}
            coll.insert(doc)
        end
        response_body = [200, "Gear DNS: #{ENV['OPENSHIFT_GEAR_DNS']}<br />" + size + " records have been inserted into mongodb<br />"]
    elsif action == "delete"
        coll.remove
        response_body = [200, "Gear DNS: #{ENV['OPENSHIFT_GEAR_DNS']}<br />All the records have been deleted from mongodb database<br />"]
    elsif action == "show"
        count = coll.count
        if count == 0
            response_body = [200, "Gear DNS: #{ENV['OPENSHIFT_GEAR_DNS']}<br />There is no record in database<br />"]
        else
            doc = coll.find_one
            response_body = [200, "Gear DNS: #{ENV['OPENSHIFT_GEAR_DNS']}<br />There are " + count.to_s + " records in database<br />Here's one record: #{doc['data']}"]
        end
    else
        response_body = "[rhc-cartridge]snapshot/restore big mysql data to existing app<br />[rhc-cartridge]snapshot/restore big mysql data to new app<br />"
    end
    conn.close
    return response_body
end

run Sinatra::Application
