import os.path
import time
from sdc_viewer.viewer_backend import SDCViewer

testfilepath = "./tests/testfiles/"
testoutputpath = "./.test-output/"

def test_viewer():
    viewer = SDCViewer()
