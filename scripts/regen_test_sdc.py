import os.path

from sdc_archiver.archiver_backend import SDCArchiver

test_file_path = "./tests/testfiles/"

# Regenerates normalsdc.7z and normalacm.json
archiver = SDCArchiver()

archiver.acm.add_access_level("admin")
archiver.acm.add_access_level("privileged")
archiver.acm.add_access_level("default")

archiver.acm.add_user("alice", "letmein", "admin")
archiver.acm.add_user("bob", "opensesame", "privileged")
archiver.acm.add_user("charles", "password", "default")

archiver.acm.add_document("text_normal_1.txt", ["admin", "privileged", "default"], test_file_path + "files/text_normal_1.txt",)
archiver.acm.add_document("text_normal_2.txt", ["admin", "privileged"], test_file_path + "files/text_normal_2.txt",)
archiver.acm.add_document("text_normal_3.txt", ["admin"], test_file_path + "files/text_normal_3.txt",)

# Export draft archive
draft_output_path = test_file_path + "drafts/"
os.makedirs(draft_output_path, exist_ok=True)

draft_path = draft_output_path + "normalacm.json"
archiver.save_draft(draft_path)

# Export archive
archive_output_path = test_file_path + "sdcs/"
os.makedirs(archive_output_path, exist_ok=True)

archive_path = archive_output_path + "normalsdc.7z"
archiver.export_archive(archive_path, "sonormal")
