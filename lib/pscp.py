import paramiko
import scp
import os

class Pscp(object):
    scp = None
    ssh = None
    host = None

    def __init__(self, host='openshift-mtv-01', port=22, user='root', password='redhat'):
        # make connection
        if host:
            self.host = host

        if self.host == '10.14.16.138':
            password = 'vostok08'

        t = paramiko.Transport((host, port))
        t.connect(username=user, password=password)
        
        scp_sess = scp.SCPClient(t)
        
        # now, do the actual bootstrap process
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=password)
        self.ssh = ssh
        self.scp = scp_sess 

    def copy_from(self, src, dst='./'):
        """
        Copy a dir/file from remote host to specified place
        """
        if self.host != 'localhost':
            # don't need to do scp if we are already at localhost
            self.scp.get_r(src, dst)

    def copy_to(self, src, dst):
        remote_cmd = "mkdir -p %s" % dst
        #print remote_cmd
        stdin, stdout, stderr = self.ssh.exec_command(remote_cmd)
        #print stdout.readlines()
        #print stderr.readlines()
        if self.host != 'localhost':
            # don't need to do scp if we are already at localhost
            self.scp.put_r(src, dst)

    def copy_to_global_location(self, src, dst):
        """
        copy the html log over to the global location
        """
        # first make the top-level directory
        try:
            remote_cmd = "mkdir -p %s" % dst.rpartition(os.path.basename(dst))[0]
        except:
            #case, when dst ends with '/'
            remote_cmd = "mkdir -p %s" % dst
        print remote_cmd
        stdin, stdout, stderr = self.ssh.exec_command(remote_cmd)
        print stderr.readlines()
        remote_cmd = "cp -pr %s %s" % (src, dst)
        print remote_cmd
        stdin, stdout, stderr = self.ssh.exec_command(remote_cmd)
        print stderr.readlines()


    def __del__(self):
        self.ssh.close()

if __name__ == '__main__':
    #myscp = Pscp(host='localhost', user='pruan', password='vostok08')
    myscp = Pscp(host='10.14.16.138', user='peter', password='vostok08')
    src = '/var/www/html/testresults/201206/25/Collections_Demo_Demo01-279-20120625155434'
    dst = '/automation_logs/OpenShift_QE/automation/testresults/201206/25'
    global_log_basepath = "/automation_logs/OpenShift_QE/automation"

    global_dst = global_log_basepath + src.split('/var/www/html')[1]
    print global_dst
    myscp.copy_to_global_location(src, global_dst)
