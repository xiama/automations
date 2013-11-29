#!/usr/bin/env python
#
# Helper script for updating RHC clients based on OS
#
# mzimen@redhat.com
#

import os
import sys
import re
import fcntl
from helper import *

'''
BASE_REPO_HOST='https://mirror.openshift.com/'
URL = { "gem": {"candidate": "/libra/rhel-6-libra-candidate/client/gems/",
                "stage": "/libra/rhel-6-libra-stage/client/gems/"},
        "yum": {"candidate": "/libra/rhel-6-libra-candidate/x86_64/Packages/",
                "stage": "/libra/rhel-6-libra-stage/x86_64/Packages/"}}
'''
BASE_REPO_HOST='https://mirror1.ops.rhcloud.com/'
URL = { "gem": {"candidate": "/libra/libra-rhel-6.3-candidate/client/gems/",
                "stage": "/libra/libra-rhel-6.3-stage/client/gems/"},
        "yum": {"candidate": "/libra/libra-rhel-6.3-candidate/x86_64/Packages/",
                "stage": "/libra/libra-rhel-6.3-stage/x86_64/Packages/"}}
CERT=os.environ['RHTEST_HOME']+'/etc/client-cert.pem'
KEY=os.environ['RHTEST_HOME']+'/etc/client-key.pem'

CONFIG={
    "Fedora19": 'gem',
    "Fedora18": 'gem',
    "Fedora17": 'gem',
    "Debian": 'gem',
    "Ubuntu": 'gem',
    "Fedora16": 'yum',
    "RedHat": 'yum'}

if os.getuid() == 0:
    need_sudo=""
else:
    need_sudo="sudo"


def fetch_rhc_client_file(file_name, branch):
    if file_name.endswith(".gem"):
        method = "gem"
    elif file_name.endswith(".rpm"):
        method = "yum"
    url = BASE_REPO_HOST + URL[method][branch] + file_name
    dst_file = os.path.expanduser("~/%s" % (file_name))
    cmd = 'curl -3 -f -# -k --cert %s --key %s %s --output %s'%(CERT, KEY, url, dst_file)
    attempts=3
    log.info("Fetching %s from branch %s" % (file_name, branch))
    for a in range(0,attempts):
        (status, output) = cmd_get_status_output(cmd, quiet=True)

        if status!=0:
            continue
        else:
            break
    if status!=0:
        log.error("CMD="+cmd)
        log.error(output)
    return (status, dst_file)

def install_rhc_client_file(file_name):
    if not os.path.exists(file_name):
        raise Exception("client file %s doesn't exist"%file_name)
    log.info("Going to install %s" % (file_name))
    if file_name.endswith(".gem"):
        _gem_install_rhc_client_file(file_name)
    elif file_name.endswith(".rpm"):
        _yum_install_rhc_client_file(file_name)

def _gem_install_rhc_client_file(file_name):
    if detect_os() in ("Ubuntu", "Debian"):
        cmd = "%s gem uninstall -ax rhc ; %s gem install %s" % (need_sudo, need_sudo, file_name)
    else:
        cmd = "gem uninstall -ax rhc ; gem install %s" % (file_name)
    (status, output) = cmd_get_status_output(cmd)
    if status == 0:
        log.info("rhc client gem file %s successfully installed" % (file_name))
    else:
        log.info(output)
    return status

def _yum_install_rhc_client_file(file_name):
    global need_sudo
    cmd = "%s yum remove -y rhc ; %s yum localinstall -y %s" % (need_sudo, need_sudo, file_name)
    (status, output) = cmd_get_status_output(cmd)
    if status == 0:
        log.info("rhc client rpm file %s successfully installed" % (file_name))
    else:
        log.info(output)
    return status


def _yum_install_rhc_client_from_repo():
    global need_sudo
    cmd = "rpm -q rhc && %s yum update -y rhc || %s yum install -y rhc" % (need_sudo, need_sudo)
    (status, output) = cmd_get_status_output(cmd)
    if status == 0:
        log.info("rhc client is successfully installed")
    else:
        log.info(output)
    return status

def get_current_rhc_version():
    cmd = "rhc --version"
    (status, output) = cmd_get_status_output(cmd)
    if status == 0:
        match = re.search(r'(?<=rhc )[\d\.]+', output)
        if match:
            return match.group(0)
        else:
            log.error("Failed to get the current version of rhc client in the output")
            log.error(output)
            return None
    else:
        log.info("rhc client isn't installed")
        return None

def get_latest_rhc_release(branch):
    method = CONFIG[detect_os()]
    log.info("Finding latest client version from %s..."%(branch))
    url = BASE_REPO_HOST + URL[method][branch]
    cmd = 'curl -3 --retry 3 -f -# -k --cert %s --key %s %s'%(CERT, KEY, url)
    (status, output) = cmd_get_status_output(cmd, quiet=True)
    if status!=0:
        raise Exception("Unable to get the list of rhc: %s"%output)
    latest_version = [0,0,0]
    pattern = re.compile(r'(?<=<a href=")rhc-(\d+)\.(\d+)\.(\d+).*?(\.gem|\.rpm)')
    for match in pattern.finditer(output):
        for i in range(3):
            if int(match.group(i+1)) > latest_version[i]:
                latest_version = [int(match.group(1)), int(match.group(2)), int(match.group(3))]
    if latest_version == [0,0,0]:
        raise Exception("Failed to get the latest version of rhc client")
    latest_version = map(str, latest_version)
    return '.'.join(latest_version)

def get_rhc_filename_by_release(release, branch):
    method = CONFIG[detect_os()]
    url = BASE_REPO_HOST + URL[method][branch]
    cmd = 'curl -3 --retry 3 -f -# -k --cert %s --key %s %s'%(CERT, KEY, url)
    (status, output) = cmd_get_status_output(cmd, quiet=True)
    if status!=0:
        raise Exception("Unable to get the list of rhc: %s"%output)
    if release == None:
        release = get_latest_rhc_release(branch)
    print release
    pattern = re.compile(r'(?<=<a href=")rhc-%s.*?(\.gem|\.rpm)' % (release))
    match = pattern.search(output)
    if match:
        return match.group(0)
    else:
        raise Exception("Failed to get rhc client file name")


def do_setup(release, branch, yum_install):
    log.info("release: %s, branch: %s" % (release, branch))
    current_version = get_current_rhc_version()
    if yum_install:
        return _yum_install_rhc_client_from_repo()

    if release == None:
        log.info("No rhc version specified. Going to use the latest one")
        target_version = get_latest_rhc_release(branch)
    else:
        target_version = release
    if current_version == target_version:
        log.info("The required rhc client %s has already been installed" % (target_version))
        return 0
    else:
        file_name = get_rhc_filename_by_release(target_version, branch)
        (status, file_path) = fetch_rhc_client_file(file_name, branch)
        if status != 0:
            raise Exception("Failed to fetch rhc file. Version: %s" % (target_version))
        else:
            install_rhc_client_file(file_path)
        return 0
