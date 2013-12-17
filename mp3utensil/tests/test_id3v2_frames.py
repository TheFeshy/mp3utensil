# pylint: disable=import-error, invalid-name
# pylint: disable=protected-access, line-too-long
'''Test Module for id3v2 frames'''

from codecs import BOM_UTF16

import unittest
import config
import mp3file
import id3v2_frames

#pylint: disable=too-many-public-methods
#above is a side-effect of using decorators.
class Test_ID3v2xFrames(unittest.TestCase):
    def test_short_01_verion2_init_and_read_basic(self):
        """Tests the generic text frame for version 2 tags.  Because it uses
        the underlying generic frame as well, that is also tested."""
        frame = id3v2_frames.ID3v2_ID_Generic_Text(version=2)
        frame.name = "TP2"
        frame.data = "Artist Name"
        stuff = bytes(frame)
        frame2 = id3v2_frames.ID3v2_ID_Generic_Text(2, data=stuff)
        self.assertEqual(frame.data, frame2.data, "Frame write/read does not match")
        self.assertEqual(frame.name, 'TP2', "Frame name not saved properly")
        self.assertEqual(frame2.name, 'TP2', "Frame name not read properly")
        self.assertEqual(frame2.version, 2, "Frame version not read properly")
        #test using bytes for name (which we support)
        frame.name = bytes([84,80,49])
        stuff = bytes(frame)
        frame2 = id3v2_frames.ID3v2_ID_Generic_Text(2, data=stuff)
        self.assertEqual(frame2.name, 'TP1', "Frame name not handled properly when given as bytes")

    def test_short_02_version2_exception(self):
        """Tests for certain error conditions in v2 frames"""
        frame = id3v2_frames.ID3v2_ID_Generic_Text(version=2)
        frame.name = "NO"
        frame.data = "not tested"
        self.assertRaises(ValueError, frame.__bytes__)#name too short
        frame = id3v2_frames.ID3v2_ID_Generic_Text(version=2)
        frame.name = "NoNoNo"
        frame.data = "not tested"
        self.assertRaises(ValueError, frame.__bytes__)#name too long
        self.assertRaises(AttributeError, frame.__setattr__, "compressed_flag", True)

    def test_short_03_version2_unicode(self):
        """Tests v2 frame unicode support"""
        frame = id3v2_frames.ID3v2_ID_Generic_Text(version=2)
        frame.name = "TP2"
        frame.data = "Ūbür artist"
        stuff = bytes(frame)
        frame2 = id3v2_frames.ID3v2_ID_Generic_Text(2, data=stuff)
        self.assertEqual(frame.data, frame2.data, "Failed to read and write unicode data")
        self.assertEqual(BOM_UTF16, stuff[7:9], "Failed to write Unicode BOM")

    def test_short_04_version3_init_and_read(self):
        """Tests the generic text frame for version 3 tags.  Because it uses
        the underlying generic frame as well, that is also tested."""
        frame = id3v2_frames.ID3v2_ID_Generic_Text(version=3)
        frame.name = "TPE1"
        frame.data = "Artist Name"
        stuff = bytes(frame)
        frame2 = id3v2_frames.ID3v2_ID_Generic_Text(3, data=stuff)
        self.assertEqual(frame.data, frame2.data, "Frame write/read does not match")
        self.assertEqual(frame.name, 'TPE1', "Frame name not saved properly")
        self.assertEqual(frame2.name, 'TPE1', "Frame name not read properly")
        self.assertEqual(frame2.version, 3, "Frame version not read properly")
        #test using bytes for name (which we support)
        frame.name = bytes([84,80,69,49])
        stuff = bytes(frame)
        frame2 = id3v2_frames.ID3v2_ID_Generic_Text(3, data=stuff)
        self.assertEqual(frame2.name, 'TPE1', "Frame name not handled properly when given as bytes")
        frame.data = "Long but easily compressible string easily compressible because string has duplicate strings"
        stuff2 = bytes(frame)
        frame.compressed_flag = True
        stuff = bytes(frame)
        self.assertLess(len(stuff), len(stuff2), "Failed to compress data")
        frame2 = id3v2_frames.ID3v2_ID_Generic_Text(3, data=stuff)
        self.assertEqual(frame.data, frame2.data, "Failed to make read/write round-trip with compressed frame")

    def test_short_99_previous_bugs(self):
        """Tests bugs we have found before so they don't come back"""
        frame = id3v2_frames.ID3v2_ID_Generic_Text(version=2)
        frame.data = "stuff"
        frame.name = "OKY"
        frame.__bytes__()
        temp = frame.data
        frame.name = "TRY"
        frame.__bytes__()
        temp2 = frame.data
        self.assertEqual(temp, temp2, "Data member being changed by __bytes__ method")

def test_me():
    """Runs unit tests for the associated module"""
    try:
        import test_all #@UnresolvedImport
    except ImportError:
        import tests.test_all as test_all
    test_all.run_tests([Test_ID3v2xFrames])


if __name__ == '__main__':
    test_me()
