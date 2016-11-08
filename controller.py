
import commands
import serial
import sys
import threading
import time

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


