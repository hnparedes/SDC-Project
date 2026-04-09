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
