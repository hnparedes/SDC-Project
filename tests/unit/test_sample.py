from sdc_archiver.archiver_backend import SDCArchiver
import os.path

testfilepath = "./tests/testfiles/"
testoutputpath = "./.test-output/"

def test_acm():
    archiver = SDCArchiver()

    # Test access level functionality

    # Access levels with properly formatted names should be accepted
    assert archiver.acm.add_access_level("level1")

    # Access levels with nonunique names should be rejected
    assert not archiver.acm.add_access_level("level1")

    # Access levels with empty names should be rejected
    assert not archiver.acm.add_access_level("")

    # Renaming an access level with a properly formatted name should succeed
    archiver.acm.add_access_level("level2")
    assert archiver.acm.rename_access_level("level2", "level2_renamed")

    # Renaming an access level with a nonunique name should fail
    archiver.acm.add_access_level("level3")
    archiver.acm.add_access_level("level4")
    assert not archiver.acm.rename_access_level("level3", "level4")

    # Renaming an empty access level should fail
    assert not archiver.acm.rename_access_level("", "something")

    # Renaming a nonexistent access level should fail
    assert not archiver.acm.rename_access_level("nonexistent", "nonexistent_renamed")

    # Renaming an access level to an empty name should fail
    archiver.acm.add_access_level("level5")
    assert not archiver.acm.rename_access_level("level5", "")

    # Test user functionality
    # TBA

    # Test document functionality
    # TBA

    username = "testuser"
    password = "password123"
    access_level = "testlevel"
    archiver.acm.add_user(username, password, access_level)

    testfile = testfilepath + "files/text_normal_1.txt"
    archiver.acm.documents[testfile] = [access_level]

    # Are passwords hashed consistently?
    assert archiver.acm.users[username]["password_hash"] == archiver.acm.hash_password(password)

    os.mkdir(testoutputpath)
    outputpath = testoutputpath + "output.7z"

    # Does exporting an archive create a file?
    archiver.export_archive(outputpath, "password")
    assert os.path.isfile(outputpath)
