from sdc_archiver.archiver_backend import SDCArchiver
import os.path

testfilepath = "./tests/testfiles/"
testoutputpath = "./.test-output/"

def test_acm():
	archiver = SDCArchiver()


	username = "testuser"
	password = "password123"
	access_level = "testlevel"
	archiver.acm.add_user(username, password, access_level)

	testfile = testfilepath + "files/text_normal_1.txt"
	archiver.acm.files[testfile] = [access_level]

	# Are passwords hashed consistently?
	assert archiver.acm.users[username]["password_hash"] == archiver.acm.hash_password(password)

	os.mkdir(testoutputpath)
	outputpath = testoutputpath + "output.7z"

	# Does exporting an archive create a file?
	archiver.export_archive(outputpath, "password")
	assert os.path.isfile(outputpath)
