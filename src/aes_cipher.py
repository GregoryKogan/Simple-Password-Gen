import os
from Crypto.Cipher import AES
from Crypto.Util import Padding
from hashlib import sha256


class AESCipher:
    @staticmethod
    def encrypt(key: str, plaintext: str) -> str:
        # Deterministically hash the key to 32 bytes
        hashed_key = sha256(key.encode()).digest()

        # Generate a random initialization vector (iv)
        iv = os.urandom(AES.block_size)

        # Pad the plaintext to be a multiple of 16 bytes
        padded_plaintext = Padding.pad(
            plaintext.encode(), AES.block_size, style="pkcs7"
        )

        # Generate a cipher object using the key and iv
        cipher = AES.new(hashed_key, AES.MODE_CBC, iv)

        # Encrypt the plaintext and return the ciphertext and iv as a single string
        ciphertext = cipher.encrypt(padded_plaintext)
        return (iv + ciphertext).hex()

    @staticmethod
    def decrypt(key: str, ciphertext_and_iv: str) -> str:
        # Deterministically hash the key to 32 bytes
        hashed_key = sha256(key.encode()).digest()

        # Convert the ciphertext_and_iv to bytes
        ciphertext_and_iv = bytes.fromhex(ciphertext_and_iv)

        # Extract the iv and ciphertext from the input string
        iv = ciphertext_and_iv[: AES.block_size]
        ciphertext = ciphertext_and_iv[AES.block_size :]

        # Generate a cipher object using the key and iv
        cipher = AES.new(hashed_key, AES.MODE_CBC, iv)

        # Decrypt the ciphertext
        padded_plaintext = cipher.decrypt(ciphertext)

        # Remove the padding from the plaintext
        try:
            plaintext = Padding.unpad(padded_plaintext, AES.block_size, style="pkcs7")
            return plaintext.decode()
        except ValueError as e:
            raise ValueError("Wrong key") from e
