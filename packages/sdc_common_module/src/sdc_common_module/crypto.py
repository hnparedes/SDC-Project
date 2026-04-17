# Import PyCryptodome library for cryptography
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


# Common cryptography class for SDC operations
class CryptoSDC:
    def encrypt_data(self, plaintext_data: bytes, key: bytes) -> bytes:
        # Setup AES in CBC mode
        cipher = AES.new(key, AES.MODE_CBC)

        # Pad the plaintext data to match block size
        padded_data = pad(plaintext_data, AES.block_size)

        # Encrypt and return the Initialization Vector followed by the ciphertext
        return cipher.iv + cipher.encrypt(padded_data)

    def decrypt_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        # The first 16 bytes are the IV
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        # Initialize cipher with the extracted IV
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)

        # Decrypt the data
        decrypted_data = cipher.decrypt(ciphertext)

        # Unpad and return the original plaintext
        return unpad(decrypted_data, AES.block_size)
