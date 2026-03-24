import hashlib
import json
import os
import shutil
import tempfile

import py7zr
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad


# Common backend class for ACM
class AccessControlMatrix:
    # Setup user, file, and access lists
    def __init__(self):
        self.users = {}
        self.files = {}
        self.access_levels = []

    # Simple hashing function (SHA256)
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # Function to add user with unique user ID, and their password and access levels. (TODO: Move to archiver class?)
    def add_user(self, uid, password, access_level):
        self.users[uid] = {
            "password_hash": self.hash_password(password),
            "access_level": access_level,
        }

    # Function to add access level to a file
    def add_file_permission(self, file_id, access_levels):
        self.files[file_id] = access_levels

    # JSON formatting helper
    def to_json(self):
        return {
            "users": self.users,
            "files": self.files,
            "access_levels": self.access_levels,
        }

    # JSON loader
    def load_json(self, data):
        self.users = data.get("users", {})
        self.files = data.get("files", {})
        self.access_levels = data.get("access_levels", [])


# Archiver backend class (TODO: Missing unfinalized SDC saving)
class SDCArchiver:
    # Setup ACM, document list, and key library for the archiver's later usage.
    def __init__(self):
        self.acm = AccessControlMatrix()
        self.documents = {}
        self.key_library = {}

    # Exports completed SDC
    def export_archive(self, archive_name, archive_password):
        temp_dir = tempfile.mkdtemp(prefix=".tempdir_sdc_")
        try:
            for fid, fpath in self.documents.items():
                # 32 bytes -> 256 bits
                key = get_random_bytes(32)
                self.key_library[fid] = key.hex()

                # Setup AES-256
                cipher = AES.new(key, AES.MODE_CBC)
                with open(fpath, "rb") as f:
                    data = f.read()

                encrypted_data = cipher.iv + cipher.encrypt(pad(data, AES.block_size))
                with open(os.path.join(temp_dir, fid), "wb") as f:
                    f.write(encrypted_data)

            with open(os.path.join(temp_dir, "acm.json"), "w") as f:
                json.dump(self.acm.to_json(), f)

            with open(os.path.join(temp_dir, "key_lib.json"), "w") as f:
                json.dump(self.key_library, f)

            with py7zr.SevenZipFile(
                archive_name, "w", password=archive_password
            ) as archive:
                archive.writeall(temp_dir, "sdc_contents")
            return True
        # Cover exception cases
        except Exception as e:
            raise e
        # Delete temp directory upon completion
        finally:
            shutil.rmtree(temp_dir)
