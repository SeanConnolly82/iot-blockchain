import time
import sys
import os
import socket
import argparse

import base_logger

from sensor import Sensor
from iot_client import IoTClient


DEFAULT_URL = 'http://192.168.0.165:8008'

LOGGER = base_logger.get_logger(__name__)

def _get_private_keyfile():
    """ Gets private key filepath.

    returns:
        A string representing the private key filepath.
    """
    hostname = socket.gethostname()
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
    #client = IoTClient(DEFAULT_URL, device.payload['device_id'], key_file)
    loop = True
    while loop:
        device.get_values()
        #print(client.post(device.payload))
        if interval:
            time.sleep(interval)
        else:
            loop = False


def do_get(device):
    """ Instatiates an IoTClient object, and gets the current blockchain state
     value for an IoT device.

    Args:
        device: An IoT device object.
    """
    key_file = _get_private_keyfile()
    client = IoTClient(DEFAULT_URL, device.payload['device_id'], key_file)
    response = client.get()
    print(response)


def create_arg_parser():
    """ Creates parser for command line arguments.

    Returns:
        parser: An argparser parser object.
    """
    parser = argparse.ArgumentParser(
        description='Process data from IoT device')
    subparser = parser.add_subparsers(dest='action') # needs required = true
    parser_post = subparser.add_parser('post')
    parser_post.add_argument(
        'device_id', help='The ID of the IoT device to post')
    parser_post.add_argument('device_type', choices=[
                             'temp', 'humidity'], help='The type of IoT device')
    parser_post.add_argument('-i',
        '--interval', type=float, help='The interval in seconds for transactions sent from the IoT device')
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
            device = Sensor(args.device_id)
            do_get(device)
        elif args.action == 'post':
            device = Sensor(args.device_id, args.device_type)
            LOGGER.info('Created a {} device with id {}'.format(device.payload['device_type'], device.payload['device_id']))
            do_post(device, args.interval)
    except KeyboardInterrupt:
        LOGGER.warn('Keyboard interrupt')
    except Exception as err:
        print(err)
        sys.exit(1)


if __name__ == '__main__':
    main()
