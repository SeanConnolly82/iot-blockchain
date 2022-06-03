import hashlib
import random
import cbor
import requests


import base_logger
import helper_functions as hf

from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_signing import CryptoFactory
from sawtooth_signing import create_context

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import Batch

REST_API_URL = ['http://192.168.0.165:8008','http://192.168.0.81:8008','http://192.168.0.228:8008']
FAMILY_NAME = 'IoT-data'

LOGGER = base_logger.get_logger(__name__)

class IoTClient():
    """ Send IoT device transactions to Transaction Processor.
    """
    def __init__(self, device_id, key_file=None):
        if key_file is None:
            self._signer = None
            return
        try:
            with open(key_file) as key_fd:
                private_key_str = key_fd.read().strip()
        except OSError as err:
            LOGGER.error('Unable to get private key from file. {}'.format(err))
            raise Exception(err)
        try:
            private_key = Secp256k1PrivateKey.from_hex(private_key_str)
            #private_key = create_context('secp256k1').new_random_private_key()
        except ParseError as err:
            LOGGER.error('Unable to parse private key. {}'.format(err))
            raise Exception(err)

        self._signer = CryptoFactory(create_context(
            'secp256k1')).new_signer(private_key)
        self._public_key = self._signer.get_public_key().as_hex()
        self._address = hf.get_address(FAMILY_NAME, device_id, self._public_key)
        self._txn_list = []

    def post(self, payload):
        """ Posts IoT Batch list to REST API.

        Args:
            payload: The IoT device payload.
        Returns:
            The API response text.
        """
        if not isinstance(payload, dict):
            LOGGER.error('Expected a dictionary but instead got a {}'.format(type(payload)))
            raise TypeError
                
        payload_bytes = cbor.dumps(payload)
        txn = self._create_txn(payload_bytes)
        self._txn_list.append(txn)
        if len(self._txn_list) == 10:
            batches = self._create_batch_list()
            self._txn_list = []
            return self._send_to_rest_api('POST', 'batches', batches)

    def get(self):
        """ Gets current state payload from REST API.

        returns:
            The API response text.
        """
        return self._send_to_rest_api('GET', 'state')

    def _send_to_rest_api(self, method, suffix, data=None):
        """ Sends a POST or GET HTTP request to the Sawtooth REST API.

        Args:
            method: HTTP method, POST or GET
            suffix: Endpoint to be added to base url
            data: Batch list
        Returns:
            The API response text.
        """
        url = '{}/{}'.format(REST_API_URL[random.randint(0,2)], suffix)
        headers = {'Content-Type': 'application/octet-stream'}

        try:
            if method == 'POST':
                result = requests.post(url, headers=headers, data=data)
            elif method == 'GET':
                result = requests.get('{url}/{}'.format(self._address), headers=headers)

            if not result.ok:
                LOGGER.error('Transaction received a {} status code'.format(
                    result.status_code))
                raise Exception("Error {}: {}".format(
                    result.status_code, result.reason))
            else:
                LOGGER.info('Transaction received a {} status code. {}'.format(
                    result.status_code, result.text))

        except requests.ConnectionError as err:
            LOGGER.error('Failed to connect to {}: {}'.format(url, str(err)))
            raise Exception(err)
        except Exception as err:
            raise Exception(err)

    def _create_txn(self, payload):
        """ Adds the IoT payload to a transaction with a header.

        Args:
            payload: The IoT device payload.
        Returns:
            txn: A Sawtooth transactions.
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
        return txn

    def _create_batch_list(self):
        """ Creates a list of batches containing the IoT transactions.

        Returns:
            A serialised list of batches
        """
        batch_header = BatchHeader(
            signer_public_key=self._public_key,
            transaction_ids=[txn.header_signature for txn in self._txn_list],
        ).SerializeToString()

        batch = Batch(
            header=batch_header,
            header_signature=self._signer.sign(batch_header),
            transactions=self._txn_list
        )
        return BatchList(batches=[batch]).SerializeToString()
