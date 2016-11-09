###

controller ideas

frames, like an animation

init: 
    read abs positions of all arms
    ? how to move safely into positions ?
        which arms conflict?

loop:
    expand:
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

    contract:
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

import json
import Queue
import settings
import time
import threading
import yaml

#from thirtybirds.Logs.main import Exception_Collector
from thirtybirds.Network.manager import init as network_init

def network_status_handler(msg):
    print "network_status_handler", msg

def network_message_handler(msg):
    try:
        #print "network_message_handler", msg
        topic = msg[0]
        host, sensor, data = yaml.safe_load(msg[1])
        # print "Exception Received:", ex
    except Exception as e:
        print "exception in network_message_handler", e


class Controller():
    def __init__(self, host, channel):
        self.host = host
        self.channel = channel
        self.position = -1
    def get_abs_position(self):
        pass
    def store   _abs_position(self):
        pass
    def zero_abs_position(self):
        pass
    def expand(self, speed, end_pos):
        # check 
        pass
    def contract(self, speed, end_pos):
        pass



controllers = {
    "Bathmat":Controller(,),
    "Eyeballs":Controller(,),
    "Lantern":Controller(,),
    "HairSticks":Controller(,),
    "LotusFigure":Controller(,),
    "RuffleLeg":Controller(,),
    "GeoSkirt":Controller(,),
    "WoodenLeg":Controller(,),
    "BirdNest":Controller(,)
}


newList = map(method, objectList)

class Animator(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.exceptions = Queue.Queue(0)

    def setException(self, ex):

        self.exceptions.queue.put(ex)

    def run(self):
        while self.exceptions.queue.qsize == 0:





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
    network.subscribe_to_topic("exceptions")
    network.subscribe_to_topic("Bathmat")
    network.subscribe_to_topic("Eyeballs")
    network.subscribe_to_topic("Lantern")
    network.subscribe_to_topic("HairSticks")
    network.subscribe_to_topic("LotusFigure")
    network.subscribe_to_topic("RuffleLeg")
    network.subscribe_to_topic("GeoSkirt")
    network.subscribe_to_topic("WoodenLeg")
    network.subscribe_to_topic("BirdNest")

