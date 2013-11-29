#
#  File name: bandwith_for_spammers.py
#  Date:      2012/02/27 03:59
#  Author:    mzimen@redhat.com
#

import common
import Common.File
import OSConf
import rhtest
import time
import json

class OpenShiftTest(rhtest.Test):
    ACCOUNT = {
        'SMTP'     : 'smtp.googlemail.com',
        'USERNAME' : 'nohatshift@gmail.com',
        'PASSWORD' : 'vostok08'}
    ports = {    #limits per port
        '25': {'limit_kbps': 24,   
               'fsize_kb':32  
              },
        '587':{'limit_kbps': 256,
               'fsize_kb':128
              }}
    def initialize(self):
        self.ACCOUNT['RECIPIENT'] = self.config.OPENSHIFT_user_email
        self.summary = "[Runtime][rhc-cartridge][US1478] Bandwith restriction for spamming users"
        self.app_name = 'spam'+common.getRandomString(7)
        self.app_type = 'php'
        common.env_setup()

    def finalize(self):
        pass

class BandwidthForSpammers(OpenShiftTest):
    def test_method(self):
        self.add_step("Create a PHP app" , 
                common.create_app,
                function_parameters=[ self.app_name, 
                                      common.app_types[self.app_type], 
                                      self.config.OPENSHIFT_user_email, 
                                      self.config.OPENSHIFT_user_passwd, True],
                expect_return=0)

        self.add_step("Enable email functionality.",
                self.write_file, 
                expect_return=0)

        self.add_step("Verify the limits via remote script.",
                self.verify,
                expect_return=True)

        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)

    def verify(self):
        base_url = OSConf.get_app_url(self.app_name)
        opts="-s -H Pragma:no-cache"
        time.sleep(5)
        for port in self.ports.keys():
            time.sleep(10)
            url = base_url +'/spammer.php?port=%s&size=%s'%(port, self.ports[port]['fsize_kb'])
            fetch_cmd = "curl %s '%s'"%(opts, url)
            (retcode, output) = common.command_getstatusoutput(fetch_cmd)
            try:
                res = json.loads(output)
            except Exception as e:
                self.error("%s -- %s"%(e, output))
                return False
            self.debug(res)
            if res['transmission_rate_kbps'] > self.ports[port]['limit_kbps']:
                self.error("Transmission rate for port#%s was over the allowed limit."%port)
                return False
        return True

    def write_file(self):
        php_program='''
<?php

// PEAR
require_once('Mail.php');
require_once('Mail/mime.php');

// Sending Mail
function mail_sending($hostname, $port, $username, $password, $attachment ) {
    $extraheaders['From'] = '%(USERNAME)s';
    $extraheaders['To'] = '%(RECIPIENT)s';
    $extraheaders['Subject'] = 'Test message';

    $params['host'] = $hostname;
    $params['port'] = $port;
    $params['auth'] = true;
    $params['username'] = $username;
    $params['password'] = $password;
    //Enable this if you want to debug ERRORS!
    //Then don't expect to have valid JSON response.
    //$params['debug'] = true;

    $smtp = Mail::factory('smtp', $params);

    $message = new Mail_mime();
    $message->setTXTBody('Just testing...');
    $message->addAttachment($attachment);
    $body = $message->get();
    $headers = $message->headers($extraheaders);

    $start_time = time(); 
    $status = $smtp->send($extraheaders['To'], $headers, $body); 
    $end_time = time();

    if (PEAR::isError($status)) {
       $error = $smtp->getMessage();
    }else{
       $error = "Message successfully sent!";
    }

    $diff = $end_time - $start_time;
    $size = strlen($body);
    $speed = ( ( (float) $size * 8 ) / $diff ) / 1024;
    return array(
        "port"        => $port,
        "error"       => $error,
        "body_length" => $size,
        "filename"    => $attachment,
        "elapsed_in_seconds"     => $diff,
        "transmission_rate_kbps" => $speed
    );
}

// Configuration
$USERNAME = '%(USERNAME)s';
$PASSWORD = '%(PASSWORD)s';

// Creating testing attachments
if (isset($_GET['size'])){
    $size=$_GET['size'];
}else{
    $size=32;
}
$test_file = "/tmp/test.img";
system("dd if=/dev/urandom of=$test_file bs=1024 count=$size");

if (isset($_GET['port'])){
    $port = $_GET['port'];
}else{
    $port = 25;
}
$smtp_server='%(SMTP)s';
$res = mail_sending($smtp_server, $port, $USERNAME, $PASSWORD, $test_file);
print json_encode($res);

?>'''%(self.ACCOUNT)
        Common.File.append('%s/deplist.txt'%self.app_name, "Mail")
        Common.File.append('%s/deplist.txt'%self.app_name, "Mail_Mime")
        Common.File.write('%s/php/spammer.php'%self.app_name, php_program)
        cmd = [ 'cd %s '%self.app_name,
                'git add php/spammer.php',
                'git commit -a -m "Added email feature"',
                'git push']
        return common.command_getstatusoutput(" && ".join(cmd))[0]


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(BandwidthForSpammers)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of bandwith_for_spammers.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
