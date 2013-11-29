#!/usr/bin/python
import os
import sys
import commands
import pexpect

def remote_exec(hostname, username, password, cmd):
    #fout=file('mylog.txt','w')
    #cmd= "grep 'hello word testing' /tmp/test/test.log"
    #cmd="""/bin/sh -c "%s" """ %(cmd)
    print ">>>",cmd
    #child = pexpect.spawn(('ssh %s@%s %s' %(username,hostname,cmd)),timeout=6,maxread=2000,logfile=None)
    #child = pexpect.spawn("/usr/bin/ssh root@127.0.0.1",["grep 'hello word testing' /tmp/mytest.log"])
    #child = pexpect.spawn("""ssh root@127.0.0.1 "grep 'hello word testing' /tmp/mytest.log" """)
    user_hostname = "%s@%s" %(username,hostname)
    child = pexpect.spawn("/usr/bin/ssh",[user_hostname,cmd],timeout=6,maxread=2000,logfile=None)
    child.logfile_read = sys.stdout
    #fout=file('mylog.txt','w')
    #child.logfile=fout

    while True:
        index = child.expect(['(yes\/no)', 'password:', pexpect.EOF, pexpect.TIMEOUT])
        #print index
        if index == 0:
            child.sendline("yes")
        elif index == 1:
            child.sendline(password)
        elif index == 2:
            return child.before
        elif index == 3:
            return "TIMEOUT!!!"

#child.logfile_read = None # To turn off log

#a=remote_exec("127.0.0.1","root","redhat","cat /tmp/check.log > /tmp/test/test.log")
#a=remote_exec("127.0.0.1","root","redhat","grep 'hello word testing' /tmp/test/test.log")
#print a

def ssh_key_gen(key_file=None, key_type='rsa'):
    pre_cmd = "rm -rf %s %s.pub" %(key_file, key_file)
    if key_file != None:
        cmd = "%s; /usr/bin/ssh-keygen -t %s -N '' -f %s" %(pre_cmd, key_type, key_file)
    else:
        cmd = "%s; /usr/bin/ssh-keygen -t %s -N ''"  %(pre_cmd, key_type)
    print "Command: %s" %(cmd)
    return commands.getstatusoutput(cmd)

def ssh_copy_id(pub_key_file, username, password, hostname):
    user_hostname = "%s@%s" %(username, hostname)
    cmd = "ssh-copy-id -i %s %s" %(pub_key_file, user_hostname)
    print "Command: %s" %(cmd)
    child = pexpect.spawn(cmd, timeout=30, maxread=2000, logfile=None)
    child.logfile_read = sys.stdout
    while True:
        index = child.expect(['(yes\/no)', 'password:', pexpect.EOF, pexpect.TIMEOUT])
        #print index
        if index == 0:
            child.sendline("yes")
        elif index == 1:
            child.sendline(password)
        elif index == 2:
            break
        elif index == 3:
            print "TIMEOUT!!! Try ssh connect manually!"
            break

    #print "-----%s-------" %(child.before)

    if child.before.find("Now try logging into the machine") != -1:
        return 0
    else:
        print "ssh-copy-id is terminated abnormally, pls check!!!"
        return 1

       


def main():
    usage = """
usage: %s -i target_host -u username -p password [-f key_file] [-t key_type]
""" %(os.path.basename(__file__))

    from optparse import OptionParser
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--target_host", dest="target_host", help="setup auto ssh between local host and target host")
    parser.add_option("-u", "--username", dest="username", help="username for logging into target host")
    parser.add_option("-p", "--password", dest="password", help="password for loggint into target host")
    parser.add_option("-f", "--key_file", dest="key_file", help="specify generated key file. Default: mykey (optional)")
    parser.add_option("-t", "--key_type", dest="key_type", help="specify generated key type. Default: rsa (optional)")

    (options, args) = parser.parse_args()
    if options.target_host == None or options.username == None or options.password == None:
        print usage
        sys.exit(1)
    
    if options.key_file == None:
        key_file =  "mykey"
    else:
        key_file = options.key_file

    if options.key_type == None:
        key_type =  "rsa"  
    else:
        key_type = options.key_type

    (ret, output) = ssh_key_gen(key_file, key_type)
    print output
    if ret == 0:
        if ssh_copy_id("%s.pub" %(key_file), options.username, options.password, options.target_host) != 0:
            return 1
    else:
        print "fail to generate ssh key file"
        return ret

    cmd = "ssh -i %s %s@%s 'free -m'" %(key_file, options.username, options.target_host)
    print "Command: %s" %(cmd)
    (ret, output)=commands.getstatusoutput(cmd)
    print output
    if ret == 0:
        return 0
    else:
        return 1



if __name__ == "__main__":
    exit_code=main()
    sys.exit(exit_code)
