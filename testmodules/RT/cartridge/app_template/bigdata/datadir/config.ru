require 'rubygems'
require 'bundler'

Bundler.require

get '/' do
    "[rhc-cartridge]snapshot/restore big data to new app"
end

get '/create' do
    begin
        size = request.params().fetch("size", "300")
        cmd = "dd if=/dev/urandom of=#{ENV['OPENSHIFT_DATA_DIR']}bigfile bs=1M count=#{size}"
        ret = system(cmd)
        if ret == true
            msg = "The bigfile has been created."
        else
            msg = "Failed to create bigfile under OPENSHIFT_DATA_DIR"
        end
    end
    "Command: #{cmd}<br />#{msg}"
end

get '/delete' do
    begin
        cmd = "rm -f #{ENV['OPENSHIFT_DATA_DIR']}bigfile"
        ret = system(cmd)
        if ret == true
            msg = "The bigfile has been deleted."
        else
            msg = "Failed to delete the bigfile"
        end
    end
    "Command: #{cmd}<br />#{msg}"
end

get '/show' do
    begin
        cmd = "ls -lh #{ENV['OPENSHIFT_DATA_DIR']}bigfile"
        ret = system(cmd)
        output = `#{cmd}`
        if ret == true
            msg = "The bigfile exists."
        else
            msg = "The bigfile doesnot exist."
        end
    end
    "Command: #{cmd}<br />#{output}<br />#{msg}"
end


run Sinatra::Application
