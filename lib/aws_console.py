#!/usr/bin/env python

import sys
if sys.platform.startswith('win'):
    #We have to disable CA verification on the Windows boxes...
    #don't know how to fix, but it seems to work without it
    import libcloud.security
    libcloud.security.VERIFY_SSL_CERT = False

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import time
import paramiko
import os
from optparse import OptionParser
import datetime
import clog
import re

log = clog.get_logger()
parser = OptionParser()


def ssh_try(host, iterations = 5):
    private_key_file = os.path.expanduser("~/.ssh/libra.pem")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    mykey = paramiko.RSAKey.from_private_key_file(private_key_file)
    retries = iterations
    can_ssh = False
    while retries !=0:
        try:
            ssh.connect(host, username='root', pkey=mykey)
            can_ssh = True
            break
        except:
            retries -= 1
            #print "%s Retries: %s" % (time.ctime(), retries)
    return can_ssh

def config_parser():
    # these are required options.
    parser.add_option("-t", "--image_type", default="m1.medium", help="image type (m1.large|m1.small|m1.medium|t1.micro)")    
    parser.add_option("-a", "--action", help="action you want to take (list|create|store)")
    parser.add_option("-i", "--image_name", help="ami_id or devenv number, if none is given, then the latest devenv will be used.")
    parser.add_option("-n", "--name", help="name of the instance, if none is given, it will assigned a name pdevenv") 
    (options, args) = parser.parse_args()
    
    # make sure all the ducks are in a row
    if options.action == 'create':
        if options.name is None:
            import uuid
            options.name = "pdevenv_%s" % uuid.uuid1().hex[:6]
            log.info("No user instance name specified, system will assign auto-generated name \'%s' as label for the new instance" % options.name)
    return options, args


 
class AWS_Console(object):
    conn = None
    def __init__(self):
        aws = get_driver(Provider.EC2)
        self._get_credentials()
        self.conn = aws(self.AWSAccessKeyId, self.AWSSecretKey)
        
    def list_nodes(self):
        nodes = self.conn.list_nodes()
        #for node in nodes:
        #    print "name: %s" % node.name
        return nodes
    
    def list_images(self, filter='self'):
        images = self.conn.list_images(filter)
        log.info("Found %s images" % len(images))
        print("ID\t\t\tNAME")
        print("---------------------------------------------------")
        for image in images:
            print("%s\t  %s \t%s" % (image.id, image.name, image.extra['tag']))
            #self.info("xxx", 1)
        return images

    def get_image(self, ami_id):
        image = self.conn.get_image(ami_id)
        return image
    
    def create_node(self, node_name, image, image_type='m1.medium'):
        """
        create an new instance based on image object given.
        """
        log.info("Creating node: %s with image: %s" % (node_name, image.id))
        sizes = self.conn.list_sizes()
        instance_size = None
        for img_size in sizes:
            if img_size.id == image_type:
                instance_size = img_size
                break

        #if image_type in 'm1.large' or image_type in 't1.micro'
        node = self.conn.create_node(name=node_name, image=image, size=instance_size)
        node_avail = False
        print time.ctime()
        while not node_avail:
            nodes = self.conn.list_nodes()

            for n in nodes:
                if n.name == node_name:
                    if len(n.public_ip) !=0:
                        log.info("Node with IP: %s is ready" % n.public_ip[0])
                        node_avail = ssh_try(n.public_ip[0])
                        log.info("Giving the system time to come up...")
                        time.sleep(120)
                        return n
                        
            if node_avail:
                log.info("Node is ready to be used")
                break
            time.sleep(10)
        return node

    def get_all_devenv_images(self, sort_name=True, tag='qe-ready', pattern='devenv'):
        images = self.conn.list_images('self')
        devenv_images = {}
        for image in images:
            if image.extra['tag'] == tag:  # ONLY list images that are 'qe-ready'
                name = image.name.split('/')[1]
                if name.startswith(pattern):
                    # sort the array so the first element will be the latest image
                    if sort_name:
                        image_number = int(name.split('_')[1])
                    else:
                        image_number = name
                    devenv_images[image_number] = image
                #print "NAME: %s" % name
        return devenv_images

    def get_filtered_image(self, pattern):
        images = self.conn.list_images('self')
        pattern_is_ami = False
        image_found = False
        if pattern.startswith('ami'):
            pattern_is_ami = True
       
        if pattern_is_ami:
            try:
                image = self.get_image(pattern)
                image_found = True
                return image
             
            except:
                log.error("Can't find matching ami-id '%s' in AWS repo" %
                        pattern)
                sys.exit(1)

        for image in images:
            if pattern in image.name:
                image_found = True
                break
        if not image_found:
            log.error("Can't find matching image '%s'in AWS repo" % pattern)
            sys.exit(1)

        return image


    def get_nodes(self):
        nodes = self.conn.list_nodes()
        return nodes
    
    def get_instance(self, label, running=False):
        """ returns a node instance given the label """
        nodes = self.get_nodes()
        if label.startswith('i-'):
            label_is_name = False 
        else:
            label_is_name = True
        for node in nodes:
            if running:
                if node.state != 0: #if not running, let's ignore it
                    continue
            if label_is_name:
                if node.name == label:
                    return node
            else:
                if node.extra['instanceId'] == label:
                    return node


    def stop_node(self, node_name):
        
        node = self.get_instance(node_name)
        self.conn.ex_stop_node(node)
        res = self.conn.ex_create_tags(node, {'Name': 'terminate-me'})
        return node


    def _get_credentials(self):
        fr = open(os.path.expanduser("~/.awscred"), 'r')
        content = fr.read()
        fr.close()
        obj = re.search(r'AWSAccessKeyId\s*=\s*(\S+)',content)
        if obj:
            self.AWSAccessKeyId = obj.group(1)
        else:
            log.error("Bad format of ~/.awscred file: AWSAccessKeyId key is missing")
        obj = re.search(r'AWSSecretKey\s*=\s*(\S+)', content)
        if obj:
            self.AWSSecretKey= obj.group(1)
        else:
            log.error("Bad format of ~/.awscred file: AWSSecretKey key is missing")

        return (self.AWSAccessKeyId, self.AWSSecretKey)


def get_ami(instance_ip):
    import paramiko
    import os
    private_key_file = os.path.expanduser("~/.ssh/libra.pem")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    mykey = paramiko.RSAKey.from_private_key_file(private_key_file)

    ssh.connect(instance_ip, username='root', pkey=mykey)
    stdin, stdout, stderr = ssh.exec_command("facter | grep ami_id")
    ami_id = stdout.readline().split('=>')[1].strip()
    return ami_id

def _test():
    aws = AWS_Console()
    image = aws.get_image('ami-e7c51c8e')
    #node = aws.create_node('libcloud-dev', image)
    #nodes = aws.list_nodes()
    node = aws.create_node('ppp-dev', image, 't1.micro')

if __name__ == '__main__':
    (options, args)= config_parser()
 
    aws = AWS_Console()
    if options.action == 'list':
        log.info("Getting a list of images...")
        images = aws.list_images()

    elif options.action == 'create':
        ami_id = None
        if options.image_name is None:
            # find the latest devenv
            image_dict = aws.get_all_devenv_images()
            target_image = image_dict[max(sorted(image_dict))]
            log.info("User did not specify an ami or devenv name, using the latest '%s'" % target_image.name)
        else:
            target_image = aws.get_filtered_image(options.image_name)
        log.info("Create instance from ami '%s'..." % target_image.id)
        aws.create_node(options.name, target_image, options.image_type)

    elif options.action == 'stop':
        inst = aws.stop_node(options.name)
    else:
        log.error("Unsupported action '%s'" % options.action)
        parser.print_help()
