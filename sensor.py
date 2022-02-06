import time

class Sensor():
    """
    This could be an abstract method instatiated for different sensor types
    """
    def __init__(self, sensor_id, sensor_type=None):
        self.payload = {
            'timestamp': None,
            'device_id': sensor_id,
            'device_type': sensor_type,
            'value': None
        }

    def read_value(self):
        self.payload['timestamp'] = self._get_timestamp()
        self.payload['value'] = self._get_reading()

    def _get_reading():
        """ Placeholer for reading physical device
        """
        return 4 # read the sensor value

    def _get_timestamp():
        """
        """
        return time.now()