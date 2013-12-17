# pylint: disable=import-error, invalid-name
# pylint: disable=protected-access, line-too-long
'''Test Module for mp3file module'''

import unittest
import random

import mp3file
import config
try:
    from sample_file_maker import SampleMP3File #@UnresolvedImport
except:
    from tests.sample_file_maker import SampleMP3File #@UnresolvedImport

#pylint: disable=too-many-public-methods
#above is a side-effect of using decorators.
class Test_MP3File(unittest.TestCase):
    """All the values that are tested for in this class are derived
       from the various 4k samples of mp3 files provided."""

    def setUp(self):
        """ Creates the necessary test data for each test."""
        self.savedopts = config.OPTS
        random.seed(1) #unit tests should be predictable; so let's use the same seed ech time.

    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_short_01_numpy_single_frame(self):
        """Tests ability to identify a file consisting of a single frame.
           Very basic test of frame identification."""
        config.OPTS.use_numpy = True
        self.single_frame()

    def test_short_02_python_single_frame(self):
        """Tests ability to identify a file consisting of a single frame.
           Very basic test of frame identification."""
        config.OPTS.use_numpy = False
        self.single_frame()

    def single_frame(self):
        """implimentation of above."""
        config.OPTS.consecutive_frames_to_id = 1 #only one frame in sample file
        temp = SampleMP3File()
        temp.add_valid_frame()
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(1, len(mfile.frames), "Found more or less than one frame")
        self.assertEqual(0, len(mfile.other), "Found data where there was none")
        self.assertEqual(0, mfile.frames[0][1], "Found frame at wrong position")

    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_medium_03_numpy_many_frames(self):
        """Tests a basic mp3 file with many frames but no "junk" data."""
        config.OPTS.use_numpy = True
        self.many_frames()

    def test_medium_04_python_many_frames(self):
        """Tests a basic mp3 file with many frames but no "junk" data."""
        config.OPTS.use_numpy = False
        self.many_frames()

    def many_frames(self):
        """implimentation of above."""
        config.OPTS.consecutive_frames_to_id = 3
        temp = SampleMP3File()
        temp.add_valid_frames(100)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(100, len(mfile.frames), "Found more or less than one frame")
        self.assertEqual(0, len(mfile.other), "Found data where there was none")
        self.assertEqual(0, mfile.frames[0][1], "Found frame at wrong position")

    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_short_05_numpy_two_frames_junk_before(self):
        """A short test case to identify junk before frames"""
        config.OPTS.use_numpy = True
        self.two_frames_junk_before()

    def test_short_06_python_two_frames_junk_before(self):
        """A short test case to identify junk before frames"""
        config.OPTS.use_numpy = False
        self.two_frames_junk_before()

    def two_frames_junk_before(self):
        """implimentation of above."""
        config.OPTS.consecutive_frames_to_id = 2 #only one frame in sample file
        temp = SampleMP3File()
        junk_amount = 128
        temp.add_bytes(junk_amount)
        temp.add_valid_frames(2)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(2, len(mfile.frames), "Found more or less than one frame")
        self.assertEqual(1, len(mfile.other), "Found data where there was none")
        self.assertEqual(junk_amount, mfile.frames[0][1], "Found frame at wrong position")
        self.assertEqual(0, mfile.other[0].position, "Junk found at wrong location")
        self.assertEqual(junk_amount, len(mfile.other[0]), "Junk found had wrong length")

    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_short_07_numpy_two_frames_junk_after(self):
        """A simple test to identify junk at the end of a file"""
        config.OPTS.use_numpy = True
        self.only_junk()

    def test_short_08_python_two_frames_junk_after(self):
        """A simple test to identify junk at the end of a file"""
        config.OPTS.use_numpy = False
        self.only_junk()

    def two_frames_junk_after(self):
        """implimentation of above."""
        config.OPTS.consecutive_frames_to_id = 2 #only one frame in sample file
        temp = SampleMP3File()
        junk_amount = 128
        temp.add_valid_frames(2)
        junk_start = temp.get_size()
        temp.add_bytes(junk_amount)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(2, len(mfile.frames), "Found more or less than one frame")
        self.assertEqual(1, len(mfile.other), "Found data where there was none")
        self.assertEqual(0, mfile.frames[0][1], "Found frame at wrong position")
        self.assertEqual(junk_start, mfile.other[0].position, "Junk found at wrong location")
        self.assertEqual(junk_amount, len(mfile.other[0]), "Junk found had wrong length")

    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_medium_09_numpy_only_junk(self):
        """Tests the pathological case of a file with no MP3 data."""
        config.OPTS.use_numpy = True
        self.only_junk()

    def test_medium_10_python_only_junk(self):
        """Tests the pathological case of a file with no MP3 data."""
        config.OPTS.use_numpy = False
        self.only_junk()

    def only_junk(self):
        """implimentation of above."""
        config.OPTS.consecutive_frames_to_id = 2 #only one frame in sample file
        temp = SampleMP3File()
        junk_amount = 16384
        temp.add_bytes(junk_amount)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(0, len(mfile.frames), "Found more or less than one frame")
        self.assertEqual(1, len(mfile.other), "Found data where there was none")
        self.assertEqual(0, mfile.other[0].position, "Junk found at wrong location")
        self.assertEqual(junk_amount, len(mfile.other[0]), "Junk found had wrong length")

    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_short_11_numpy_junk_middle(self):
        """Test to identify junk data within the mp3 stream"""
        config.OPTS.use_numpy = True
        self.junk_middle()

    def test_short_12_python_junk_middle(self):
        """Test to identify junk data within the mp3 stream"""
        config.OPTS.use_numpy = False
        self.junk_middle()

    def junk_middle(self):
        """implimentation of above."""
        config.OPTS.consecutive_frames_to_id = 3 #only one frame in sample file
        temp = SampleMP3File()
        junk_amount = 2007
        temp.add_valid_frame()
        temp.add_valid_frames(9, temp.last_header)
        junk_start = temp.get_size()
        temp.add_bytes(junk_amount)
        temp.add_valid_frames(10, temp.last_header)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(20, len(mfile.frames), "Found wrong number of frames")
        self.assertEqual(1, len(mfile.other), "Found data where there was none")
        self.assertEqual(0, mfile.frames[0][1], "Found frame at wrong position")
        self.assertEqual(junk_start, mfile.other[0].position, "Junk found at wrong location")
        self.assertEqual(junk_amount, len(mfile.other[0]), "Junk found had wrong length")

    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_medium_13_numpy_mixed_frames(self):
        """Test to identify mixed, but otherwise valid, MP3 frames"""
        config.OPTS.use_numpy = True
        self.mixed_frames()

    def test_medium_14_python_mixed_frames(self):
        """Test to identify mixed, but otherwise valid, MP3 frames"""
        config.OPTS.use_numpy = False
        self.mixed_frames()

    def mixed_frames(self):
        """implimentation of above."""
        config.OPTS.consecutive_frames_to_id = 2
        temp = SampleMP3File()
        temp.add_mixed_valid_frames(100)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(100, len(mfile.frames), "Found more or less than one frame")
        self.assertEqual(0, len(mfile.other), "Found data where there was none")
        self.assertEqual(0, mfile.frames[0][1], "Found frame at wrong position")

    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_medium_15_numpy_junk_all_three(self):
        """Test to identify junk in three locations within a file."""
        config.OPTS.use_numpy = True
        self.junk_all_three()

    def test_medium_16_python_junk_all_three(self):
        """Test to identify junk in three locations within a file."""
        config.OPTS.use_numpy = False
        self.junk_all_three()

    def junk_all_three(self):
        """implimentation of above."""
        config.OPTS.consecutive_frames_to_id = 3
        temp = SampleMP3File()
        junk_amount1 = 2007
        junk_amount2 = 5213
        junk_amount3 = 128
        temp.add_bytes(junk_amount1)
        temp.add_valid_frame()
        temp.add_valid_frames(9, temp.last_header)
        junk_start = temp.get_size()
        temp.add_bytes(junk_amount2)
        temp.add_valid_frames(10, temp.last_header)
        junk_start2 = temp.get_size()
        temp.add_bytes(junk_amount3)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(20, len(mfile.frames), "Found wrong number of frames")
        self.assertEqual(3, len(mfile.other), "Found data where there was none")
        self.assertEqual(junk_amount1, mfile.frames[0][1], "Found frame at wrong position")
        self.assertEqual(0, mfile.other[0].position, "Junk found at wrong location")
        self.assertEqual(junk_start, mfile.other[1].position, "Junk found at wrong location")
        self.assertEqual(junk_start2, mfile.other[2].position, "Junk found at wrong location")
        self.assertEqual(junk_amount1, len(mfile.other[0]), "Junk found had wrong length")
        self.assertEqual(junk_amount2, len(mfile.other[1]), "Junk found had wrong length")
        self.assertEqual(junk_amount3, len(mfile.other[2]), "Junk found had wrong length")

    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    @unittest.expectedFailure
    def test_short_17_numpy_short_frame_end(self):
        """Test to identify a "valid" frame that extends past the file as a short frame."""
        config.OPTS.use_numpy = True
        self.short_frame_end()

    @unittest.expectedFailure
    def test_short_18_python_short_frame_end(self):
        """Test to identify a "valid" frame that extends past the file as a short frame."""
        config.OPTS.use_numpy = False
        self.short_frame_end()

    def short_frame_end(self):
        """implimentation of above."""
        config.OPTS.consecutive_frames_to_id = 2
        temp = SampleMP3File()
        temp.add_valid_frames(3)
        junk_start = temp.get_size()
        header = temp.last_header
        temp.add_header(header)
        temp.add_bytes(9) #less than a full frame
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(3, len(mfile.frames), "Found more or less than one frame")
        self.assertEqual(1, len(mfile.other), "Found data where there was none")
        self.assertEqual(0, mfile.frames[0][1], "Found frame at wrong position")
        self.assertEqual(junk_start, mfile.other[0].position, "Junk found at wrong location")
        self.assertEqual(13, len(mfile.other[0]), "Junk found had wrong length")

    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    @unittest.expectedFailure
    def test_short_17_numpy_short_frame_middle(self):
        """This test attempts to identify a short frame in the middle of the file.
           This could happen if a file is split, has ID3v1 tag badly written to it,
           then is rejoined.  The short frame should be junk, while the long frame
           following it should be valid."""
        config.OPTS.use_numpy = True
        self.short_frame_middle()

    @unittest.expectedFailure
    def test_short_18_python_short_frame_middle(self):
        """This test attempts to identify a short frame in the middle of the file.
           This could happen if a file is split, has ID3v1 tag badly written to it,
           then is rejoined.  The short frame should be junk, while the long frame
           following it should be valid."""
        config.OPTS.use_numpy = False
        self.short_frame_middle()

    def short_frame_middle(self):
        """implimentation of above."""
        config.OPTS.consecutive_frames_to_id = 3
        temp = SampleMP3File()
        temp.add_valid_frames(10)
        junk_start = temp.get_size()
        header = temp.last_header
        temp.add_header(header)
        temp.add_bytes(9) #less than a full frame
        frame_restart = temp.get_size()
        temp.add_valid_frames(10, header)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(20, len(mfile.frames), "Found more or less frames")
        self.assertEqual(1, len(mfile.other), "Found data where there was none")
        self.assertEqual(0, mfile.frames[0][1], "Found first frame at wrong position")
        self.assertEqual(frame_restart, mfile.frames[10][1], "Didn't detect next full frame")
        self.assertEqual(junk_start, mfile.other[0].position, "Junk not found in correct location (junk is valid frame cut short)")
        self.assertEqual(13, len(mfile.other[0]), "Junk found had wrong length (junk i svalid frame cut short)")

    def test_short_19_python_extended_lockon_test(self):
        """Because the python code uses two different methods to lock on - one
           to skip large empty chunks and one to quickly parse frequent hits,
           we must test both by exceeding the limit of the first."""
        config.OPTS.consecutive_frames_to_id = 3
        config.OPTS.use_numpy = False
        temp = SampleMP3File()
        temp.add_valid_frames(5)
        junkstart = temp.get_size()
        for _ in range(mp3file._MAX_INDEX_METHOD_SEARCHES * 2):
            temp.add_bytes(11)
            temp.add_char(255)
        nextframe = temp.get_size()
        temp.add_valid_frames(5)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(nextframe, mfile.frames[5][1], "unable to find frame with secondary lockon method")
        self.assertEqual(junkstart, mfile.other[0].position, "junk foun in wrong location")
        self.assertEqual(24 * mp3file._MAX_INDEX_METHOD_SEARCHES, len(mfile.other[0]), "junk found was wrong size")

    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_short_20_numpy_identify_frame_after_false_seek(self):
        """Makes sure that false seek flags immediately before valid frame
           data are skipped as junk"""
        config.OPTS.use_numpy = True
        self.identify_frame_after_false_seek()

    def test_short_21_python_identify_frame_after_false_seek(self):
        """Makes sure that false seek flags immediately before valid frame
           data are skipped as junk"""
        config.OPTS.use_numpy = False
        self.identify_frame_after_false_seek()

    def identify_frame_after_false_seek(self):
        """Implimentation of above"""
        config.OPTS.consecutive_frames_to_id = 3
        temp = SampleMP3File()
        temp.add_char(255)
        temp.add_valid_frames(5)
        junkstart = temp.get_size()
        temp.add_char(255)
        temp.add_char(255)
        framestart = temp.get_size()
        temp.add_valid_frames(5)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(1, mfile.frames[0][1], "Didn't skip false seek byte")
        self.assertEqual(0, mfile.other[0].position, "junk #1 found in wrong location")
        self.assertEqual(junkstart, mfile.other[1].position, "junk #2 found in wrong location")
        self.assertEqual(2, len(mfile.other[1]), "junk was wrong length")
        self.assertEqual(framestart, mfile.frames[5][1], "Didn't skip 2 byte false seek tag")

    def tearDown(self):
        """restore opts"""
        config.OPTS = self.savedopts

if __name__ == '__main__':
    import test_all #@UnresolvedImport
    test_all.run_tests([Test_MP3File])
