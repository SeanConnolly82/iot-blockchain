import hashlib
import random

import cbor
import requests

import base_logger

from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_signing import CryptoFactory
from sawtooth_signing import create_context

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import Batch


# Test adding more transactions to a batch
FAMILY_NAME = 'IoT-data'
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


class IoTClient():
    """ Send IoT device transactions to Transaction Processor.
    """

    def __init__(self, base_url, device_id, key_file=None):
        self.base_url = base_url

        # if key_file is None:
        #     self._signer = None
        #     return

        # try:
        #     with open(key_file) as key_fd:
        #         private_key_str = key_fd.read().strip()
        # except OSError as err:
        #     raise Exception('Insert message')

        try:
            #private_key = Secp256k1PrivateKey.from_hex(private_key_str)
            private_key = create_context('secp256k1').new_random_private_key()
        except ParseError as err:
            raise Exception('Insert message')

        self._signer = CryptoFactory(create_context(
            'secp256k1')).new_signer(private_key)
        self._public_key = self._signer.get_public_key().as_hex()
        self._address = _get_address(device_id, self._public_key)

    def post(self, payload):
        """ Posts IoT Batch list to REST API.

        Args:
            payload: The IoT device payload.
        Returns:
            The API response text.
        """
        if not isinstance(payload, dict):
            raise TypeError(
                'Expected a dictionary but instead got a {}'.format(type(payload)))
        payload_bytes = cbor.dumps(payload)
        batches = self._create_batch_list(payload_bytes)
        return self._send_to_rest_api('POST', 'batches', batches)

    def get(self):
        """ 
        """
        return self._send_to_rest_api('GET', 'batches')

    def _send_to_rest_api(self, method, suffix, data=None):
        """ Sends a Post or Get request to the Sawtooth REST API.

        Args:
            method: HTTP method, POST or GET
            suffix: Endpoint to be added to base url
            data: Batch list
        Returns:
            The API response text.
        """
        url = '{}/{}'.format(self.base_url, suffix)
        headers = {'Content-Type': 'application/octet-stream'}

        try:
            if method == 'POST':
                result = requests.post(url, headers=headers, data=data)
            elif method == 'GET':
                result = requests.get(url, headers=headers)

            if not result.ok:
                LOGGER.error('Transaction received a {} status code'.format(
                    result.status_code))
                raise Exception("Error {}: {}".format(
                    result.status_code, result.reason))
            else:
                LOGGER.info('Transaction received a {} status code'.format(
                    result.status_code))

        except requests.ConnectionError as err:
            LOGGER.error('Connection error {}'.format(err))
            raise Exception(
                'Failed to connect to {}: {}'.format(url, str(err)))
        except Exception as err:
            raise Exception(err)

        return result.text

    def _create_txn_list(self, payload):
        """ Adds the IoT payload to a transaction with a header.

        Args:
            payload: The IoT device payload.
        Returns:
            [txn]: A list of transactions.
        """
        txn_header = TransactionHeader(
            family_name=FAMILY_NAME,
            family_version='1.0',
            inputs=[self._address],
            outputs=[self._address],
            signer_public_key=self._public_key,
            batcher_public_key=self._public_key,
            dependencies=[],
            payload_sha512=hashlib.sha512(payload).hexdigest(),
            nonce=random.random().hex().encode()
        ).SerializeToString()

        txn = Transaction(
            header=txn_header,
            payload=payload,
            header_signature=self._signer.sign(txn_header)
        )
        return [txn]

    def _create_batch_list(self, payload):
        """ Creates a list of batches containing the IoT transactions.

        Args:
            payload: The IoT device payload.
        Returns:
            A serialised list of batches
        """
        txns = self._create_txn_list(payload)
        batch_header = BatchHeader(
            signer_public_key=self._public_key,
            transaction_ids=[txn.header_signature for txn in txns],
        ).SerializeToString()

        batch = Batch(
            header=batch_header,
            header_signature=self._signer.sign(batch_header),
            transactions=txns
        )
        return BatchList(batches=[batch]).SerializeToString()
