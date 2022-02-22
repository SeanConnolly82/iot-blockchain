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

    def get_values(self):
        """ Reads sensor values and updates sensor object.
        """
        self.payload['timestamp'] = self._get_timestamp()
        self.payload['value'] = self._get_reading()
        LOGGER.info('Sesnor reading of {} for {} on device ID {} at {}'.format(self.payload['value'], self.payload['device_type'], self.payload['device_id'], time.strftime(
            "%a, %d %b %Y %H:%M:%S +0000", time.localtime(self.payload['timestamp']))))

    def _get_reading(self):
        """ Get the sensor reading.

        Returns:
            Current sensor value.
        """
        return 40  # read the sensor value

    def _get_timestamp(self):
        """ Timestamp for sesnor reading.

        Returns:
            Current time timestamp.
        """
        return time.time()
