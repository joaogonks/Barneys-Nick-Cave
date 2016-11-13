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
        if topic == "RuffleLeg":
          action, params = yaml.safe_load(msg[1])

          position = params[0]
          if action == "expand":
            controller.moveTo(1, position)
          if action == "contract":
            controller.moveTo(1, position)
        if topic == "GeoSkirt":
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
    network.subscribe_to_topic("RuffleLeg")
    network.subscribe_to_topic("GeoSkirt")

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
        timeout=0
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
  """
  def setSpeed(self, channel, rpm):
    if self.open:
      cmd = '!G ' + str(channel) + ' '+str(rpm)+'\r'
      print cmd
      self.serial.write(cmd)
    else:
      print 'Serial not connected'
      pass
  """
  def moveTo(self, channel, position):
    print "moveTo=",channel, position
    self.cmdQueue.put([channel, position])
    """
    if channel == 1:
      self.destination1 = int(position)
    if channel == 2:
      self.destination2 = int(position)
      cmd = '!G ' + str(channel) + ' '+str(self.speed) + '\r'
      self.cmdQueue.put(cmd)
    """
  def run(self):
    while True:
      print 101
      # if is there a new moveTo command in the queue
      while not self.cmdQueue.empty():
        print 102
        channel, destinationPosition = self.cmdQueue.get()
        # read current positions
        cmd = '?C' + '\r'
        # write to serial
        self.serial.write(cmd)
        # read resp from serial
        positions_raw = self.serial.readline()
        print "positions_raw=",positions_raw
        #positions_raw = self.serialDialog(cmd)
        measuredPosition1, measuredPosition2 = positions_raw.split('=')[1].split(':')
        if channel == 1:
          print 103
          # set destinations
          self.destinationPosition1 = destinationPosition
          # calculate direction and save
          self.direction1 = 1 if measuredPosition1 < self.destinationPosition1 else -1
          speed = int(self.direction1 * 30)
          # generate serial command
          cmd = '!G ' + str(channel) + ' '+str(speed) + '\r'
          # write to serial
          self.serial.write(cmd)
          # read resp from serial
          resp = self.serial.readline()
          print "resp=",resp
        if channel == 2:
          print 104
          # set destinations
          self.destinationPosition1 = destinationPosition
          # calculate direction and save
          self.direction1 = 1 if measuredPosition2 < self.destinationPosition2 else -1
          speed = int(self.direction1 * 30)
          # generate serial command
          cmd = '!G ' + str(channel) + ' '+str(speed) + '\r'
          # write to serial
          self.serial.write(cmd)
          # read resp from serial
          resp = self.serial.readline()
          print "resp=",resp
      print 106
      # read current positions
      cmd = '?C' + '\r'
      print 107
      # write to serial
      self.serial.write(cmd)
      print 108
      # read resp from serial
      positions_raw = self.serial.readline()
      print 109
      print "positions_raw=",positions_raw
      measuredPosition1, measuredPosition2 = positions_raw.split('=')[1].split(':')
      # channel 1
      # if encoder is past/near destination
      if self.direction1 == 1:
        if measuredPosition1 > self.destinationPosition1:
          print "channel 1 endpoint, direction 1", measuredPosition1, self.destinationPosition1
          # send new speed of 0
          cmd = '!G ' + str(1) + ' '+str(0) + '\r'
          # write to serial
          self.serial.write(cmd)
          # read resp from serial
          resp = self.serial.readline()
          print "resp=",resp
      if self.direction1 == -1:
        if measuredPosition1 < self.destinationPosition1:
          print "channel 1 endpoint, direction -1", measuredPosition1, self.destinationPosition1
          # send new speed of 0
          cmd = '!G ' + str(1) + ' '+str(0) + '\r'
          # write to serial
          self.serial.write(cmd)
          # read resp from serial
          resp = self.serial.readline()
          print "resp=",resp

      # channel 2
      # if encoder is past/near destination
      if self.direction2 == 1:
        if measuredPosition2 > self.destinationPosition2:
          print "channel 2 endpoint, direction 1", measuredPosition1, self.destinationPosition1
          # send new speed of 0
          cmd = '!G ' + str(2) + ' '+str(0) + '\r'
          # write to serial
          self.serial.write(cmd)
          # read resp from serial
          resp = self.serial.readline()
          print "resp=",resp
      if self.direction2 == -1:
        if measuredPosition2 < self.destinationPosition2:
          print "channel 1 endpoint, direction -1", measuredPosition2, self.destinationPosition2
          # send new speed of 0
          cmd = '!G ' + str(2) + ' '+str(0) + '\r'
          # write to serial
          self.serial.write(cmd)
          # read resp from serial
          resp = self.serial.readline()
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