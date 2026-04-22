import os.path
import time
from sdc_archiver.archiver_backend import SDCArchiver

testfilepath = "./tests/testfiles/"
testoutputpath = "./.test-output/"

def test_archiver():
    archiver = SDCArchiver()

    username = "testuser"
    password = "password123"
    access_level = "testlevel"
    archiver.acm.add_user(username, password, access_level)

    testfile = testfilepath + "files/text_normal_1.txt"
    archiver.acm.add_document("text_normal_1.txt", [access_level], testfile)

    # Are passwords hashed consistently?
    assert archiver.acm.users[username]["password_hash"] == archiver.acm.hash_password(
        password
    )

    try:
        os.mkdir(testoutputpath)
    except FileExistsError:
        pass

    archiveoutputpath = testoutputpath + "test_archiver" + time.strftime("%Y%m%d-%H%M%S") + "/"
    os.makedirs(archiveoutputpath, exist_ok=True)
    outputpath = archiveoutputpath + "output-.7z"

    # Does exporting an archive create a file?
    archiver.export_archive(outputpath, "password")
    assert os.path.isfile(outputpath)

def test_save_load():
    # Set up a basic SDC
    archiver = SDCArchiver()

    username = "testuser"
    password = "password123"
    access_level = "testlevel"
    archiver.acm.add_user(username, password, access_level)

    testfile = testfilepath + "files/text_normal_1.txt"
    archiver.acm.add_document("text_normal_1.txt", [access_level], testfile)

    outputpath = testoutputpath + "test_save_load" + time.strftime("%Y%m%d-%H%M%S") + "/"
    os.makedirs(outputpath, exist_ok=True)
    fileoutputpath = outputpath + "output.json"

    archiver.save_draft(fileoutputpath)

    archiver2 = SDCArchiver()
    archiver2.load_draft(fileoutputpath)

    # Make sure that the ACM's contents are identical after loading
    assert archiver2.acm.access_levels == archiver.acm.access_levels
    assert archiver2.acm.users == archiver.acm.users
    assert archiver2.acm.documents == archiver.acm.documents

    # Save and load again to make sure the ACM isn't damaged in any way
    archiver2.save_draft(fileoutputpath)

    archiver3 = SDCArchiver()
    archiver3.load_draft(fileoutputpath)

    assert archiver3.acm.access_levels == archiver.acm.access_levels
    assert archiver3.acm.users == archiver.acm.users
    assert archiver3.acm.documents == archiver.acm.documents
