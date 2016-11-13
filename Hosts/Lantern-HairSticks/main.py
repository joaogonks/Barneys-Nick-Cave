import json
import Queue
import settings
import time
import threading
import yaml
import commands
import serial
import sys
import spidev
import RPi.GPIO as GPIO

#from thirtybirds.Logs.main import Exception_Collector
from thirtybirds.Network.manager import init as network_init

def network_status_handler(msg):
    print "network_status_handler", msg

def network_message_handler(msg):
    try:
        #print "network_message_handler", msg
        topic = msg[0]
        if topic == "HairSticks":
          action, params = yaml.safe_load(msg[1])

          position = params[0]
          if action == "expand":
            controller.moveTo(1, position)
          if action == "contract":
            controller.moveTo(1, position)
        if topic == "Lantern":
          action, params = yaml.safe_load(msg[1])
          position = params[0]
          if action == "expand":
            controller.moveTo(2, position)
          if action == "contract":
            controller.moveTo(2, position)

          # print "Exception Received:", ex
    except Exception as e:
        print "exception in network_message_handler", e
network = None

def init(HOSTNAME):
    global network
    network = network_init(
        hostname=HOSTNAME,
        role="client",
        discovery_multicastGroup=settings.discovery_multicastGroup,
        discovery_multicastPort=settings.discovery_multicastPort,
        discovery_responsePort=settings.discovery_responsePort,
        pubsub_pubPort=settings.pubsub_pubPort,
        message_callback=network_message_handler,
        status_callback=network_status_handler
    )

    network.subscribe_to_topic("system")  # subscribe to all system messages
    network.subscribe_to_topic("exceptions")
    network.subscribe_to_topic("Lantern")
    network.subscribe_to_topic("HairSticks")

######## MOTOR CONTROL ##########

class Controller(threading.Thread):
  def __init__(self, deviceId=0):
    threading.Thread.__init__(self)
    self.deviceId = deviceId
    self.cmdQueue = Queue.Queue()
    self.open = False
    self.devicePath = "/dev/ttyUSB" + str(deviceId)
    try:
      self.serial = serial.Serial(
        port=self.devicePath,
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        #startbits=serial.STARTBITS_ONE,
        stopbits=serial.STOPBITS_ONE,
        parity=serial.PARITY_NONE,
        timeout=1
      )
      #self.serial.open()
      self.open = True
      self.destinationPosition1 = 0
      self.destinationPosition2 = 0
      self.direction1 = 1
      self.direction2 = 1
      self.speed = 30
      print "Serial connected at ", self.devicePath
    except:
      self.open = False
      print("could not open device at ", self.devicePath)
  
  def serialDialog(self, msg):
    if self.open:
      #print "serialDialog msg=", msg
      self.serial.flush()
      self.serial.write(msg)
      self.serial.flush()
      resp = self.serial.readline()
      #print "serialDialog response:" 
      return resp
    else:
      print 'Serial not connected'
      return ""
  
  def moveTo(self, channel, position):
    print "moveTo=",channel, position
    self.cmdQueue.put([channel, position])

  def outOfBounds(self, measuered, destination, direction):
    print "BOUNDS === ", repr(measuered), repr(destination), repr(direction)
    if direction == -1:
      return measuered >= destination
    if direction == 1:
      return measuered <= destination

  def run(self):
    while True:
      while not self.cmdQueue.empty():
        channel, destinationPosition = self.cmdQueue.get()
        cmd = '?C' + '\r'
        positions_raw = self.serialDialog(cmd)
        print "positions_raw=",positions_raw
        measuredPosition1, measuredPosition2 = positions_raw.split('=')[1].split(':')
        if channel == 1:
          self.destinationPosition1 = destinationPosition
          self.direction1 = 1 if measuredPosition1 > self.destinationPosition1 else -1
          print "channel 1 direction", self.direction1, measuredPosition1, self.destinationPosition1 
          if self.outOfBounds(measuredPosition1, self.destinationPosition1, self.direction1):
            cmd = '!G ' + str(channel) + ' '+str(0) + '\r'
          else:
            speed = int(self.direction1 * 15)
            cmd = '!G ' + str(channel) + ' '+str(speed) + '\r'
          resp = self.serialDialog(cmd)
        print cmd
        if channel == 2:
          self.destinationPosition2 = destinationPosition
          self.direction2 = 1 if measuredPosition2 > self.destinationPosition2 else -1
          print "channel 2 direction", self.direction2, measuredPosition2, self.destinationPosition2
          if self.outOfBounds(measuredPosition2, self.destinationPosition2, self.direction2):
            cmd = '!G ' + str(channel) + ' '+str(0) + '\r'
          else:
            speed = int(self.direction2 * 30)
            cmd = '!G ' + str(channel) + ' '+str(speed) + '\r'
          print cmd
          resp = self.serialDialog(cmd)
      cmd = '?C' + '\r'
      positions_raw = self.serialDialog(cmd)
      measuredPosition1, measuredPosition2 = positions_raw.split('=')[1].split(':')
      print measuredPosition1, measuredPosition2
      if self.outOfBounds(measuredPosition1, self.destinationPosition1, self.direction1):
        print "channel 1 out of bounds",measuredPosition1, self.destinationPosition1, self.direction1
        cmd = '!G ' + str(1) + ' '+str(0) + '\r'
        resp = self.serialDialog(cmd)
        print "resp=",resp

      if self.outOfBounds(measuredPosition2, self.destinationPosition2, self.direction2):
        print "channel 2 out of bounds",measuredPosition2, self.destinationPosition2, self.direction2
        cmd = '!G ' + str(2) + ' '+str(0) + '\r'
        resp = self.serialDialog(cmd)
        print "resp=",resp

      time.sleep(0.05)

        # read any fault states
          # channel 1
            # if fault state
              # send new speed of 0
          # channel 2
            # if fault state
              # send new speed of 0


        
    # read positions









controller = Controller()
controller.start()

######## ABSOLUTE ENCODER ###########

class AMT203():
  def __init__(self, bus=0, deviceId=0, pin=3):
    self.deviceId = deviceId
    self.bus = bus
    self.pin = pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.pin, GPIO.OUT)
    GPIO.output(self.pin, GPIO.HIGH)
    try:
      self.spi = spidev.SpiDev()
      self.spi.open(self.bus,self.deviceId)
      self.open = True
      print "SPI connected. Device id: ", self.deviceId
    except:
      self.open = False
      print "Could not connect to SPI device"

  def clean_buffer(self):
    first_result = self.spi.xfer([0x00],0,20)
    while first_result[0] != 165:
      first_result = self.spi.xfer([0x00],0,20)
    print "Buffer empty"


  def get_position(self):
    first_result = self.spi.xfer([0x10],0,20)
    while first_result[0] != 16:
      first_result = self.spi.xfer([0x00],0,20)
    msb_result = self.spi.xfer([0x00],0,20)
    lsb_result = self.spi.xfer([0x00],0,20)
    print "MSB: %s | LSB: %s " % (msb_result, lsb_result)
    # msb_bin = bin(msb_result[0]<<8)[2:]
    # lsb_bin = bin(lsb_result[0])[2:]
    final_result = (msb_result[0]<<8 | lsb_result[0])
    print "Final: ", final_result
    self.clean_buffer()

  def set_zero(self):
    first_result = self.spi.xfer([0x70],0,20)
    while first_result[0] != 128:
      first_result = self.spi.xfer([0x00],0,20)
    print "Zero set was successful and the new position offset is stored in EEPROM"
    self.clean_buffer()
    GPIO.output(self.pin, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(self.pin, GPIO.HIGH)


amt = AMT203()