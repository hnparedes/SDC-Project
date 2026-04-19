import hashlib
from re import L


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
            raise Exception("Name cannot be empty. Please input at least one character")

        # Are there no existing access levels with this name?
        if lvl in self.access_levels:
            raise Exception(
                "Access Level with given name already exists. Please choose a different name."
            )

        if lvl.lower() == "unassigned":
            raise Exception("'Unassigned' is a reserved system level")

        self.access_levels.append(lvl)
        return True

    # Function to add user with unique user ID, and their password and access levels.
    # Returns true if and only if the user was added successfully.
    def add_user(self, uid, password, access_level):
        # Are all field nonempty?
        if not uid or not password or not access_level:
            raise Exception(
                "One or more fields are empty. Please make sure to fill out all fields."
            )

        # Are there no existing users with this uid?
        if uid in self.users:
            raise Exception(
                "This username already exists in the user list. Please choose a different username."
            )

        self.users[uid] = {
            "password_hash": self.hash_password(password),
            "access_level": access_level,
        }
        return True

    # Function to add document with a unique name, and the access levels allowed to view it
    def add_document(self, doc_id, access_levels, path = ""):
        # Is the document name and access level list nonempty?
        # (Path is allowed to be empty)
        if not doc_id or not access_levels:
            raise Exception(
                "One or more fields are empty. Please make sure to fill out all fields."
            )

        # Are there no existing documents with this id?
        # Potential alternate behavior:
        # - Auto-incrementing filenames instead of rejecting duplicate names?
        # - Ask if the user wants to overwrite the existing entry?
        if doc_id in self.documents:
            raise Exception(
                "This document is already in the SDC Archive. Please choose a different document."
            )

        for a in access_levels:
            if a.lower() == "unassigned":
                raise Exception("'Unassigned' is a reserved system level.")

        self.documents[doc_id] = {
            "path": path,
            "access_levels": access_levels
        }

        return True

    def rename_access_level(self, old_lvl, new_lvl):
        # Is the old level name nonempty and has a corresponding access level?
        if not old_lvl or old_lvl not in self.access_levels:
            raise Exception(
                "The access level you are trying to rename does not exist. Please choose an existing access level."
            )

        # Is the new level name nonempty?
        if not new_lvl:
            raise Exception("Name cannot be empty. Please input at least one character")

        # Is the new level name different from the old level name?
        if new_lvl == old_lvl:
            raise Exception(
                "The new name is the same as the old one. Please input a new name."
            )

        # Is there no existing access level that already has the new name?
        if new_lvl in self.access_levels:
            raise Exception(
                "The provided name already exists in the access level list. Please input a new name."
            )

        if new_lvl.lower() == "unassigned":
            raise Exception("'Unassigned' is a reserved system level")

        # Change the access level name
        idx = self.access_levels.index(old_lvl)
        self.access_levels[idx] = new_lvl

        # Cascade change to users
        for uid, udata in self.users.items():
            if udata["access_level"] == old_lvl:
                udata["access_level"] = new_lvl

        # Cascade change to files
        for fid, document in self.documents.items():
            if old_lvl in document["access_levels"]:
                document["access_levels"][document["access_levels"].index(old_lvl)] = new_lvl

        return True

    def update_user(self, old_uid, new_uid, new_pwd, new_lvl):
        # Is the old user ID nonempty and has a corresponding user?
        if not old_uid or old_uid not in self.users:
            raise Exception(
                "The user you are trying to rename does not exist. Please select an already existing user."
            )

        # Is the new user ID and access level nonempty?
        if not new_uid or not new_lvl:
            raise Exception("Name cannot be empty. Please input at least one character")

        # Note that the password is NOT checked for nonemptiness.
        # That's because this function interprets an empty password field as retaining the current password.

        # If the user ID is being changed, is the new user ID unique?
        if new_uid != old_uid and new_uid in self.users:
            raise Exception(
                "The provided username already exists in the user list. Please input a new name."
            )

        old_hash = self.users[old_uid]["password_hash"]
        if new_uid != old_uid:
            del self.users[old_uid]

        self.users[new_uid] = {
            "password_hash": self.hash_password(new_pwd) if new_pwd else old_hash,
            "access_level": new_lvl,
        }
        return True

    def set_document_perms(self, doc_id, access_levels):
        # Is the document name and access level list nonempty?
        if not doc_id or not access_levels:
            raise Exception(
                "No access level selected. Please make sure that an entry in the access level list is selected."
            )

        # Does the document we are changing the permissions of exist?
        if doc_id not in self.documents:
            raise Exception("Please select an already existing document.")

        # TODO: Reject the document if access_levels contains the error access level

        self.documents[doc_id]["access_levels"] = access_levels
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
            uid for uid, udata in self.users.items() if udata["access_level"] == lvl
        ]

    def delete_access_level(self, lvl_to_delete):
        # Is the level name nonempty?
        if not lvl_to_delete:
            raise Exception("Please select an access level to delete.")

        # Does the access level exist?
        if lvl_to_delete not in self.access_levels:
            raise Exception(
                "The access level you are trying to delete does not exist. Please select an existing access level."
            )

        affected_users = self.get_users_with_access_level(lvl_to_delete)

        # Remove from backend's main access level list
        if lvl_to_delete in self.access_levels:
            self.access_levels.remove(lvl_to_delete)

        # Remove this access level from any documents through iteration
        for fid, doc in self.documents.items():
            if lvl_to_delete in doc["access_levels"]:
                doc["access_levels"].remove(lvl_to_delete)

            # If no access level remain, assign "Unassigned"
            if not doc["access_levels"]:
                doc["access_levels"] = ["Unassigned"]

        # Set affected users to "Unassigned"
        for uid in affected_users:
            self.users[uid]["access_level"] = "Unassigned"

        return True

    def delete_user(self, uid):
        # Is the user ID nonempty?
        if not uid:
            raise Exception("Please select a user to delete.")

        # Does the user exist?
        if uid not in self.users:
            raise Exception(
                "The user you are trying to delete does not exist. Please select an already existing user."
            )

        # Remove from user list and access control
        if uid in self.users:
            del self.users[uid]
        return True

    def delete_document(self, fid):
        # Is the document ID nonempty?
        if not fid:
            raise Exception("Please select a document.")

        # Does the document exist?
        if fid not in self.documents:
            raise Exception(
                "The document you are trying to delete does not exist. Please select an already existing document."
            )

        if fid in self.documents:
            del self.documents[fid]
        return True

    # JSON formatting helper
    def to_json(self, strip_paths = False):
        format = {
            "users": self.users.copy(),
            "files": self.documents.copy(),
            "access_levels": self.access_levels.copy(),
        }
        if strip_paths:
            for fid in format["files"]:
                # Copy to ensure we aren't destroying the archiver's copy of the ACM
                format["files"][fid] = format["files"][fid].copy()
                del format["files"][fid]["path"]
        return format

    # JSON loader
    def load_json(self, data):
        self.users = data.get("users", {})
        self.documents = data.get("files", {})
        self.access_levels = data.get("access_levels", [])
