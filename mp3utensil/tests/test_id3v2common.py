# pylint: disable=trailing-whitespace, import-error, invalid-name
# pylint: disable=protected-access, line-too-long
'''Test Module for id3v2common'''

import unittest
import id3v2common

#pylint: disable=too-many-public-methods
#above is a side-effect of using decorators.
class Test_ID3v2Common(unittest.TestCase):
    def test_short_01_read(self):
        testdata = bytes([1,255])
        self.assertEqual(id3v2common.read_non_syncsafe(0, testdata, 2), 511, "Failed to read normal int")
        testdata = bytes([3,127])
        self.assertEqual(id3v2common.read_syncsafe(0, testdata, 2),511, "Failed to read syncsafed int")
        testdata = bytes([9,255])
        self.assertRaises(ValueError, id3v2common.read_syncsafe, 0, testdata, 2)
        
    def test_short_02_write(self):
        self.assertEqual(id3v2common.write_normal(511, 2), bytes([1,255]), "failed to convert an int to non-syncsafed bytes")
        self.assertEqual(id3v2common.write_syncsafe(511, 2), bytes([3,127]), "failed to convert an int to syncsafed bytes")
        self.assertRaises(ValueError, id3v2common.write_syncsafe, 511, 1)
        
    
def test_me():
    """Runs unit tests for the associated module"""
    try:
        import test_all #@UnresolvedImport
    except ImportError:
        import tests.test_all as test_all
    test_all.run_tests([Test_ID3v2Common])
    
    
if __name__ == '__main__':
    test_me()