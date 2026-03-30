from sdc_archiver.archiver_backend import SDCArchiver

def test_acm():
	archiver = SDCArchiver()

	username = "testuser"
	password = "password123"
	access_level = "testlevel"
	archiver.acm.add_user(username, password, access_level)

	# Are passwords hashed consistently?
	assert archiver.acm.users[username]["password_hash"] == archiver.acm.hash_password(password)
