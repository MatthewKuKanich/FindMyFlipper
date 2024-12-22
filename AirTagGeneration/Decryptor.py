import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend


class Decryptor:
    def __init__(self, data: bytes, priv: int):
        # check if NULL bytes are present in the data
        offsetAdjustment = len(data) - 88
        # If so slice the data accordingly | Thanks, @c4pitalSteez!
        eph_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP224R1(), data[5+offsetAdjustment:62+offsetAdjustment])
        shared_key = ec.derive_private_key(priv, ec.SECP224R1(), default_backend()).exchange(ec.ECDH(), eph_key)
        symmetric_key = self.__sha256(shared_key + b'\x00\x00\x00\x01' + data[5+offsetAdjustment:62+offsetAdjustment])
        decryption_key = symmetric_key[:16]
        iv = symmetric_key[16:]
        auth_tag = data[72+offsetAdjustment:]

        self.enc_data = data[62+offsetAdjustment:72+offsetAdjustment]
        self.algorithm_dkey = algorithms.AES(decryption_key)
        self.mode = modes.GCM(iv, auth_tag)
    
    def __sha256(self, data: bytes):
        digest = hashlib.new("sha256")
        digest.update(data)
        return digest.digest()
        
    def Decrypt(self):
        decryptor = Cipher(self.algorithm_dkey, self.mode, default_backend()).decryptor()
        return decryptor.update(self.enc_data) + decryptor.finalize()




