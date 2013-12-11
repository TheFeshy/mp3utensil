# pylint: disable=trailing-whitespace, import-error, invalid-name
# pylint: disable=protected-access, line-too-long
'''Test Module for id3 module'''

import unittest
import config
import mp3file
import id3v2
from sample_file_maker import SampleMP3File #@UnresolvedImport

#pylint: disable=too-many-public-methods
#above is a side-effect of using decorators.
class Test_ID3v2x(unittest.TestCase):
    def test_short_01_init(self):
        pass
    pass

def test_me():
    """Runs unit tests for the associated module"""
    import test_all #@UnresolvedImport
    test_all.run_tests([Test_ID3v2x])
    
if __name__ == '__main__':
    test_me()