import json
import os
import shutil
import tempfile
import hashlib

import py7zr
from Crypto.Random import get_random_bytes
from sdc_common_module.crypto import CryptoSDC
from sdc_common_module.acm import AccessControlMatrix


# Archiver backend class (TODO: Missing unfinalized SDC saving)
class SDCArchiver:
    # Setup ACM, crypto, document list, and key library for the archiver's later usage.
    def __init__(self):
        self.acm = AccessControlMatrix()
        self.crypto = CryptoSDC()
        self.document_filepaths = {}
        self.key_library = {}

    # Exports completed SDC
    def export_archive(self, archive_name, archive_password):
        temp_dir = tempfile.mkdtemp(prefix=".tempdir_sdc_")
        try:
            # Hash password for 7z encryption
            hashed_password = hashlib.sha256(archive_password.encode()).hexdigest()
            for fid, fpath in self.document_filepaths.items():
                # 32 bytes -> 256 bits
                key = get_random_bytes(32)
                self.key_library[fid] = key.hex()

                # Read plaintext data
                with open(fpath, "rb") as f:
                    plaintext_data = f.read()

                encrypted_data = self.crypto.encrypt_data(plaintext_data, key)

                # Ensure encryption actually changed the data
                if encrypted_data[16:] == plaintext:
                    raise Exception(f"Encryption failed for {fid}")

                with open(os.path.join(temp_dir, fid), "wb") as f:
                    f.write(encrypted_data)

            with open(os.path.join(temp_dir, "acm.json"), "w") as f:
                json.dump(self.acm.to_json(), f)

            with open(os.path.join(temp_dir, "key_lib.json"), "w") as f:
                json.dump(self.key_library, f)

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
