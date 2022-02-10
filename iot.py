from ast import arg
import time
import sys
import os
import socket
import argparse

import base_logger

from sensor import Sensor
#from iot_client import IoTClient


DEFAULT_URL = 'http://localhost:8008'

LOGGER = base_logger.get_logger(__name__)

def _get_private_keyfile():
    """ Gets private key filepath.

    returns:
        A string representing the private key filepath.
    """
    hostname = socket.gethostname()
    print(hostname)
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")
    return '{}/{}.priv'.format(key_dir, hostname)


def do_post(device, interval):
    """ Gets values for an IoT device, instatiates an IoTClient object, and
    calls post on the IoTClient object.

    Args:
        device: An IoT device object.      
        interval: The interval for updating values on the blockchain.
    """
    key_file = _get_private_keyfile()
    client = IoTClient(DEFAULT_URL, device.payload['device_id'], key_file)
    loop = True
    while loop:
        device.get_values()
        response = client.post(device.payload)
        print(response)
        if interval:
            time.sleep(interval)
        else:
            loop = False


def do_get(device):
    """ Instatiates an IoTClient object, and gets the current blockchain committed
     value for an IoT device.

    Args:
        device: An IoT device object.
    """
    key_file = _get_private_keyfile()
    client = IoTClient(DEFAULT_URL, device.payload['device_id'], key_file)
    return client.get()


def create_arg_parser():
    """ Creates parser for command line arguments.

    Returns:
        parser: An argparser parser object.
    """
    parser = argparse.ArgumentParser(
        description='Process data from IoT device')
    subparser = parser.add_subparsers(dest='action', required=True)
    parser_post = subparser.add_parser('post')
    parser_post.add_argument(
        'device_id', help='The ID of the IoT device to post')
    parser_post.add_argument('device_type', choices=[
                             'temp', 'humidity'], help='The type of IoT device')
    parser_post.add_argument(
        'interval', type=int, help='The interval in seconds for transactions sent from the IoT device')
    parser_get = subparser.add_parser('get')
    parser_get.add_argument(
        'device_id', help='The ID of the IoT device to read')
    return parser


def main():
    """ Main function
    """
    args = create_arg_parser().parse_args()
    try:
        if args.action == 'get':
            sensor = Sensor(args.device_id)
            #do_get(sensor)
        elif args.action == 'post':
            sensor = Sensor('args.device_id', 'temp')
            sensor.read_value()
            #do_post(sensor, args.interval)
    except KeyboardInterrupt:
        print('Stopped')
    except Exception:
        sys.exit(1)


if __name__ == '__main__':
    main()
