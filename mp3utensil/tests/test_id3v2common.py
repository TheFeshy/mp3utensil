# pylint: disable=import-error, invalid-name
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

    def test_short_03_syncsafe(self):
        testval = bytearray((82,82,85,90,45,255,224,100))
        testval2 = bytearray((82,82,85,90,45,255,24,100))
        testval3 = bytearray((82,82,85,90,255,0,119))
        testval4 = bytearray((70,71,72,255,255,73,74,255,0,75))
        compareval = bytearray((82,82,85,90,45,255,0,224,100))
        compareval3 = bytearray((82,82,85,90,255,0,0,119))
        compareval4 = bytearray((70,71,72,255,0,255,73,74,255,0,0,75))
        self.assertEqual(compareval, id3v2common.syncsafe_data(testval), "Does't syncsafe data with false sync")
        self.assertEqual(testval, id3v2common.un_syncsafe_data(compareval), "failed to unsync data with false sync")
        self.assertEqual(testval2, id3v2common.syncsafe_data(testval2), "mangled data without sync bit")
        self.assertEqual(compareval3, id3v2common.syncsafe_data(testval3), "Didn't syncsafe zeros as required")
        self.assertEqual(testval3, id3v2common.un_syncsafe_data(compareval3), "Didn't unsyncsafe zeros as required")
        self.assertEqual(compareval4, id3v2common.syncsafe_data(testval4), "Didn't handle multiple bytes needing syncsafing")
        self.assertEqual(testval4, id3v2common.un_syncsafe_data(compareval4), "Didn't handle multiple bytes needing un-syncsafing")

def test_me():
    """Runs unit tests for the associated module"""
    try:
        import test_all #@UnresolvedImport
    except ImportError:
        import tests.test_all as test_all
    test_all.run_tests([Test_ID3v2Common])

if __name__ == '__main__':
    test_me()
