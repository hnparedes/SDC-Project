import hashlib
import json
import os
import shutil
import tempfile

# For 7zip support
import py7zr

# PyCryptodome for hashing
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from sdc_common_module.acm import AccessControlMatrix


# Viewer backend class
class SDCViewer:
    def __init__(self):
        # Setup variables for the viewer's later usage.
        self.temp_dir = None
        self.acm = AccessControlMatrix()
        self.key_library = {}
        self.current_user_level = None
        self.contents_dir = None

    # Function to open and attempt to access the SDC at the 7zip level
    def open_archive(self, archive_name, archive_password):
        # Use entered password as a hash for 7z decryption
        hashed_password = hashlib.sha256(archive_password.encode()).hexdigest()
        self.temp_dir = tempfile.mkdtemp(prefix=".tempdir_viewer_")
        try:
            with py7zr.SevenZipFile(
                archive_name, "r", password=hashed_password
            ) as archive:
                archive.extractall(path=self.temp_dir)
            self.contents_dir = os.path.join(self.temp_dir, "sdc_contents")

            with open(os.path.join(self.contents_dir, "acm.json"), "r") as f:
                self.acm.load_json(json.load(f))
            with open(os.path.join(self.contents_dir, "key_lib.json"), "r") as f:
                self.key_library = json.load(f)
            return True
        except py7zr.exceptions.PasswordRequired:
        # TODO: This should be handled better.
        self.close()
        return False
        except Exception as e:
            self.close()
            raise e

    # Function to authenicate with SDC
    def login(self, uid, password):
        user = self.acm.users.get(uid)
        if user and user["password_hash"] == self.acm.hash_password(password):
            self.current_user_level = user["access_level"]
            return True
        return False

    # Function to only access files (their titles specifically) permitted from the user's access levels
    def get_accessible_files(self):
        return [
            fid
            for fid, levels in self.acm.documents.items()
            if self.current_user_level in levels
        ]

    # Function to extract a select file
    def extract_document(self, file_id, dest_path):
        try:
            key = bytes.fromhex(self.key_library[file_id])
            enc_filepath = os.path.join(self.contents_dir, file_id)

            # Read encrypted file in binary mode
            with open(enc_filepath, "rb") as f:
                # IV -> Initialization Vector
                iv = f.read(16)
                ciphertext = f.read()

            # Validate encrypted structure
            if len(ciphertext) == 0:
                raise Exception("File is not properly encrypted or is corrupted")

            # Decrypt the file
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)

            # Write decrypted file in byte mode
            with open(dest_path, "wb") as f:
                f.write(decrypted_data)

            # Inform user data is accessible
            return True

        except Exception as e:
            # Inform user data is NOT accessible
            raise Exception(f"Data cannot be accessed: {e}")

    # Helper function to clear temp directory after closing viewer
    def close(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
