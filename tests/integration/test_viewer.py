import os.path
import time

import pytest
from sdc_viewer.viewer_backend import SDCViewer

testfilepath = "./tests/testfiles/"
testoutputpath = "./.test-output/"

# This test uses the normalsdc.7z test archive for testing.
# See normalsdc.txt for documentation on the contents of this test archive.
def test_viewer():
    viewer = SDCViewer()

    testarchivelocation = testfilepath + "sdcs/normalsdc.7z"
    # The viewer should fail attempting to open an archive that doesn't exit
    with pytest.raises(Exception):
        viewer.open_archive("nowhere", "password")

    # The viewer should fail attempting to open an archive using the wrong password
    with pytest.raises(Exception):
        viewer.open_archive(testarchivelocation, "wrongpassword")

    # The viewer should succeed attempting to open an archive using the correct password
    assert viewer.open_archive(testarchivelocation, "sonormal")

    # Logging in as a nonexistent user should fail
    assert not viewer.login("nonexistent", "opensesame")

    # Logging in with the incorrect password should fail
    assert not viewer.login("bob", "wrongpassword")

    # Logging in with the correct password should succeed
    assert viewer.login("bob", "opensesame")

    # The user should only be able to see the documents available to their access level
    assert viewer.get_accessible_files() == ["text_normal_1.txt", "text_normal_2.txt"]

    # Create a test folder to output extracted documents into
    extractionoutputpath = testoutputpath + "test_viewer" + time.strftime("%Y%m%d-%H%M%S") + "/"
    os.makedirs(extractionoutputpath, exist_ok=True)

    # Extracting a document that is not in the archive should fail
    with pytest.raises(Exception):
        viewer.extract_document("nonexistent", extractionoutputpath + "nonexistent")

    # Extracting a document that the user does not have permissions for should fail
    with pytest.raises(Exception):
        viewer.extract_document("text_normal_3.txt", extractionoutputpath + "text_normal_3.txt")

    # The error for nonexistent documents and documents with insufficient permissions should be identical
    try:
        # Get the error message for a document that doesn't exist
        viewer.extract_document("nonexistent_1", extractionoutputpath + "nonexistent_1")
        assert False
    except Exception as e1:
        try:
            # Get the error message for a document without permission to access
            viewer.acm.add_document("nonexistent_1", ["admin"])
            viewer.extract_document("nonexistent_1", extractionoutputpath + "nonexistent_1")
            assert False
        except Exception as e2:
            assert str(e1) == str(e2), "Error message for trying to access a nonexistent document and a document with insufficient permission to access are different"

    # Extracting a document that the user does have permissions for should succeed
    assert viewer.extract_document("text_normal_2.txt", extractionoutputpath + "text_normal_2.txt")

    # The contents of a document extracted from the archive should be correct
    assert "Lorem ipsum dolor sit amet." in open(extractionoutputpath + "text_normal_2.txt").read()
