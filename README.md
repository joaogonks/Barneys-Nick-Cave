# Barneys-Nick-Cave

+ spi.py
 - Example:
 <br> import spi
 <br> spi.amt.set_zero()
 <br> spi.amt.get_position()
 
 - amt.set_zero()
 <br> Prints "Zero set was successful and the new position offset is stored in EEPROM"
 <br> if successful.
 <br> Note:
 <br>Method uses a GPIO pin to reset the encoder.
 <br>Maximum current for GPIO pin is 16mA.
 
  - amt.get_position()
  <br>Prints and returns a number from 0-4095 corresponding to the position.
