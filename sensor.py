import time

import base_logger

LOGGER = base_logger.get_logger(__name__)

class Sensor():
    """
    This could be an abstract method instatiated for different sensor types.
    """
    def __init__(self, sensor_id, sensor_type=None):
        self.payload = {
            'timestamp': None,
            'device_id': sensor_id,
            'device_type': sensor_type,
            'value': None
        }

    def read_value(self):
        """ Reads sensor values and updates sensor object.
        """
        self.payload['timestamp'] = self._get_timestamp()
        self.payload['value'] = self._get_reading()
        LOGGER.debug('Temperature reading of .. taken at ..')

    def _get_reading(self):
        """ Get the sensor reading.

        Returns:
            Current sensor value.
        """
        return 4 # read the sensor value

    def _get_timestamp(self):
        """ Timestamp for sesnor reading.

        Returns:
            Current time timestamp.
        """
        return 1