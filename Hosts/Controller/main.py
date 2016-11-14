
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
        if topic == "exceptions":
            ex.setException(msg[1])
            stopAll() # because we can't call it too many times
    except Exception as e:
        print "exception in network_message_handler", e

class Ex():
    def __init__(self):
        self.exceptions = Queue.Queue(0)
        self.ref = lambda: True
    def setException(self, ex):
        print "Motions Exception:", ex
        self.exceptions.put(ex)
        self.ref()

    def setExceptionAction(self, ref):
        self.ref = ref

    def checkNoException(self):
        return self.exceptions.empty()

ex = Ex()

class Motion():
    def __init__(self, motion_name):
        self.motion_name = motion_name
        self.position = -1
    def get_abs_position(self):
        outgoingmessagespool.addMessage(self.motion_name, "get_abs_position", [])
    def store_abs_position(self, position):
        self.position = position
    def zero_abs_position(self):
        outgoingmessagespool.addMessage(self.motion_name, "zero_abs_position", [])
    def expand(self, end_pos, speed):
        outgoingmessagespool.addMessage(self.motion_name, "expand", [end_pos, speed])
    def contract(self, end_pos, speed):
        outgoingmessagespool.addMessage(self.motion_name,  "contract", [end_pos, speed])
    def stop(self):
        print "stop", self.motion_name
        outgoingmessagespool.addMessage(self.motion_name, ["stop", [end_pos, speed]])

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
        motions["LotusFigure"].expand(0, 3)
        #time.sleep(1)
        #motions["WoodenLeg"].expand(0, 100)
        #time.sleep(1)
        motions["RuffleLeg"].expand(0, 100)
        time.sleep(1)
        motions["Lantern"].expand(-4000, 100)
        time.sleep(1)
        motions["Bathmat"].expand(9000, 100)
        time.sleep(1)

        time.sleep(20)

    def contract(self):
        motions["LotusFigure"].contract(0, -3)  
        #time.sleep(1)
        motions["Bathmat"].expand(-9000, 100)
        time.sleep(1)
        motions["Lantern"].contract(6000, 0)
        time.sleep(1)
        #motions["HairSticks"].contract(20000, 0)
        #time.sleep(1)
        motions["RuffleLeg"].contract(35000, 100)
        time.sleep(1)
        #motions["WoodenLeg"].contract(20000, 100)
        #time.sleep(1)
        motions["LotusFigure"].contract(0, 0)
        time.sleep(15)

    def run(self):
        while True:
            self.expand()
            time.sleep(5)
            self.contract()
            time.sleep(5)

network = None

class OutgoingMessageSpool(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.msgQueue = Queue.Queue()
        self.frequency = 1.0
    def addMessage(self,destination,cmd,params):
        self.msgQueue.put([destination,cmd,params])
    def run(self):
        while True:
            if ex.checkNoException():
                while not self.msgQueue.empty():
                    destination,cmd,params = self.msgQueue.get()
                    #print "OutgoingMessageSpool 1", destination, cmd, params
                    network.send(destination, [cmd, params])
                for motion_name in motion_names:
                    #print "OutgoingMessageSpool 2", motion_name
                    network.send(motion_name, ["deadman", [True]])
                time.sleep(self.frequency)
            else:
                for motion_name in motion_names:
                    #print "OutgoingMessageSpool 3", motion_name
                    network.send(motion_name, ["deadman", [False]])

outgoingmessagespool = OutgoingMessageSpool()

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

    animator = Animator()
    animator.start()
    outgoingmessagespool.run()
