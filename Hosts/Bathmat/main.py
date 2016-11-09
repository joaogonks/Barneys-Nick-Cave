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
        host, sensor, data = yaml.safe_load(msg[1])
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
    network.subscribe_to_topic("Bathmat")

######## MOTOR CONTROL ##########

class Controller():
  def __init__(self, deviceId=0):
    self.deviceId = deviceId
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
      )
      #self.serial.open()
      self.open = True
      print "Serial connected at ", self.devicePath
    except:
      self.open = False
      print("could not open device at ", self.devicePath)

  def setSpeed(self, channel, rpm): 
    if self.open:
      cmd = '!G ' + str(channel) + ' '+str(rpm)+'\r'
      print cmd
      self.serial.write(cmd)
    else:
      print 'Serial not connected'
      pass

controller = Controller()

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


