import hashlib

def hash(data):
    """ Compute the SHA-512 hash and return the result as hex characters.

    Args:
        data: The data to be hashed.
    Returns:
        Hex characters of hashed data.
    """
    return hashlib.sha512(data).hexdigest()


def get_address(family_name, device_id, public_key):
    """ Returns namespace address for storing state on merkle tree. Derived
    from hashes of family name, device_id, and public key.

    Args:
        family_name: Transaction family name
        device_id: The IoT devive id.
        public_key: Public key of the IoT client.
    Returns:
        A 70 character address of the merkle namespace.
    """
    return hash(family_name.encode('utf-8'))[:6] + \
        hash(device_id.encode('utf-8'))[:4] + \
        hash(public_key.encode('utf-8'))[:60]