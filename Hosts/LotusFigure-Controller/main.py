###

controller ideas

frames, like an animation

init: 
    read abs positions of all arms
    ? how to move safely into positions ?
        which arms conflict?

loop:
    contract:
        eyeball
        -pause-
        wooden leg
        -pause-
        ruffle leg
        -pause-
        geometric skirt
        -pause-
        hair sticks
        -pause-
        lantern
        -pause-
        bathmat
        -pause-
        birdnest
        -pause-

    expand:
        birdnest
        -pause-
        bathmat
        -pause-
        lantern
        -pause-
        hair sticks
        -pause-
        geometric skirt
        -pause-
        ruffle leg
        -pause-
        wooden leg
        -pause-
        eyeball
        -pause-

what do network commands look like?
    /hostname/arm/action

    actions:
        expand
        contract
        exception
        getPosition
            once?
            always check for safety?

how to lock down safety?
    exception catching is nimble
    lock all motors on fault states

###


"""
server      

incubator

"""


import time
import threading
import settings
import yaml
import json

from thirtybirds.Logs.main import Exception_Collector
from thirtybirds.Network.manager import init as network_init
            

def network_status_handler(msg):
    print "network_status_handler", msg

def network_message_handler(msg):
    try:
        #print "network_message_handler", msg
        topic = msg[0]
        host, sensor, data = yaml.safe_load(msg[1])
    except Exception as e:
        print "exception in network_message_handler", e

motions = {
}

network = None

def init(HOSTNAME):
    global network
    network = network_init(
        hostname=HOSTNAME,
        role="server",
        discovery_multicastGroup=settings.discovery_multicastGroup,
        discovery_multicastPort=settings.discovery_multicastPort,
        discovery_responsePort=settings.discovery_responsePort,
        pubsub_pubPort=settings.pubsub_pubPort,
        message_callback=network_message_handler,
        status_callback=network_status_handler
    )

    network.subscribe_to_topic("system")  # subscribe to all system messages
    network.subscribe_to_topic("motion_commands")
    network.subscribe_to_topic("exceptions")
    
