import time
import cbor

import base_logger
import helper_functions as hf

from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction


VALIDATOR_ADDRESS = 'tcp://192.168.0.221:4004'
FAMILY_NAME = 'IoT-data'
VERSION = '1.0'

MIN_TEMP = -10
MAX_TEMP = 35

LOGGER = base_logger.get_logger(__name__)


class IoTTransactionHandler(TransactionHandler):

    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return [VERSION]

    @property
    def namespaces(self):
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        """ Apply transaction.

        args:
            transaction: An IoT-data transaction.
            context: An interface for setting, getting and deleting a validator state.

        """
        header = transaction.header
        from_key = header.signer_public_key

        timestamp, device_id, device_type, value = self._decode_unpack_txn(
            transaction.payload)

        if timestamp > time.time():
            LOGGER.error('Received a timestamp of {} that ocurs in the future'.format(time.strftime(
                "%a, %d %b %Y %H:%M:%S +0000", time.localtime(timestamp))))
            raise InvalidTransaction('Invalid timestamp')

        if not self._validate_txn(device_type, value):
            LOGGER.error('Value of {} for {} on device {} failed validation'.format(
                value, device_type, device_id))
            raise InvalidTransaction('Invalid reading')

        address = hf.get_address(FAMILY_NAME, device_id, from_key)
        self._set_state(address, transaction.payload, context)

    def _decode_unpack_txn(self, payload):
        """ Decodes the CBOR encoded payload and unpacks the contents.

        Args:
            payload: The transaction payload.
        Returns:
            timestamp: device_id, device_type, value
        """
        try:
            content = cbor.loads(payload)
        except Exception as err:
            print(err)
        timestamp = content['timestamp']
        device_id = content['device_id']
        device_type = content['device_type']
        value = content['value']
        return timestamp, device_id, device_type, value

    def _validate_txn(self, device_type, value):
        """ Validate transaction values are within expected range.

        Args:
            device_type: The type of device from the transaction payload.
            value: The value of the device fron the transaction payload.
        Returns:
            True if value is valid, False if not valid
        """
        if device_type == 'temp':
            return MIN_TEMP <= value <= MAX_TEMP
        if device_type == 'humidity':
            pass

    def _set_state(self, address, state_data, context):
        """ Sets state on the blockchain.

        Args:
            address: The merkle tree namespace to store state.
            state_data: The data that will be stroed in state.
            context: An interface for setting, getting and deleting a validator state.
        """
        context.set_state({address: state_data})


def main():
    """ Main function
    """
    try:
        processor = TransactionProcessor(VALIDATOR_ADDRESS)
        ns_prefix = hf.hash(FAMILY_NAME.encode('utf-8'))[0:6]
        handler = IoTTransactionHandler(ns_prefix)
        processor.add_handler(handler)
        LOGGER.info('{} transaction processor started on {}'.format(
            FAMILY_NAME, VALIDATOR_ADDRESS))
        processor.start()
    except Exception as err:
        print(err)


if __name__ == "__main__":
    main()
