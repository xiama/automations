from helper import *
from misc import *


def add_application_template(template_tag, descriptor):
    """
    This function copies the application template file (in yaml format) to the broker server
    and adds with the appropriate oo-admin command.
    """

    template_file_name = "%s/%s.yaml" % (get_tmp_dir(), template_tag)
    template_file = open(template_file_name, "w")
    for line in descriptor.splitlines():
        template_file.write(line + "\n")
    template_file.close()

    command_get_status(
        "scp  -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no 2>/dev/null -i %s %s root@%s:/tmp" % ( get_root_ssh_key(), template_file_name, get_instance_ip())
    )

    return run_remote_cmd_as_root( "oo-admin-ctl-template -c add -n %s -d %s -g git://github.com/openshift/wordpress-example.git -t wordpress  --cost 1  -m '{ \"a\" : \"b\" }'" % ( template_tag, template_file_name ))[0]


def get_consumed_gears(user=None):
    """
    This functions returns the consumed_gears of the given user.
        * if the user is None => REST API (/user) for current user
        * else we use `oo-admin-ctl-user -l $user` to get this value
        * if error, returns None
    """
    if user != None:
        #as root#
        (status, output) = run_remote_cmd_as_root("oo-admin-ctl-user -l %s"%user)
        if status == 0:
            obj = re.search(r"consumed gears:\s+(\d+)", output)
            if obj:
                return int(obj.group(1))
            else:
                print "ERROR: Unable to parse the max_gears for %s from oo-admin-ctl-user output."%user
                print output
                return None
        else:
            print "ERROR: Unable to get the number of max_gears per %s."%user
            print output
            return None
    else:
        #as user from REST API
        (user, passwd) = get_default_rhlogin()
        rest = openshift.Openshift(host=get_instance_ip(), user=user, passwd=passwd)
        (status, raw) = rest.get_user()
        if status == 'OK':
            return int(rest.rest.response.json['data']['consumed_gears'])
        else:
            print "ERROR: %s,%s"%(status, raw)
            return None


def get_max_gears(user=None):
    """
    This functions returns the max_gears of the given user.
        * if the user is None => REST API (/user) for current user
        * else we use `oo-admin-ctl-user -l $user` to get this value
        * if error, returns None
    """
    if user != None:
        #as root#
        (status, output) = run_remote_cmd_as_root("oo-admin-ctl-user -l %s"%user)
        if status == 0:
            obj = re.search(r"max gears:\s+(\d+)", output)
            if obj:
                return int(obj.group(1))
            else:
                print "ERROR: Unable to parse the max_gears for %s from oo-admin-ctl-user output."%user
                print output
                return None
        else:
            print "ERROR: Unable to get the number of max_gears per %s."%user
            print output
            return None
    else:
        #as user from REST API
        rest = openshift.Openshift(host=get_instance_ip(), 
                                 user=os.getenv("OPENSHIFT_user_email"), 
                                 passwd=os.getenv("OPENSHIFT_user_passwd"))
        (status, raw) = rest.get_user()
        if status == 'OK':
            return int(rest.rest.response.json['data']['max_gears'])
        else:
            print "ERROR: %s,%s"%(status, raw)
            return None


def set_max_gears(user=None, max_gears=3):
    """
    This functions configures the maximum number of gears the given
    user can consume.
    """
    if user is None:
        (user, passwd) = get_default_rhlogin()
    return run_remote_cmd_as_root(
        "oo-admin-ctl-user -l %s --setmaxgears %d" % ( user, int(max_gears) )
    )[0]


def set_user_capability(capability, value="", user=None):
    """
    addgearsize [small, medium, ...]
    removegearsize [small, medium, ...]
    allowsubaccounts [true, false]
    inheritgearsizes [true, false]
    ...
    ...more from: oo-admin-ctl-user --help
    ...
    """
    if user is None:
        (user, passwd) = get_default_rhlogin()
    cmd = "oo-admin-ctl-user -l %s --%s %s"%(user, capability, value)
    return run_remote_cmd_as_root(cmd)[0]


def remove_gearsize_capability(gearsize, user=None):
    if user is None:
        (user, passwd) = get_default_rhlogin()
    return set_user_capability('removegearsize', gearsize, user)


def add_gearsize_capability(gearsize, user=None):
    if user is None:
        (user, passwd) = get_default_rhlogin()
    return set_user_capability('addgearsize', gearsize, user)


def get_nodes():
    """
    Returns a list of nodes running within broker
    When error, returns None
    """
    (ret, output) = run_remote_cmd_as_root("mco ping", quiet=True)
    if ret != 0:
        print "ERROR:", output
        return None

    nodes=[]
    for line in output.split('\n'):
        obj = re.search(r"^([^\s]+)\s+time=", line)
        if obj:
            nodes.append(obj.group(1))

    return nodes


def destroy_district(district):
    cmd = "oo-admin-ctl-district -c destroy -n %s"%(district)
    return run_remote_cmd_as_root(cmd)


def create_district(district):
    cmd = "oo-admin-ctl-district -c create -n %s"%(district)
    return run_remote_cmd_as_root(cmd)


def add_node2district(district, hostname):
    cmd = "oo-admin-ctl-district -c add-node -n %s -i %s"%(district, hostname)
    return run_remote_cmd_as_root(cmd)[0]


def get_gears_per_node(node=None):
    """
    Returns a list of the gears which reside on particular node
    """
    (ret, output) = run_remote_cmd_as_root("ls -l /var/lib/openshift/", node)
    if (ret != 0):
        print "ERROR getting list of gears from node."
        return None
    l = {}
    for line in output.split('\n'):
        obj = re.search(r"^d.*\s+([^\s]+)$", line)
        if obj:
            l[obj.group(1)] = None
            continue
        obj = re.search(r"^l.*\s+([^\s]+)\s+->\s+([^\s]+)$", line)


def move_gear_between_nodes(gear_uuid, node_identity):
    cmd ="oo-admin-move --gear_uuid %s --target_server_identity %s "%(gear_uuid, node_identity)
    (ret, output) = run_remote_cmd_as_root2(cmd)
    if ret != 0:
        log.error(output)

    return ret


def get_districts():
    '''
    cmd = "oo-admin-ctl-district"
    (status, output) = run_remote_cmd_as_root2(cmd)
    print output
    return ruby_hash2python(output)
    '''
    from brokerdb import BrokerDB
    db = BrokerDB(collections='district')
    try:
        c = db.get_collection('district')
        if c is None:
            log.error("Problem getting collection of districts -> None")
            return []
    except Exception as e:
        log.error(str(e))
        return []

def get_district_of_node(server_identity):
    """
    Returns district name of given node's server_identity
    """
    for ds in get_districts():
        for si in ds['server_identities']:
            if si['name'] == server_identity:
                return ds['name']
    return []


def get_users():
    from brokerdb import BrokerDB
    db = BrokerDB(collections='user')
    return db.get_collection('user')


def get_district_of_gear(gear_uuid):
    #1. get districts
    districts = get_districts()
    for d in districts:
        for si in d['server_identities']:
            node = si['name']
            p_node = get_public_ip(node)
            for g in get_gears_of_node(p_node).keys():
                if g == gear_uuid:
                    return d['name']
    return None


def get_multi_node_env_setup():
    """
    Returns dict of multi node current setup environment
    """
    setup_file =get_msetup_file()
    if valid_cache(setup_file):
        f = open(setup_file, 'r')
        setup = pickle.load(f)
        f.close()
        return setup
    else:
        return setup_multi_node_env()


#@exclusive
def setup_multi_node_env(district_name=None, force_cache=False):
    """
    Adding all nodes to given district if not already have been assigned.
    Returns: 
        {'nodes': [n1, n2,..], 
         'district': [{d1},...], 
         'user': [{user1},...]}
    Saves/uses dump in ~/tmp/msetup.openshift for 6hours
    """
    log.info("Not yet fully tested/supported")
    return None
    msetup_file = "%s/msetup.openshift"%get_tmp_dir()
    if district_name is None:
        district_name = getRandomString(10)
    try:
        if valid_cache(msetup_file) and not force_cache:
            f = open(msetup_file, 'rb')
            msetup = pickle.load(f)
            f.close()
            return msetup
    except Exception as e:
        log.error("Unable to read from (corrupted?) cache file %s: %s"%(msetup_file, str(e)))
        if os.path.exists(msetup_file):
            os.unlink(msetup_file)

    nodes = get_nodes()
    for n in nodes :  #got private IP addresses from `mco ping` 
        ds = get_district_of_node(n)
        if ds is None:
            create_district(district_name)
            log.debug("Adding nodes to a district")
            ret = add_node2district(district_name, n)
            if ret != 0:
                log.error("Unable to add a node[%s] to the district[%s]."%(n, district_name))
        else:
            log.info("Node[%s] already belongs to district[%s]"%(n, ds))

    from brokerdb import BrokerDB
    broker = BrokerDB()
    msetup = {'nodes': nodes, 
              'district': broker.get_collection('district'), 
              'user': broker.get_collection('users')}

    #Save file for later usage as cache
    if not os.path.exists(msetup_file) or not valid_cache(msetup_file) or force_cache:
        try:
            log.debug("Saving msetup file...")
            oldumask = os.umask(0000)
            f = open(msetup_file, 'wb')
            pickle.dump(msetup, f)
            f.close()
            os.umask(oldumask)
        except Exception as e:
            log.error(e)
    return msetup


def get_msetup_file():
    return "%s/msetup.openshift"%get_tmp_dir()

