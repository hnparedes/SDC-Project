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
