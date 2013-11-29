from consts import *
from misc import *
import OSConf
import re

def get_num_of_gears_by_web(app_name, app_type):
    """
        Calls /env.* page with all of the env variables
        and seeks for OPENSHIFT_GEAR_DNS occurence.
    """
    app_url = OSConf.get_app_url(app_name)
    url = app_url + "/env" + APP_SUFFIX[app_type.split('-')[0]]
    gears = list()
    #
    #we will seek for OPENSHIFT_GEAR_DNS
    #
    pattern = re.compile(r"^(OPENSHIFT_([\w\_]?)GEAR_DNS.*)$", re.MULTILINE)
    #pattern = re.compile(r"^(OPENSHIFT_GEAR_DNS.*)$", re.MULTILINE)
    for i in range(7):
        for i in range(3):
            page = fetch_page(url)
            obj = pattern.search(page)
            if obj:
                gear = obj.group(1)
                if gear not in gears:
                    log.info("GEAR: [%s]"%gear)
                    gears.append(gear)
        time.sleep(7)
    return len(gears)


