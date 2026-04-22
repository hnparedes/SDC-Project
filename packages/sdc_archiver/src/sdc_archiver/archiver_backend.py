import json
import os
import shutil
import tempfile
import hashlib

import py7zr
from Crypto.Random import get_random_bytes
from sdc_common_module.ackey import ackey
from sdc_common_module.crypto import CryptoSDC
from sdc_common_module.acm import AccessControlMatrix


# Archiver backend class (TODO: Missing unfinalized SDC saving)
class SDCArchiver:
    # Setup ACM, crypto, document list, and key library for the archiver's later usage.
    def __init__(self):
        self.acm = AccessControlMatrix()
        self.crypto = CryptoSDC()
        self.key_library = {}

    # Saves draft ACM
    def save_draft(self, location):
        with open(location, "w") as f:
            json.dump(self.acm.to_json(), f)

    # Loads draft ACM
    def load_draft(self, location):
        with open(location, "r") as f:
            self.acm.load_json(json.load(f))

    # Exports completed SDC
    def export_archive(self, archive_name, archive_password):
        temp_dir = tempfile.mkdtemp(prefix=".tempdir_sdc_")
        try:
            # Hash password for 7z encryption
            hashed_password = hashlib.sha256(archive_password.encode()).hexdigest()
            for fid, doc in self.acm.documents.items():
                fpath = doc["path"]
                # 32 bytes -> 256 bits
                key = get_random_bytes(32)
                self.key_library[fid] = key.hex()

                # Read plaintext data
                with open(fpath, "rb") as f:
                    plaintext_data = f.read()

                encrypted_data = self.crypto.encrypt_data(plaintext_data, key)

                # Ensure encryption actually changed the data
                if encrypted_data[16:] == plaintext_data:
                    raise Exception(f"Encryption failed for {fid}")

                with open(os.path.join(temp_dir, fid), "wb") as f:
                    f.write(encrypted_data)
                    
            # Encrypt ACM and key library using the master key (ackey)
            acm_json = json.dumps(self.acm.to_json(True)).encode("utf-8")
            keylib_json = json.dumps(self.key_library).encode("utf-8")
            ackey_bytes = ackey.encode("utf-8")
            ackey_hash = hashlib.sha256(ackey_bytes).digest()

            # Encrypted ACM and key library
            acm_encrypted = self.crypto.encrypt_data(acm_json, ackey_hash)
            keylib_encrypted = self.crypto.encrypt_data(keylib_json, ackey_hash)

            # Write encrypted metadata files
            with open(os.path.join(temp_dir, "acm.enc"), "wb") as f:
                f.write(acm_encrypted)
            with open(os.path.join(temp_dir, "key_lib.enc"), "wb") as f:
                f.write(keylib_encrypted)

            with py7zr.SevenZipFile(
                archive_name, "w", password=hashed_password
            ) as archive:
                archive.writeall(temp_dir, "sdc_contents")
            return True
        # Cover exception cases
        except Exception as e:
            raise e
        # Delete temp directory upon completion
        finally:
            shutil.rmtree(temp_dir)
