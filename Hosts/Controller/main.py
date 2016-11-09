
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
        action, params = yaml.safe_load(msg[1])
        # print "Exception Received:", ex
    except Exception as e:
        print "exception in network_message_handler", e

class Ex():
    def __init__(self):
        self.exceptions = Queue.Queue(0)
        self.ref = lambda: True
    def setException(self, ex):
        print "Motions Exception:", ex
        self.exceptions.queue.put(ex)
        self.ref()

    def setExceptionAction(self, ref):
        self.ref = ref

    def checkException(self):
        return False if self.exceptions.queue.qsize() == 0 else True

ex = Ex()

class Motion():
    def __init__(self, motion_name):
        self.motion_name = motion_name
        self.channel = channel
        self.position = -1
    def get_abs_position(self):
        network.send(self.motion_name, ["get_abs_position", []])
    def store_abs_position(self, position):
        self.position = position
    def zero_abs_position(self):
        network.send(self.motion_name, ["zero_abs_position", []])
    def expand(self, end_pos, speed):
        if ex.checkException():
            self.stop()
        else:
            network.send(self.motion_name, ["expand", [end_pos, speed]])
    def contract(self, end_pos, speed):
        if ex.checkException():
            self.stop()
        else:
            network.send(self.motion_name, ["contract", [end_pos, speed]])
    def stop(self):
        network.send(self.motion_name, ["stop", []])

motion_names = ["Bathmat","Eyeballs","Lantern","HairSticks","LotusFigure","RuffleLeg","GeoSkirt","WoodenLeg","BirdNest"]
motions = {}
for motion_name in motion_names:
    motions[motion_name] = Motion(motion_name)

def stopAll():
    for motion_name in motion_names:
        motions[motion_name].stop()

ex.setExceptionAction(stopAll)

class Animator(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.animations = {
            "safe_expand":[],
            "expand":[
            ],
            "contract":[
            ]
        }
    def expand(self):
        motions["LotusFigure"].expand(0, 100)
        time.sleep(1)
        motions["Eyeballs"].expand(0, 100)
        time.sleep(1)
        motions["WoodenLeg"].expand(0, 100)
        time.sleep(1)
        motions["RuffleLeg"].expand(0, 100)
        time.sleep(1)
        motions["GeoSkirt"].expand(0, 100)
        time.sleep(1)
        motions["HairSticks"].expand(0, 100)
        time.sleep(1)
        motions["Lantern"].expand(0, 100)
        time.sleep(1)
        motions["Bathmat"].expand(0, 100)
        time.sleep(1)
        motions["BirdNest"].expand(0, 100)
        time.sleep(1)

    def contract(self):
        motions["LotusFigure"].contract(2000, 100)
        time.sleep(1)
        motions["BirdNest"].contract(2000, 100)
        time.sleep(1)
        motions["Bathmat"].contract(2000, 100)
        time.sleep(1)
        motions["Lantern"].contract(2000, 100)
        time.sleep(1)
        motions["HairSticks"].contract(2000, 100)
        time.sleep(1)
        motions["GeoSkirt"].contract(2000, 100)
        time.sleep(1)
        motions["RuffleLeg"].contract(2000, 100)
        time.sleep(1)
        motions["WoodenLeg"].contract(2000, 100)
        time.sleep(1)        
        motions["Eyeballs"].contract(2000, 100)
        time.sleep(1)

    def run(self):
        while True:
            self.expand()
            time.sleep(5)
            self.contract()
            time.sleep(5)

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

