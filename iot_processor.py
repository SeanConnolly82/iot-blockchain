import hashlib

import cbor

from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_xo.processor.handler import XoTransactionHandler


FAMILY_NAME = 'IoT-data'

MIN_TEMP = -10
MAX_TEMP = 35

def _hash(data):
    '''Compute the SHA-512 hash and return the result as hex characters.'''
    return hashlib.sha512(data).hexdigest()

def _get_address(device_id, from_key):
    """
    Look into namespace becuase there were some interesting points in the docs.
    """
    return _hash(FAMILY_NAME.encode('utf-8'))[:6] + \
                _hash(device_id.encode('utf-8'))[:4] + \
                _hash(from_key.encode('utf-8'))[:60]

class IoTTransactionHandler(TransactionHandler):
    
    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        """
        This function will take a transaction and save it to state.
        There will be some validation rules applied.
        Use https://github.com/hyperledger/sawtooth-sdk-python/blob/main/examples/intkey_python/sawtooth_intkey/processor/handler.py for ref
        
        """
        header = transaction.header
        from_key = header.signer_public_key

        timestamp, device_id, device_type, value = self._decode_unpack_txn(transaction.payload)
        if not self._validate_txn(device_type, value):
            pass

        address = _get_address(device_id, from_key)
        self._set_state(address, transaction.payload, context)
    

    def _decode_unpack_txn(self, payload):
        """
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
        """
        """
        pass
        

    def _set_state(self, address, state_data, context):
        """
        """
        context.set_state({address: state_data})

    def _get_state():
        pass

def main():
    """Main function
    """
    processor = TransactionProcessor(url='tcp://127.0.0.1:4004')
    handler = IoTTransactionHandler()
    processor.add_handler(handler)
    processor.start()

if __name__ == "__main__":
    main()