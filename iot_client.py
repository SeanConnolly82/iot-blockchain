import hashlib

import cbor
import requests
from iot_processor import FAMILY_NAME

from sawtooth_signing import ParseError
from sawtooth_signing import Secp256k1PrivateKey
from sawtooth_signing import CryptoFactory
from sawtooth_signing import create_context

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import Batch

# Test adding more transactions to a batch
FAMILY_NAME = 'IoT-data'

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


class IoTClient():
    """
    Business logic for sending transactions to TP
    """
    def __init__(self, base_url, device_id, key_file=None):
        self.base_url = base_url

        if key_file is None:
            self._signer = None
            return
        
        try:
            with open(key_file) as key_fd:
                private_key_str = key_fd.read().strip()
        except OSError as err:
            raise Exception('Insert message')

        try:
            #private_key = Secp256k1PrivateKey.from_hex(private_key_str)
            private_key = create_context('secp256k1').new_random_private_key()
        except ParseError as err:
            raise Exception('Insert message')
        
        self._signer = CryptoFactory(create_context('secp256k1')).new_signer(private_key)
        self._public_key = self._signer.get_public_key().as_hex()
        self._address = _get_address(device_id, self._public_key)


def post(self, payload):
    """
    """
    if not isinstance(payload, dict):
        raise TypeError('Give me some dict')
    payload_bytes = cbor.dumps(payload)
    batches = self._create_batch_list(payload_bytes)
    return self._send_to_rest_api('post', 'batches', batches)

def get(self):
    """
    """
    return self._send_to_rest_api('get', 'batches')

def _send_to_rest_api(self, method, suffix, data=None):
    """
    """
    url = 'http://localhost:8008'
    headers={'Content-Type': 'application/octet-stream'}

    try:
        if method == 'post':
            result = requests.post(url, headers=headers, data=data)
        elif method == 'get':
            result = requests.get(url, headers=headers)

        if not result.ok:
            raise Exception("Error {}: {}".format(
                result.status_code, result.reason))

    except requests.ConnectionError as err:
        raise Exception(
            'Failed to connect to {}: {}'.format(url, str(err)))

    except BaseException as err:
        raise Exception(err)

    return result.text

def _create_txn_list(self, payload):
    """
    """
    txn_header = TransactionHeader(
        family_name=FAMILY_NAME,
        family_version='1.0',
        inputs=[],
        outputs=[],
        signer_public_key=self._public_key,
        batcher_public_key=self._public_key,
        dependencies=[],
        payload_sha512=hashlib.sha512(payload).hexdigest()
        nonce=random.random().hex().encode()
    ).SerializeToString()

    txn = Transaction(
        header=txn_header,
        payload=payload,
        header_signature=self._signer.sign(txn_header)
    )
    return [txn]

def _create_batch_list(self, payload):
    """
    """
    txns = self._create_txn_list(payload)
    batch_header = BatchHeader(
        signer_public_key=self._public_key,
        transaction_ids=[txn.header_signature for txn in txns],
    ).SerializeToString()

    batch = Batch(
        header=batch_header,
        header_signature=self.signer.sign(batch_header),
        transactions=txns
    )
    return BatchList(batches=[batch]).SerializeToString()