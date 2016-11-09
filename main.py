"""
Logs
    how to set log levels with decorator?
        pass loglevel var to each module?
        set dynamic value via import?
    use logging module



perhaps go back to passing logging function to other modules
use Queue object to make thread safe
create non-trace decorator for efficiency
how to collect data from other devices?
    all devices send log data to the server

new optional command-line args
    nodename= (overrides local hostname)
    loglevel=trace  ( default is no trace)
    dashboard=true (add role of collecting logs)

internal data formats:
    topic (single word) - defines a flow/shape of data, not its function
    address (path, possibly RESTful) - represents not a final address within the software, but an ontology in the data
    data (hash type) - the payload data

    does the action

topic patterns: 
    server-to-host, 
    server_broadcast, 
    dashboard

address examples /


system commands:
    change log level
    restart
    force upgrade ( restart )

NEXT:
    pass HOSTNAME through to all modules b/c name may be overridden
    pass reference to ExceptionCollector through to all
        set up exception networking after init
"""

#########################################
######## IMPORTS, PATHS, GLOBALS ########
#########################################

import importlib
import json
import os
import settings 
import sys
import threading
import time
import yaml

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
UPPER_PATH = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
DEVICES_PATH = "%s/Hosts/" % (BASE_PATH )
THIRTYBIRDS_PATH = "%s/thirtybirds" % (UPPER_PATH )

PAUSE_UNTIL_ONLINE_MAX_SECONDS = 30

sys.path.append(BASE_PATH)
sys.path.append(UPPER_PATH)

args = sys.argv[1:]

try:
    pos = args.index("-l")
    LOG_LEVEL = args[pos+1]
    assert LOG_LEVEL in ["trace","info","quiet","silent"]
except Exception as E:
    LOG_LEVEL = "quiet"

try:
    pos = args.index("-u")
    au = args[pos+1]
    assert au in ["true","True"]
    AUTO_UPDATE = True 
except Exception as E:
    AUTO_UPDATE = False

HOSTNAMES = filter(lambda x: os.path.isdir(os.path.join(DEVICES_PATH, x)), os.listdir(DEVICES_PATH))

from thirtybirds.Network.info import init as network_info_init
network_info = network_info_init()

def pauseUntilOnline(max_seconds):
    for x in range(max_seconds):
        if network_info.getOnlineStatus():
            print "got connection!"
            break
        else:
            print "waiting for connection..."
            time.sleep(1)

pauseUntilOnline(PAUSE_UNTIL_ONLINE_MAX_SECONDS)

if AUTO_UPDATE:
    from thirtybirds.Updates.manager import init as updates_init
    updates_init(BASE_PATH, True, True)
    updates_init(THIRTYBIRDS_PATH, True, True)

try:
    pos = args.index("-n") # pull hostname from command line argument, if there is one
    HOSTNAME = args[pos+1]
except Exception as E:
    HOSTNAME = network_info.getHostName() 

host = importlib.import_module("Hosts.%s.main" % (HOSTNAME))
host.init(HOSTNAME)

