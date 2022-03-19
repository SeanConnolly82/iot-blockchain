import time

import base_logger

from temp_sensor import TempSensor

LOGGER = base_logger.get_logger(__name__)


class Sensor():
    """ Creates an instance of an IoT sensor device object.
    """

    def __init__(self, device_id, device_type=None):
        self.payload = {
            'timestamp': None,
            'device_id': device_id,
            'device_type': device_type,
            'value': None
        }

    def get_values(self):
        """ Reads sensor values and updates sensor object.
        """
        self.payload['timestamp'] = self._get_timestamp()
        self.payload['value'] = self._get_reading()
        LOGGER.info('Sensor reading of {:.2f} for {} on device ID {} at {}'.format(self.payload['value'], self.payload['device_type'], self.payload['device_id'], time.strftime(
            "%a, %d %b %Y %H:%M:%S", time.localtime(self.payload['timestamp']))))

    def _get_reading(self):
        """ Get the sensor reading.
        
        Returns:
            Current sensor value.
        """
        if self.payload['device_type'] == 'temp':
            temp = TempSensor()
            value = temp.get_temp()
            temp.close()
            return value

    def _get_timestamp(self):
        """ Timestamp for sesnor reading.

        Returns:
            Current time timestamp in unix epoch.
        """
        return time.time()
