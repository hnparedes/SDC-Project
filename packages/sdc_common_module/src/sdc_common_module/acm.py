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
        self.documents = {}
        self.access_levels = []

    # Simple hashing function (SHA256)
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # Function to add access level with a unique name.
    # Returns true if and only if the access level was added successfully.
    def add_access_level(self, lvl):
        # Is the name nonempty?
        if not lvl:
            return False

        # Are there no existing access levels with this name?
        if lvl in self.access_levels:
            return False

        self.access_levels.append(lvl)
        return True

    # Function to add user with unique user ID, and their password and access levels.
    # Returns true if and only if the user was added successfully.
    def add_user(self, uid, password, access_level):
        # Are all field nonempty?
        if not uid or not password or not access_level:
            return False

        # Are there no existing users with this uid?
        if uid in self.users:
            return False

        self.users[uid] = {
            "password_hash": self.hash_password(password),
            "access_level": access_level,
        }
        return True

    # Function to add document with a unique name, and the access levels allowed to view it
    def add_document(self, doc_id, access_levels):
        # Is the document name and access level list nonempty?
        if not doc_id or not access_levels:
            return False

        # Are there no existing documents with this id?
        # Potential alternate behavior:
        # - Auto-incrementing filenames instead of rejecting duplicate names?
        # - Ask if the user wants to overwrite the existing entry?
        if doc_id in self.documents:
            return False

        # TODO: Reject the document if access_levels contains the error access level

        self.documents[doc_id] = access_levels
        return True

    def rename_access_level(self, old_lvl, new_lvl):
        # Is the old level name nonempty and has a corresponding access level?
        if not old_lvl or old_lvl not in self.access_levels:
            return False

        # Is the new level name nonempty?
        if not new_lvl:
            return False

        # Is the new level name different from the old level name?
        if new_lvl == old_lvl:
            return False

        # Is there no existing access level that already has the new name?
        if new_lvl in self.access_levels:
            return False

        # Change the access level name
        idx = self.access_levels.index(old_lvl)
        self.access_levels[idx] = new_lvl

        # Cascade change to users
        for uid, udata in self.users.items():
            if udata["access_level"] == old_lvl:
                udata["access_level"] = new_lvl

        # Cascade change to files
        for fid, levels in self.documents.items():
            if old_lvl in levels:
                levels[levels.index(old_lvl)] = new_lvl

        return True

    def update_user(self, old_uid, new_uid, new_pwd, new_lvl):
        # Is the old user ID nonempty and has a corresponding user?
        if not old_uid or old_uid not in self.users:
            return False

        # Is the new user ID and access level nonempty?
        if not new_uid or not new_lvl:
            return False

        # Note that the password is NOT checked for nonemptiness.
        # That's because this function interprets an empty password field as retaining the current password.

        # If the user ID is being changed, is the new user ID unique?
        if new_uid != old_uid and new_uid in self.users:
            return False

        old_hash = self.users[old_uid]["password_hash"]
        if new_uid != old_uid:
            del self.users[old_uid]

        self.users[new_uid] = {
            "password_hash": self.hash_password(new_pwd)
            if new_pwd
            else old_hash,
            "access_level": new_lvl,
        }
        return True

    def set_document_perms(self, doc_id, access_levels):
        # Is the document name and access level list nonempty?
        if not doc_id or not access_levels:
            return False

        # Does the document we are changing the permissions of exist?
        if doc_id not in self.documents:
            return False

        # TODO: Reject the document if access_levels contains the error access level

        self.documents[doc_id] = access_levels
        return True

    def get_users_with_access_level(self, lvl):
        # Should these return an error instead of an empty array?

        # Is the level name nonempty?
        if not lvl:
            return []

        # Does the access level exist?
        if lvl not in self.access_levels:
            return []

        return [
            uid
            for uid, udata in self.users.items()
            if udata["access_level"] == lvl
        ]

    def delete_access_level(self, lvl_to_delete):
        # Is the level name nonempty?
        if not lvl_to_delete:
            return False

        # Does the access level exist?
        if lvl_to_delete not in self.access_levels:
            return False

        affected_users = self.get_users_with_access_level(lvl_to_delete)

        # Remove from backend's main access level list
        if lvl_to_delete in self.access_levels:
            self.access_levels.remove(lvl_to_delete)

        # Remove this access level from any documents through iteration
        for fid, levels in self.documents.items():
            if lvl_to_delete in levels:
                levels.remove(lvl_to_delete)

        # Set affected users to "Unassigned"
        for uid in affected_users:
            self.users[uid]["access_level"] = "Unassigned"

        return True

    def delete_user(self, uid):
        # Is the user ID nonempty?
        if not uid:
            return False

        # Does the user exist?
        if uid not in self.users:
            return False

        # Remove from user list and access control
        if uid in self.users:
            del self.users[uid]
        return True

    def delete_document(self, fid):
        # Is the document ID nonempty?
        if not fid:
            return False

        # Does the document exist?
        if fid not in self.documents:
            return False

        if fid in self.documents:
            del self.documents[fid]
        return True

    # JSON formatting helper
    def to_json(self):
        return {
            "users": self.users,
            "files": self.documents,
            "access_levels": self.access_levels,
        }

    # JSON loader
    def load_json(self, data):
        self.users = data.get("users", {})
        self.documents = data.get("files", {})
        self.access_levels = data.get("access_levels", [])
