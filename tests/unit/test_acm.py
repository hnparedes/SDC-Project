

import pytest
from sdc_common_module.acm import AccessControlMatrix


def test_add_access_level():
    acm = AccessControlMatrix()
    # Access levels with properly formatted names should be accepted
    assert acm.add_access_level("test")

    # Access levels with nonunique names should be rejected
    with pytest.raises(Exception, match=r".*given name.*"):
        acm.add_access_level("test")
    # assert not acm.add_access_level("test")

    # Access levels with empty names should be rejected
    with pytest.raises(Exception, match=r".*be empty.*"):
        acm.add_access_level("")

    # Access levels with forbidden names should be rejected
    with pytest.raises(Exception, match=r".*Unassigned.*"):
        acm.add_access_level("Unassigned")


def test_rename_access_level():
    acm = AccessControlMatrix()

    # Renaming an access level with a properly formatted name should succeed
    acm.add_access_level("test")
    assert acm.rename_access_level("test", "test_renamed")

    # Renaming an access level with a nonunique name should fail
    acm.add_access_level("test_a")
    acm.add_access_level("test_b")
    with pytest.raises(Exception, match=r".*already exists.*"):
        acm.rename_access_level("test_a", "test_b")

    # Renaming an empty access level should fail
    with pytest.raises(Exception, match=r".*does not exist.*"):
        acm.rename_access_level("", "something")

    # Renaming a nonexistent access level should fail
    with pytest.raises(Exception, match=r".*does not exist.*"):
        acm.rename_access_level("nonexistent", "nonexistent_renamed")

    # Renaming an access level to an empty name should fail
    acm.add_access_level("test_c")
    with pytest.raises(Exception, match=r".*cannot be empty.*"):
        acm.rename_access_level("test_c", "")

    # Renaming an access level to a forbidden name should fail
    acm.add_access_level("test_d")
    with pytest.raises(Exception, match=r".*Unassigned.*"):
        acm.rename_access_level("test_d", "Unassigned")


def test_access_level_rename_propagation():
    acm = AccessControlMatrix()

    acm.add_access_level("test")
    acm.add_user("user", "password", "test")
    acm.add_document("document", ["test"])

    acm.rename_access_level("test", "test_renamed")

    # Users and documents should have their access level updated if it is renamed
    assert acm.users["user"]["access_level"] == "test_renamed"
    assert "test_renamed" in acm.documents["document"]["access_levels"]
    assert "test" not in acm.documents["document"]["access_levels"]


def test_delete_access_level():
    acm = AccessControlMatrix()

    acm.add_access_level("test")

    # Deleting an access level that exists should succeed
    assert acm.delete_access_level("test")

    # An access level should not remain in the access level list after being deleted
    assert "test" not in acm.access_levels

    # Deleting an access level with an empty name should fail
    with pytest.raises(Exception, match=r".*select.*"):
        acm.delete_access_level("")

    # Deleting a nonexistent access level should fail
    with pytest.raises(Exception, match=r".*does not exist.*"):
        acm.delete_access_level("nonexistent")


def test_access_level_delete_propagation():
    acm = AccessControlMatrix()

    acm.add_access_level("test")
    acm.add_access_level("test2")
    acm.add_user("user", "password", "test")
    acm.add_document("document", ["test", "test2"])
    acm.add_document("document2", ["test"])

    acm.delete_access_level("test")

    # Users should have their access level changed to "Unassigned" if it is deleted
    assert acm.users["user"]["access_level"] == "Unassigned"
    # Documents should have access levels removed from their access level list if they are deleted
    assert "test" not in acm.documents["document"]["access_levels"]
    # If a document's only access level is deleted, its access level list should be set to Unassigned
    assert "Unassigned" in acm.documents["document2"]["access_levels"]


def test_add_user():
    acm = AccessControlMatrix()
    acm.add_access_level("test")

    # Users with properly formatted usernames, passwords, and access levels should be accepted
    assert acm.add_user("user", "password", "test")

    # Users with duplicate usernames should not be accepted
    with pytest.raises(Exception, match=r".*already exists.*"):
        acm.add_user("user", "password", "test")

    # Users with empty usernames, passwords, or access levels should be rejected
    with pytest.raises(Exception, match=r".*empty.*"):
        acm.add_user("", "password", "test")
    with pytest.raises(Exception, match=r".*empty.*"):
        acm.add_user("user_a", "", "test")
    with pytest.raises(Exception, match=r".*empty.*"):
        acm.add_user("user_b", "password", "")


def test_update_user():
    acm = AccessControlMatrix()
    acm.add_access_level("test_a")
    acm.add_access_level("test_b")

    # Updating a user with a properly formatted username, password, and access level should succeed
    acm.add_user("user", "password", "test_a")
    assert acm.update_user("user", "user_renamed", "new_password", "test_b")

    # If a user is updated, the ACM should reflect the updated values
    assert "user_renamed" in acm.users
    assert "user" not in acm.users

    # Updating a user with a properly formatted password and access level without changing the username should succeed
    acm.add_user("user_a", "password", "test_a")
    assert acm.update_user("user_a", "user_a", "new_password", "test_b")

    # If an updated password is not provided, the old password should be kept
    acm.add_user("user_b", "password", "test_a")

    user_b_old_hash = acm.users["user_b"]["password_hash"]
    assert acm.update_user("user_b", "user_b_renamed", "", "test_b")
    assert acm.users["user_b_renamed"]["password_hash"] == user_b_old_hash

    # Updating a user with an empty username or access level should fail
    acm.add_user("user_c", "password", "test_a")
    with pytest.raises(Exception, match=r".*empty.*"):
        acm.update_user("user_c", "", "new_password", "test_b")
        acm.update_user("user_c", "user_c_renamed", "new_password", "")

    # Updating a user with a username that already exists should fail
    acm.add_user("user_d", "password", "test_a")
    acm.add_user("user_e", "password", "test_a")
    with pytest.raises(Exception, match=r".*already.*"):
        acm.update_user("user_d", "user_e", "new_password", "test_b")


def test_delete_user():
    acm = AccessControlMatrix()
    acm.add_access_level("test")
    acm.add_user("user", "password", "test")

    # Deleting a user that exists should succeed
    assert acm.delete_user("user")

    # A user should not remain in the user list after being deleted
    assert "user" not in acm.users

    # Deleting a user with an empty name should fail
    with pytest.raises(Exception, match=r".*select.*"):
        acm.delete_user("")

    # Deleting a nonexistent user should fail
    with pytest.raises(Exception, match=r".*does not exist.*"):
        acm.delete_user("nonexistent")


def test_add_document():
    acm = AccessControlMatrix()
    acm.add_access_level("test")

    # Documents with properly formatted names and access levels should be accepted
    assert acm.add_document("document", ["test"])

    # Documents with duplicate names should not be accepted
    with pytest.raises(Exception, match=r".*already in.*"):
        acm.add_document("document", ["test"])

    # Documents with empty names or access levels should not be accepted
    with pytest.raises(Exception, match=r".*are empty.*"):
        acm.add_document("", ["test"])
        acm.add_document("document_a", [])

    # Documents with forbidden access levels should not be accepted
    with pytest.raises(Exception, match=r".*reserved.*"):
        acm.add_document("document_b", ["Unassigned"])


def test_set_document_perms():
    acm = AccessControlMatrix()
    acm.add_access_level("test_a")
    acm.add_access_level("test_b")

    acm.add_document("document", ["test_a"])

    # Changing a document's permissions to a nonempty set of access levels should succeed
    assert acm.set_document_perms("document", ["test_b"])

    # Changing a document's permissions to an empty set of access levels should fail
    acm.add_document("document_a", ["test_a"])
    with pytest.raises(Exception, match=r".*No access.*"):
        acm.set_document_perms("document_a", [])

    # Changing the permissions of an empty document should fail
    with pytest.raises(Exception, match=r".*select.*"):
        acm.set_document_perms("", ["test_a"])

    # Changing the permissions of a nonexistent document should fail
    with pytest.raises(Exception, match=r".*select.*"):
        acm.set_document_perms("nonexistent", ["test_a"])


def test_delete_document():
    acm = AccessControlMatrix()
    acm.add_access_level("test")
    acm.add_document("document", ["test"])

    # Deleting a document that exists should succeed
    assert acm.delete_document("document")

    # A document should not remain in the document list after being deleted
    assert "document" not in acm.documents

    # Deleting a document with an empty name should fail
    with pytest.raises(Exception, match=r".*select.*"):
        acm.delete_document("")

    # Deleting a nonexistent document should fail
    with pytest.raises(Exception, match=r".*not exist.*"):
        acm.delete_document("nonexistent")

def test_to_json():
    acm = AccessControlMatrix()
    acm.add_access_level("test")
    acm.add_document("document", ["test"], "path")

    # Export the format without stripping file paths
    format = acm.to_json()

    # Path should not be stripped from the format dict
    assert "path" in format["files"]["document"]

    # Path should not be stripped from the ACM
    assert "path" in acm.documents["document"]

    # Export the format and strip file paths
    format = acm.to_json(True)

    # Path should be stripped from the format dict
    assert "path" not in format["files"]["document"]

    # Path should not be stripped from the ACM
    assert "path" in acm.documents["document"]
