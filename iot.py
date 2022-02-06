import time
import sys
import os
import socket

from sensor import Sensor
from iot_client import IoTClient


DEFAULT_URL = 'http://localhost:8008'


def _get_private_keyfile():
    """
    """
    hostname = socket.gethostname()
    print(hostname)
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")
    return '{}/{}.priv'.format(key_dir, hostname)


def arg_parser():
    pass


def do_post(sensor_id, sensor_type):
    """
    """
    key_file = _get_private_keyfile()
    sensor = Sensor(sensor_id, sensor_type)
    client = IoTClient(DEFAULT_URL, sensor.payload['device_id'], key_file)
    while True:
        sensor.read_value()
        response = client.post(sensor.payload)
        print(response)
        time.sleep(10)


def do_get(sensor_id):
    """
    """
    key_file = ''#_get_private_keyfile()
    sensor = Sensor(sensor_id)
    client = IoTClient(DEFAULT_URL, sensor.payload['device_id'], key_file)
    client.get()
    

def main ():
    """
    Create the sensor somewhere where it can be read continuously in a loop.
    """
    print('Starting')
    action = 'post'
    try:
        if action == 'read':
            do_get('TMP10000')
        elif action == 'post':
            do_post('TMP10000','Temp')
    except KeyboardInterrupt:
        print('Stopped')
    except Exception:
        sys.exit(1)

if __name__ == '__main__':
    main()