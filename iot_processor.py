import hashlib
import time

import cbor
import base_logger

from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.handler import TransactionHandler


VALIDATOR_ADDRESS = 'tcp://192.168.0.221:4004'
FAMILY_NAME = 'IoT-data'
VERSION = '1.0'

MIN_TEMP = -10
MAX_TEMP = 35

LOGGER = base_logger.get_logger(__name__)


def _hash(data):
    """ Compute the SHA-512 hash and return the result as hex characters.

    Args:
        data: The data to be hashed.
    Returns:
        Hex characters of hashed data.
    """
    return hashlib.sha512(data).hexdigest()


def _get_address(device_id, public_key):
    """ Returns namespace address for storing state on merkle tree. Derived
    from hashes of family name, device_id, and public key.

    Args:
        device_id: The IoT devive id.
        public_key: Public key of the IoT client.
    Returns:
        A 70 character address of the merkle namespace.
    """
    return _hash(FAMILY_NAME.encode('utf-8'))[:6] + \
        _hash(device_id.encode('utf-8'))[:4] + \
        _hash(public_key.encode('utf-8'))[:60]


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
        """ Explain apply function

        args:
            transaction: An IoT-data transaction
            context:

        This function will take a transaction and save it to state.
        There will be some validation rules applied.
        Use https://github.com/hyperledger/sawtooth-sdk-python/blob/main/examples/intkey_python/sawtooth_intkey/processor/handler.py for ref

        """
        header = transaction.header
        from_key = header.signer_public_key

        timestamp, device_id, device_type, value = self._decode_unpack_txn(
            transaction.payload)

        if timestamp > time.time():
            LOGGER.error('Received a timestamp of {} that ocurs in the future'.format(time.strftime(
                "%a, %d %b %Y %H:%M:%S +0000", time.localtime(timestamp))))
            return

        if not self._validate_txn(device_type, value):
            LOGGER.error('Value of {} for {} on device {} failed validation'.format(
                value, device_type, device_id))
            return

        address = _get_address(device_id, from_key)
        self._set_state(address, transaction.payload, context)

    def _decode_unpack_txn(self, payload):
        """ Decodes the CBOR encoded payload and unpacks the contents.

        Args:
            payload: The transaction payload.
        Returns:
            timestamp, device_id, device_type, value
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
        """ Stores state on the blockchain.

        Args:
            address: The merkle tree namespace to store state.
            state_data: The data that will be stroed in state.
            context:
        """
        context.set_state({address: state_data})


def main():
    """ Main function
    """
    try:
        processor = TransactionProcessor(VALIDATOR_ADDRESS)
        ns_prefix = _hash(FAMILY_NAME.encode('utf-8'))[0:6]
        handler = IoTTransactionHandler(ns_prefix)
        processor.add_handler(handler)
        LOGGER.info('{} transaction processor started on {}'.format(
            FAMILY_NAME, VALIDATOR_ADDRESS))
        processor.start()
    except Exception as err:
        print(err)


if __name__ == "__main__":
    main()
