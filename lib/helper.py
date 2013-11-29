#!/usr/bin/python

import aws_console
import uuid
import subprocess
import commands
import os
import json
import re
import random
import string
import paramiko
import time
import sys
import signal
import clog
import base64
from optparse import OptionParser

express_conf_file = "%s/.openshift/express.conf" %(os.environ['HOME'])
global_express_conf_file = "/etc/openshift/express.conf"
COMMAND_TIMEOUT=1200    #seconds to wait to kill never ending subprocesses

log = clog.get_logger()
parser = OptionParser()


def get_default_rhlogin():
    if not os.getenv('OPENSHIFT_user_email') or not os.getenv('OPENSHIFT_user_passwd'):
        log.error("Please check these ENV var: OPENSHIFT_user_email OPENSHIFT_user_passwd")
        raise Exception("Environment Variables OPENSHIFT_* Not Found.")
    return (os.getenv('OPENSHIFT_user_email'), os.getenv('OPENSHIFT_user_passwd'))


# helper function for to measure timedelta.
def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        log.debug("%r (%r, %r) %2.2f sec" % (method.__name__, args, kw, te-ts))
        return result

    return timed

class Alarm(Exception):
    pass

class TimeoutError(Exception):
    pass

class MercyException(Exception):
    pass


@timeit
def create_node(instance_tag, image_name=None, image_size="m1.medium"):
    aws_obj = aws_console.AWS_Console()
    if image_name == None:
        image_dict = aws_obj.get_all_devenv_images()
        target_image = image_dict[max(sorted(image_dict))]
        image_name = target_image.name.split('/')[1]
    if instance_tag == None:
        instance_tag="QE_auto_%s_%s" %(image_name, uuid.uuid1().hex[:6])
    elif not instance_tag.startswith("QE_"):
        instance_tag="QE_%s" %(instance_tag)
    log.info("Instance tag: %s"%instance_tag)
    log.info("Image size: %s"%image_size)
    image = aws_obj.get_filtered_image(image_name)
    node = aws_obj.create_node(instance_tag, image, image_size)
    log.info("instance_ip=%s" %(node.public_ip[0]))
    log.info("instance_name=%s" %(instance_tag))
    return node.public_ip[0]
create_broker=create_node #alias


def get_public_ip(private_ip):
    # curl http://169.254.169.254/latest/meta-data/local-ipv4
    ssh_options = "-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
    cmd = "scp %s %s root@%s: "%(ssh_options, get_root_ssh_key_(), get_instance_ip())
    (ret, output) = cmd_get_status_output(cmd, quiet=True)
    if ret != 0:
        log.error("Unable to copy private key to broker")
        return None

    key_name = get_root_ssh_key_().split('/')[-1]
    cmd = ["curl -k -s -X GET http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null",
           "rm -f %s"%key_name]
    (ret, output) = rcmd_get_status_output2("ssh %s -i ./%s root@%s %s 2>/dev/null"%(
           ssh_options,
           key_name, 
           private_ip, 
           ";".join(cmd)))
    if ret==0:
        obj = re.search("([^\s]+)$",output)
        if obj:
            return obj.group(1)
        else:
            return None
    else:
        log.error("Unable to determine public IP address from %s"%private_ip)
        return None


def get_internal_hostname(public_ip):
    pass


def get_private_ip(public_ip):
    """
    Returns internal EC2 IP address by internal http request to 169.254.169.254
    """
    cmd = "curl -k -s -X GET http://169.254.169.254/latest/meta-data/local-ipv4 2>/dev/null"
    private_ip=None
    (ret, output) = rcmd_get_status_output2(cmd, host=public_ip)
    if ret==0:
        obj = re.search("([^\s]+)$",output)
        if obj:
            private_ip = obj.group(1)

    if private_ip is None:
        log.error("Unable to determine private IP address from %s: %s"%(public_ip,output))

    return private_ip


def add_node(instance_tag, image_name=None, image_size="m1.medium", broker_ip=None):
    """
    Node: Commands are copied from li/devenv script
    """
    broker = {}
    if broker_ip is None:
        broker['internal_ip'] = get_private_ip(get_instance_ip())
    else:
        broker['internal_ip'] = get_private_ip(broker_ip)

    log.debug("Private broker's IP = %(internal_ip)s"%broker)
    #modify the broker...
    log.debug("Modifying the broker")
    ssh_cmd = [ "sed -i 's,^plugin.qpid.host.ha.*=.*,plugin.qpid.host.ha=%(internal_ip)s,' /etc/mcollective/client.cfg"%broker,
                "sed -i 's,^plugin.qpid.host.ha.*=.*,plugin.qpid.host.ha=%(internal_ip)s,' /etc/mcollective/server.cfg"%broker,
                "sed -i 's,^ssl-cert-name.*=.*,ssl-cert-name=%(internal_ip)s,' /etc/qpidd.conf"%broker,
                "sed -i 's,^server_id.*=.*,server_id=%(internal_ip)s,' /etc/openshift/devenv/qpid/make-certs.sh"%broker,
                "sed -i 's,^owner_domain_name.*=.*,owner_domain_name=%(internal_ip)s,' /etc/openshift/devenv/qpid/make-certs.sh"%broker,
                "sed -i 's,^#-A,-A,' /etc/sysconfig/iptables",
                "sed -i 's,^BROKER_HOST.*=.*,BROKER_HOST=%(internal_ip)s,' /etc/openshift/node.conf"%broker,
                "cd /etc/openshift/devenv/qpid/",
                "./make-certs.sh",
                "/bin/cp test/client_db/* /etc/qpid/pki/client_db/; /bin/cp test/server_db/* /etc/qpid/pki/server_db/",
                "restorecon -R /etc/qpid/pki/",
                "chmod +r /etc/qpid/pki/client_db/* /etc/qpid/pki/server_db/*",
                "service iptables restart",
                "service activemq restart",
                "service mcollective restart"]
    (ret, output) = rcmd_get_status_output(" ; ".join(ssh_cmd), quiet=False)
    #ret = 1
    if ret != 0:
        log.error("Interrupted: Unable to modify broker for multi node setup.")
        return 1
    #do setup for new node
    #new_node_public_ip = create_node(instance_tag, image_name, image_size)
    new_node_public_ip='23.20.68.196'
    log.debug("Modifying new node setup... of new %s"%new_node_public_ip)
    ssh_options = " -i %s  -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "%(get_root_ssh_key_())
    cmd_get_status_output('cd /tmp; rm -rf /tmp/test; scp %(opt)s -r root@%(broker)s:/etc/openshift/devenv/qpid/test/ .; scp %(opt)s -r test/client_db/* root@%(hostname)s:/etc/qpid/pki/client_db/; scp %(opt)s -r test/server_db/* root@%(hostname)s:/etc/qpid/pki/server_db/'%({'hostname': new_node_public_ip, 'opt': ssh_options, 'broker': get_instance_ip()}))
    cmd_get_status_output('cd /tmp; rm -rf /tmp/clients; scp %(opt)s -r root@%(broker)s:/etc/mcollective/ssl/clients/ .; scp %(opt)s -r clients/* root@%(hostname)s:/etc/mcollective/ssl/clients/'%({'hostname': new_node_public_ip, 'opt': ssh_options, 'broker': get_instance_ip()}))

    ssh_cmd = ["sed -i 's,^plugin.qpid.host.ha.*=.*,plugin.qpid.host.ha=%(internal_ip)s,' /etc/mcollective/server.cfg"%broker,
               "restorecon -R /etc/qpid/pki/; chmod +r /etc/qpid/pki/client_db/* /etc/qpid/pki/server_db/*",
               "sed -i 's,^BROKER_HOST.*=.*,BROKER_HOST=%(internal_ip)s,' /etc/openshift/node.conf"%broker,
               "service activemq stop; service mcollective restart"]
    (ret, output) = rcmd_get_status_output(" ; ".join(ssh_cmd), host=new_node_public_ip)
    if ret == 0:
        rcmd_get_status_output('mco ping', quiet=False)
        return 0
    else:
        log.error(output)
        return 1

@timeit
def shutdown_node(instance_name):
    aws_obj = aws_console.AWS_Console()
    print "Shuting down: %s" %(instance_name)
    aws_obj.stop_node(instance_name)


def append_file(fpath, content, flag='w+', mode=0777):
    #import stat
    fp = open(fpath, flag)
    fp.write(content)
    fp.close()
    os.chmod(fpath, mode) #, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


def write_file(fpath, content, flag='w', mode=0777):
    #import stat
    fp = open(fpath, flag)
    fp.write(content)
    fp.close()
    os.chmod(fpath, mode) #stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


def set_libra_server(instance_ip):
    """
    Do setup :
     * environment variable $OPENSHIFT_libra_server
     * $HOME/.openshift/express.conf file with:
        libra_server=<instance_ip>

    This step should be executed only once at the begining,
    because all of the RHC command will use this value later.
    """
    if instance_ip == 'int.openshift.redhat.com':
        run_mode = 'INT'
    elif instance_ip == 'stg.openshift.redhat.com':
        run_mode = 'STG'
    elif instance_ip == 'openshift.redhat.com':
        run_mode = 'PROD'
    elif instance_ip.find("example.com") != -1 or instance_ip.find("test.com") != -1 or instance_ip.find("broker") != -1:
        run_mode = 'OnPremise'
    else:
        run_mode = 'DEV'

    os.putenv('OPENSHIFT_libra_server', instance_ip)
    (user, passwd) = get_default_rhlogin()
    fname = os.path.join(get_tmp_dir(),"libra_server-%s"%user)
    write_file(fname, instance_ip)
    log.info("Setting libra server to %s in %s" %(instance_ip, express_conf_file))
    if not os.path.exists(express_conf_file):
        log.debug("Creating new config file in %s"%express_conf_file)
        os.mkdir(os.path.dirname(express_conf_file))
        if run_mode == 'DEV':
            write_file(express_conf_file, "libra_server=%s\ninsecure=true\n" %(instance_ip))
        else:
            write_file(express_conf_file, "libra_server=%s\n" % (instance_ip))
    else:
        cf = open(express_conf_file, 'r')
        output = cf.read()
        cf.close()
        output = re.sub(re.compile(r'^libra_server.*$', re.MULTILINE), 
                        "libra_server='%s'"%instance_ip, output)
        if not re.search('^libra_server=', output, re.MULTILINE):
            log.debug("Unable to find libra_server...appending new line...")
            output = output.strip()
            output += "\nlibra_server='%s'"%instance_ip
        if run_mode == 'DEV':
            if re.search('^insecure=', output, re.MULTILINE):
                output = re.sub(re.compile(r'^insecure.*$', re.MULTILINE), 
                        'insecure=true', output)
            else:
                output += "\ninsecure=true"
        else:
            match = re.search('^insecure=.*$', output, re.MULTILINE)
            if match:
                output = output[:match.start()] + output[match.end():]
        write_file(express_conf_file, output)


def get_instance_ip_by_tag(instance_tag):
    if instance_tag is None:
        raise Exception("ERROR: get_instance_ip_by_tag(): Missing/None argument.")
    aws_obj = aws_console.AWS_Console()
    node = aws_obj.get_instance(instance_tag, True)
    return node.public_ip[0]

def get_instance_ip(instance_tag=None):
    """
    If no instance_tag argument defined:
        Returns the IP address of libra server. Order of checking:
            - $OPENSHIFT_libra_server
            - ~/.openshift/express.conf
            - /etc/openshfit/express.conf

        Otherwise throws exception if none of above was found

    If instance_tag is defined, returns tries to get IP of running EC2 instance.
    """
    if instance_tag is not None:
        return get_instance_ip_by_tag(instance_tag)
    (user, passwd) = get_default_rhlogin()
    tmp_file = os.path.join(get_tmp_dir(),"libra_server-%s" %(user))
    if os.getenv("OPENSHIFT_libra_server"):
        return os.getenv("OPENSHIFT_libra_server")
    elif os.path.exists(express_conf_file):
        c = open(express_conf_file).read()
        re_match_obj = re.search("^libra_server\s*=[\s']*([^\s']+)", c, re.M)
        if re_match_obj != None:
            ret_string = re_match_obj.group(1)
            #print "Found libra_sever in %s: %s" %(express_conf_file, ret_string)
            return ret_string
        else:
            raise Exception("Not found libra_server in %s !!!" %(express_conf_file))
    elif os.path.exists(global_express_conf_file):
        c = open(global_express_conf_file).read()
        re_match_obj = re.search(r"^libra_server\s*=[\s']*([^\s']+)", c, re.M)
        if re_match_obj != None:
            #print "Found libra_sever in %s: %s" %(global_express_conf_file, re_match_obj.group(1))
            return re_match_obj.group(1)
        else:
            raise Exception("Not found libra_server in %s !!!" %(global_express_conf_file))
    elif os.path.exists(tmp_file):
        f = open(tmp_file, 'r')
        libra_ip = f.read()
        #print "Found libra_sever in %s: %s" %(tmp_file, libra_ip.strip())
        return libra_ip.strip()
    else:
        raise Exception("No libra sever specified !!!!")
get_broker_ip=get_instance_ip #alias

def extract_variants(arguments):
    variants = None

    if arguments is None:
        return variants

    try:
        if not re.match(r"^{", arguments) and (type(eval(arguments)) is dict) and ('VARIANTS' in eval(arguments).keys()):
            return eval(arguments)['VARIANTS']
    except:
        pass

    try:
        arguments = arguments.replace("'",'"') #necessary for JSON
        if not re.match(r"^{", arguments):
            json_args = json.loads(" { "+arguments+" } ")
        else:
            json_args = json.loads(arguments)

        if (json_args.has_key('variants')):
            variants=json_args['variants']
        elif (json_args.has_key('VARIANTS')):
            variants=json_args['VARIANTS']
        elif (json_args.has_key('variant')):
            variants=json_args['variant']
        else:
            pass
            #print "WARNING : UNABLE TO FIND VARIANTS field IN ARGUMENTS"
    except Exception as e:
        log.warning("INVALID JSON FORMAT FOR ARGUMENTS.:%s"%str(e))

    return variants


def get_domain_name_(user_email=None, user_passwd=None):
    """
    Returns current openshift domain per given user.
    """
    import openshift
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    li = openshift.Openshift(host=get_instance_ip(), 
                             user=user_email, 
                             passwd=user_passwd)
    try:
        status, response = li.domain_get()
        if (status == 'OK' or status == 'Not Found'):
            return response
        else:
            raise Exception("Unable to get domain name. status=%s, response=%s"%(status, response))
    except openshift.OpenShiftNullDomainException:
        return None


def get_random_string(length = 10):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(0, length))


def get_default_ssh_key_():
    return os.getenv('HOME')+"/.ssh/id_rsa"


def rcmd_get_status_output(cmd, user='root', host=None, key_filename=None, quiet=True):
    """
    Exec command under given user and retusn tuple: (ret_code, stdout)
    (host==None) => BROKER
    """
    rhcsh_banners=[
        '[\S\s.\n\r\b\t]*WARNING: This ssh terminal was started without a tty[\S\s.\n\r\b\t]+ssh -t',
        '[\S\s.\n\r\b\t]*Welcome to OpenShift shell[\S\s.\n\r\b\t]+Type "help" for more info.']

    if (user == 'root'):
        if not host:
            host = get_instance_ip()
        if not key_filename:
            key_filename = get_root_ssh_key_()
    else:
        if host is None:
            raise Exception("Host is undefined. (rcmd_get_status_output())")
        if not key_filename:
            key_filename = get_default_ssh_key_()

    remote_cmd = cmd
    if not quiet:
        print "DEBUG[SSH]: remote host: %s; user: %s; ssh key: %s" %(host, user, key_filename)
    print "DEBUG[SSH]: remote cmd:%s"%remote_cmd
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, key_filename=key_filename)
    chan = ssh.get_transport().open_session()
    chan.settimeout(COMMAND_TIMEOUT)
    chan.exec_command(remote_cmd)
    ret_code = chan.recv_exit_status() #wait for the end...
    chan.set_combine_stderr(True)
    stdout_data = []
    #stderr_data = []
    nbytes = 1024 #1kb buffer should be enough
    time.sleep(1) #let's wait for a while
    while chan.recv_ready():
        stdout_data.append(chan.recv(nbytes))
        sys.stderr.write('.')
        sys.stderr.flush()
        time.sleep(1) #let's wait for a while 
    ret_output = "".join(stdout_data)
    '''
    time.sleep(1) #let's wait for a while
    while chan.recv_stderr_ready():
        stderr_data.append(chan.recv(nbytes))
        sys.stderr.write('_')
        sys.stderr.flush()
        time.sleep(1) #let's wait for a while 
    stderr_data = "".join(stderr_data)
    '''
    chan.close()
    ssh.close()
    print "DEBUG[SSH]: exit code:%s"%ret_code

    #omit the rhcsh banners from the output
    if ('user' != 'root'):
        for ignore_pattern in rhcsh_banners:
            ret_output = re.sub(ignore_pattern,'',ret_output)
    ret_output = re.sub('^Pseudo-terminal will not.*$','',ret_output, re.MULTILINE)
    ret_output = re.sub('^Warning: Permanently added.*$','',ret_output, re.MULTILINE)

    if not quiet:
        #print "[SSH]: output:%s"%ret_output
        log.debug("[SSH]: output:%s"%ret_output)
    return (ret_code, ret_output)


def cmd_get_status(command, timeout=COMMAND_TIMEOUT, quiet=False):
    #Method  1, can not kill all child process
    #print """\nRunning Command - %s""" %(command)
    #status = subprocess.call(command, timeout=timeout, shell=True)
    #print "Command Return:", status
    #return status
    
    #Method 2, can kill all child process, but no output can be seen when command hang there
    #return command_getstatusoutput(command, False, timeout)[0]

    #Best method
    if not quiet:
        print """\nRunning Command - %s""" %(command)
    obj = subprocess.Popen(command, shell=True)
    if timeout >= 0:
        signal.signal(signal.SIGALRM, _alarm_handler)
        signal.alarm(timeout)
    try:
        status =  obj.wait()
        if not quiet:
            print "Command Return:", status
        return status
    except Alarm:
        if os.uname()[0] == 'Linux':
            child_process_list = get_child_process_list(str(obj.pid))
            if not quiet:
                print "All child process belong to %s: %s" %(obj.pid, child_process_list)
        signal.alarm(0)
        obj.terminate()
        time.sleep(2)
        obj.kill()
        time.sleep(2)
        try:
            os.killpg(obj.pid, signal.SIGTERM)
            os.killpg(obj.pid, signal.SIGKILL)
        except:
            pass
        #obj.wait()
        if os.uname()[0] == 'Linux':
            commands.getstatusoutput("kill -9 %s" %(" ".join(child_process_list)))
        raise TimeoutError("Timeout %s seconds for command `%s` has expired."%(timeout, command))
    finally:
        signal.alarm(0)


def cmd_get_status_output(command, quiet = False, timeout=COMMAND_TIMEOUT):
    if not quiet:
        print """\nRunning Command - %s""" %(command)

    output=""
    obj = subprocess.Popen(command, stdin=open(os.devnull,'rb'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    if timeout >= 0:
        signal.signal(signal.SIGALRM, _alarm_handler)
        signal.alarm(timeout)
    try:
        while obj.poll() == None:
            text = obj.stdout.readline()
            if not quiet:
                sys.stdout.write("%s" %(text))
                sys.stdout.flush()
            output = output + text
    except Alarm:
        if os.uname()[0] == 'Linux':
            child_process_list = get_child_process_list(str(obj.pid))
            if not quiet:
                print "All child process belong to %s: %s" %(obj.pid, child_process_list)
        signal.alarm(0)
        obj.terminate()
        time.sleep(2)
        obj.kill()
        time.sleep(2)
        try:
            os.killpg(obj.pid, signal.SIGTERM)
            os.killpg(obj.pid, signal.SIGKILL)
        except:
            pass
        #obj.wait()
        if os.uname()[0] == 'Linux':
            commands.getstatusoutput("kill -9 %s" %(" ".join(child_process_list)))
        raise TimeoutError("Timeout %s seconds for command `%s` has expired."%(timeout,command))
    finally:
        signal.alarm(0)

    last_text = obj.stdout.read()
    if not quiet:
        sys.stdout.write(last_text)
        sys.stdout.flush()
    output = output + last_text
    #print "-----"
    #print output
    #print "-----"
    status = obj.poll()
    if not quiet:
        print "Command Return:", status
    return (status, output)


def remote_batch(cmd, user="root", host=None, key_filename=None, quiet=True):
    """
    Run remotely command and do scp of result.
    Returns status and output as if run locally.
    """
    tmp_dump = get_random_string(10)+'.dump' #remote stdout
    tmp_code = "%s.sh"%get_random_string(10)
    if key_filename is None:
        if (user == 'root'):
            key_filename = get_root_ssh_key_()
        else:
            key_filename = get_default_ssh_key_()
    if host is None:
        host = get_instance_ip()
    ssh_options = " -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no  -i %s "%key_filename
    try:
        fw = open(tmp_code, 'wb')
        fw.write("#!/bin/sh\n\n%s"%cmd)
        fw.close()
        #SCP file to the host
        cmd = "scp %s %s %s@%s:"%(ssh_options, tmp_code, user, host)
        (status, output) = cmd_get_status_output(cmd, quiet=quiet)
        if status != 0:
            raise Exception("Unable to copy batch script to the remote host. %s"%output)
        #RUN remotely
        cmd = "sh ./%s >%s 2>&1"%(tmp_code, tmp_dump)
        (status, output) = rcmd_get_status_output(cmd, user, host)
        #SCP results back
        cmd = "scp %s %s@%s:%s ./"%(ssh_options, user, host, tmp_dump)
        (_ret, _output) = cmd_get_status_output(cmd, quiet=quiet)
        if _ret != 0:
            raise Exception("ERROR: Unable to get dump file from broker")

        output = open(tmp_dump.split('/')[-1], "rb").read()
    except Exception as e:
        log.error("Unable to open/parse file: %s"%str(e))
        raise e
    finally:
        #CLEAN locally and remotely
        (ret, _output) = rcmd_get_status_output("rm -f %s %s"%(tmp_dump,tmp_code), quiet=quiet)
        if os.path.exists(tmp_dump):
            os.remove(tmp_dump)

    return (status, output)


def rcmd_get_status_output2(cmd, user='root', host=None, key_filename=None, quiet=True):
    """
    Run command under given user and retusn tuple: (ret_code, stdout)
    Via SSH not by paramiko, which is veeryyyy slow
    """
    ssh_options = " -t -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
    rhcsh_banners=[
        '[\S\s.\n\r\b\t]*WARNING: This ssh terminal was started without a tty[\S\s.\n\r\b\t]+ssh -t',
        '[\S\s.\n\r\b\t]*Welcome to OpenShift shell[\S\s.\n\r\b\t]+Type "help" for more info.']

    if (user == 'root'):
        if not host:
            host = get_instance_ip()
        if not key_filename:
            key_filename = get_root_ssh_key_()
    else:
        if host is None:
            raise Exception("Host is undefined. (rcmd_get_status_output())")
        if not key_filename:
            key_filename = get_default_ssh_key_()

    remote_cmd = cmd
    if not quiet:
        print "DEBUG[SSH]: remote host: %s; user: %s; ssh key: %s" %(host, user, key_filename)
        print "DEBUG[SSH]: remote cmd:%s"%remote_cmd
    cmd = r"stdbuf -o0 -i0 ssh %s -i %s %s@%s '%s'"%(ssh_options, 
                                                        key_filename,
                                                        user, 
                                                        host, 
                                                        remote_cmd)
    (ret_code, ret_output) = cmd_get_status_output(cmd, quiet=True)

    #omit the rhcsh banners from the output
    if (user != 'root'):
        for ignore_pattern in rhcsh_banners:
            ret_output = re.sub(ignore_pattern,'',ret_output)

    ret_output = re.sub('^Pseudo-terminal will not.*$','',ret_output, re.MULTILINE)
    ret_output = re.sub('^Warning: Permanently added.*$','',ret_output, re.MULTILINE)

    if not quiet:
        print "DEBUG[SSH]: output:%s"%ret_output
    return (ret_code, ret_output)


def get_root_ssh_key_():
    server_ip = get_instance_ip()
    etc_dir = get_etc_dir()
    if server_ip.find("example.com") != -1 or server_ip.find("test.com") != -1:
        ssh_key = etc_dir + '/onpremise/onpremise.pem'
    else:
        ssh_key = etc_dir + '/libra.pem'
    if not os.path.isfile(ssh_key):
        raise IOError("The %s file doesn't exist."%ssh_key)
    st = os.stat(ssh_key)
    #if not bool(st.st_mode & stat.S_IRUSR):
    os.chmod(ssh_key, 0400)

    return ssh_key


def _alarm_handler(signum, frame):
    raise Alarm


def get_lib_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_etc_dir():
    return os.path.abspath(get_lib_dir() + "/../etc")


def get_child_process_list(pid):
    # input:  string or list
    # output: list
    if isinstance(pid, list):
        child_process_list = []
        for i in pid:
            (status, output) = cmd_get_status_output("pgrep -P %s" %(i))
            if status == 0:
                tmp_list = output.split('\n')
                #pid = pid + get_child_process_list(tmp_list)
                child_process_list = child_process_list + tmp_list
                child_process_list = child_process_list + get_child_process_list(tmp_list)
            else:
                pass
        #return pid
        return child_process_list
    elif isinstance(pid, str):
        return get_child_process_list([pid])
    else:
        print "Neither string or list"
        raise


def valid_cache(filename, expiration_hours=6):
    """ Returns True if mtime of file is not older than 
        expiration_hours argument """
    if not os.path.exists(filename):
        return False
    st = os.stat(filename)
    now = time.time()
    valid_period = expiration_hours*60*60
    #log.debug("%s > %s"%(st.st_mtime, (now - valid_period)))
    if st.st_mtime > (now - valid_period):
        print "[CACHE] %s FRESH"%filename
        return True
    else:
        print "[CACHE] %s EXPIRED"%filename
        return False


def lock_file(filename):
    return os.open(filename, os.O_EXCL|os.O_RDWR)


def unlock_file(lock):
    lock.close()


def exclusive(func):
    """ Exclusive decorator """
    def exclusived(*args, **kw):
        lockfile = "%s/."%get_tmp_dir()+func.__name__+".lock"  #waiting for lock
        sys.stderr.write("EXCL: Waiting for exclusive access[%s]"%lockfile)
        sys.stderr.flush()
        oldumask = os.umask(0000)
        lock = lock_file(lockfile)  #waiting for lock
        result = func(*args, **kw)
        unlock_file(lock)
        if os.path.exists(lockfile):
            os.unlink(lockfile)
        os.umask(oldumask)
        sys.stderr.write("EXCL: released[%s]"%lockfile)
        sys.stderr.flush()
        return result

    return exclusived


def repeat_if_failure(func):
    """ Repeater decorator for MercyException handling """
    def repeater(*args, **kw):
        result = None
        for attempt in range(2):
            try:
                result = func(*args, **kw)
                break
            except MercyException as e:
                log.warning("An attempt of %s failed (reason: %s)."%(func.__name__,e))
                time.sleep(5)
        return result
    return repeater 


def get_current_username():
    import getpass
    return getpass.getuser()


def get_homedir(user=None):
    if user is None:
        user = get_current_username()
    return os.path.expanduser('~%s'%user)
    

def get_tmp_dir():
    if sys.platform == 'win32':
        return os.getenv('TMP')
    else:
        return os.path.expanduser('~/tmp/')


def detect_os():
    """ Returns [String] of the operating system : 
          ['FedoraXX', 'Debian', 'Ubuntu', 'RedHat' ] """
    if os.path.isfile("/etc/debian_version"):
        return "Debian"
    elif os.path.isfile("/etc/fedora-release"):
        fr = open("/etc/fedora-release", "r")
        obj = re.search(r"Fedora release (\d+)", fr.read())
        fr.close()
        return "Fedora%s"%obj.group(1)
    elif os.path.isfile("/etc/redhat-release"):
        return "RedHat"
    elif os.path.isfile("/etc/lsb-release"):
        return "Ubuntu"
    else:
        raise Exception("Unable to detect Linux distribution...")


def dump_env():
    for k in os.environ.keys():
        print k,"=",os.environ[k]

def setup_rhc_client(version=None, branch="candidate"):
    import setup_client
    return setup_client.do_setup(version, branch)


def inject_string_by_re(regex, injection, target, after=True):
    """Inserts a string on the new line, if previous line matches regex"""
    #content  = content[:pos] + new + content[pos:]
    injected = []
    rex = re.compile(r"%s"%regex)
    hit = 0 
    for line in target.split('\n'):
        injected.append(line)
        if rex.search(line):
            if after:
                injected.append(injection)
            else:
                injected.insert(len(injected)-1, injection)
            hit += 1
    if hit == 0:
        log.warning("No injection!")
    elif hit>1:
        log.warning("Multiple injection (%d)!"%hit)
    return "\n".join(injected)


def get_auth_headers(login, password):
    """Returns dict() with HTTP authentication headers"""
    return {'Authorization' : "Basic %s"% base64.b64encode('%s:%s' % (login, password))}


def sshPKeyToFingerprint(pkey):
    import hashlib
    key = base64.b64decode(pkey)
    fp_plain = hashlib.md5(key).hexdigest()
    return ':'.join(a+b for a,b in zip(fp_plain[::2], fp_plain[1::2]))


def setup_ssh_config():
    ssh_config = """
Host *.stg.rhcloud.com
    IdentityFile ~/.ssh/id_rsa
    VerifyHostKeyDNS yes
    #LogLevel DEBUG
    PreferredAuthentications publickey
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/openshift_known_hosts.stg

Host *.int.rhcloud.com
    IdentityFile ~/.ssh/id_rsa
    VerifyHostKeyDNS yes
    PreferredAuthentications publickey
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/openshift_known_hosts.int

Host *.dev.rhcloud.com
    IdentityFile ~/.ssh/id_rsa
    VerifyHostKeyDNS yes
    #LogLevel DEBUG
    PreferredAuthentications publickey
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/openshift_known_hosts.dev

"""
    cfile = os.path.expanduser("~/.ssh/config")

    if not os.path.exists(cfile):
        write_file(cfile, ssh_config, mode=0600)
    else:
        for line in open(cfile):
            if "Host *.dev.rhcloud.com" in line:
                return 
        append_file(cfile, ssh_config, mode=0600)

