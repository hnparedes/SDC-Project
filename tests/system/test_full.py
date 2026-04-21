import os.path
import time

import pytest
from sdc_archiver.archiver_backend import SDCArchiver
from sdc_viewer.viewer_backend import SDCViewer

testfilepath = "./tests/testfiles/"
test_output_path = "./.test-output/"

# Simulates a full session of use of the SDC Suite, using all features of both programs.
# This test only attempts valid inputs. No errors should occur while this test runs.
def test_full():
	archiver = SDCArchiver()

	# Add some access levels
	archiver.acm.add_access_level("admin")
	# The typo is intentional
	archiver.acm.add_access_level("privlieged")
	archiver.acm.add_access_level("default")
	archiver.acm.add_access_level("guest")

	# Add some users
	archiver.acm.add_user("alice", "letmein", "privlieged")
	archiver.acm.add_user("bpb", "opensesame", "privlieged")
	archiver.acm.add_user("charles", "N!t7'^q>3{;8/52WnXIf", "default")
	archiver.acm.add_user("delilah", "guess", "admin")

	# Add some documents
	archiver.acm.add_document("text_normal_1.txt", ["admin", "privlieged", "default", "guest"], testfilepath + "files/text_normal_1.txt",)
	archiver.acm.add_document("text_normal_2.txt", ["admin", "privlieged", "default"], testfilepath + "files/text_normal_2.txt",)
	archiver.acm.add_document("text_normal_3.txt", ["admin"], testfilepath + "files/text_normal_3.txt",)
	archiver.acm.add_document("text_normal_4.txt", ["admin", "privlieged"], testfilepath + "files/text_normal_4.txt",)

	# Oops, some of the data we entered into the archiver is wrong.
	# Let's test a bunch of ACM functions:

	# Simulate a user trying to fumble around to fix an error:
	# I need to correct a typo in an access level name
	archiver.acm.add_access_level("privileged")
	# Wait, that isn't what I wanted to do. I wanted to rename the misspelled access level
	# For some reason it won't let me name it 'privileged'
	archiver.acm.rename_access_level("privlieged", "privilged")
	# Oh wait, I need to delete the new one I made.
	archiver.acm.delete_access_level("privileged")
	# Someone's going to get fired for this
	archiver.acm.rename_access_level("privilged", "privileged")

	# Delete an access level that we didn't need
	archiver.acm.delete_access_level("guest")

	# Whoops, Bob misspelled his name. I think I know who's getting fired.
	# We don't need to change his password, though
	archiver.acm.update_user("bpb", "bob", "", "privileged")

	# After removing the guest access level, text_normal_3.txt is unassigned. Let's fix that
	archiver.acm.set_document_perms("text_normal_3.txt", ["default"])

	# We're done updating the ACM, so let's export the archive
	archive_output_path = test_output_path + "test_full" + time.strftime("%Y%m%d-%H%M%S") + "/"
	os.makedirs(archive_output_path, exist_ok=True)

	archive_path = archive_output_path + "normalsdc.7z"
	archiver.export_archive(archive_path, "sonormal")

	# Now let's abuse saving, loading, and exporting a bit and make sure nothing breaks.

	# The user might export the ACM multiple times in one session, and this shouldn't cause problems
	archiver.export_archive(archive_path, "sonormal")

	# Let's save a draft archive too
	draft_path = archive_output_path + "normalacm.json"
	archiver.save_draft(draft_path)

	# Open the draft in a new instance of the archiver, because we forgot some things
	archiver2 = SDCArchiver()
	archiver2.load_draft(draft_path)

	# Turns out Charlie prefers going by his nickname, let's update his username
	# He also forgot his password, and asked to change it to something easier-to-remember
	archiver2.acm.update_user("charles", "charlie", "password", "default")

	# Delilah left the project, so let's remove her from the ACM
	archiver2.acm.delete_user("delilah")

	# Alice got promoted after Delilah left, so she's taking over the admin role
	archiver2.acm.update_user("alice", "alice", "", "admin")

	# Our legal team found out text_normal_4.txt has copyrighted content, so it must be removed
	archiver2.acm.delete_document("text_normal_4.txt")

	# Alright, now let's save the draft and export the archive again
	archiver2.export_archive(archive_path, "sonormal")
	archiver2.save_draft(draft_path)

	# The user might export the ACM multiple times in one session, and this shouldn't cause problems
	archiver.export_archive(archivepath, "sonormal")

	# Now that the archive is done, let's test the viewer.
	viewer = SDCViewer()

	# Open the archive
	viewer.open_archive(archive_path, "sonormal")

	# Bob is logging in
	viewer.login("bob", "opensesame")

	# Bob extracts text_normal_2.txt
	viewer.extract_document("text_normal_2.txt", archive_output_path + "text_normal_2.txt")

	# Bob closes the viewer
	viewer.close()

	# Bob confirms that the document was extracted properly by hastily reading the first line
	assert "Lorem ipsum dolor sit amet." in open(archive_output_path + "text_normal_2.txt").read()

	# Godspeed, Bob.
