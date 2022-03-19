import smbus
import math

class TempSensor():
    """ Temperature sensor class
    """
    def __init__(self):
        self.cmd = 0x84
        self.address = 0x4b # 0x4b is the default i2c address for ADS7830 Module.
        self.bus=smbus.SMBus(1)

    def _analog_read(self, chn): # ADS7830 has 8 ADC input pins, chn:0,1,2,3,4,5,6,7
        """ Read value from ADC.

        Arguments:
            chn: The ADC pin to read.
        Returns:
            The value at the ADC pin.
        """
        return self.bus.read_byte_data(self.address, self.cmd|(((chn<<2 | chn>>1)&0x07)<<4))
        
    def get_temp(self):
        """ Get temperature from the temperature sensor.

        Returns:
            Temperature in degrees Celsius.
        """
        value = self._analog_read(0) # read ADC value A0 pin
        voltage = value / 255.0 * 3.3 # calculate voltage
        Rt = 10 * voltage / (3.3 - voltage) # calculate resistance value of thermistor
        tempK = 1/(1/(273.15 + 25) + math.log(Rt/10)/3950.0) # calculate temperature (Kelvin)
        return tempK -273.15 # calculate temperature (Celsius)
            
    def close(self):
        self.bus.close()
