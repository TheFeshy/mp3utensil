# pylint: disable=trailing-whitespace, import-error, invalid-name
# pylint: disable=protected-access, line-too-long
'''Test Module for id3 module'''

import unittest
import array
import config
from sample_file_maker import SampleMP3File #@UnresolvedImport
import mp3file

import id3

#pylint: disable=too-many-public-methods
#above is a side-effect of using decorators.
class Test_ID3(unittest.TestCase):
    '''Tests the various ID3 classes'''
    
    def setUp(self):
        pass
    
    def test_short_01_test_v1_init(self):
        """Test the init functions of the ID3v1x class"""
        ar = array.array('B', [84,65,71,]+ [0]*125)
        tag = id3.ID3v1x(ar)
        self.assertTrue(id3.heuristic_verify(ar), "Unable to verify blank tag")
        self.assertEqual(0, tag.subversion, "unable to verify tag version")
        ar[126] = 1 #give it a track
        tag = id3.ID3v1x(ar)
        self.assertTrue(id3.heuristic_verify(ar), "Unable to verify blank tag")
        self.assertEqual(1, tag.subversion, "unable to verify tag version")
        
    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_short_02_numpy_basic_id3_test(self):
        """Tests a file consisting of just one ID3 tag"""
        config.OPTS.use_numpy = True
        self.basic_id3_test()
        
    def test_short_03_python_basic_id3_test(self):
        """Tests a file consisting of just one ID3 tag"""
        config.OPTS.use_numpy = False
        self.basic_id3_test()
        
    def basic_id3_test(self):
        """implement of above"""
        config.OPTS.consecutive_frames_to_id = 3 
        temp = SampleMP3File()
        temp.add_id3v1_tag("a title","an artist", "an album")
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(1, len(mfile.other),"More than one tag found")
        self.assertEqual(id3.ID3v1x, type(mfile.other[0]), "failed to identify v1 tag")
        self.assertEqual(0, mfile.other[0].subversion, "Identified wrong subversion of tag")
        self.assertEqual(0, mfile.other[0].position, "failed to identify correct starting location")
        
    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_short_04_numpy_id3_frame_test(self):
        """Tests ID3 at the end of a small file"""
        config.OPTS.use_numpy = True
        self.id3_frame_test()
        
    def test_short_05_python_id3_frame_test(self):
        """Tests ID3 at the end of a small file"""
        config.OPTS.use_numpy = False
        self.id3_frame_test()
        
    def id3_frame_test(self):
        """implements above"""
        config.OPTS.consecutive_frames_to_id = 3 
        temp = SampleMP3File()
        temp.add_valid_frames(5)
        tagstart = temp.get_size()
        temp.add_id3v1_tag("a title","an artist", "an album")
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(1, len(mfile.other),"More than one tag found")
        self.assertEqual(id3.ID3v1x, type(mfile.other[0]), "failed to identify v1 tag")
        self.assertEqual(0, mfile.other[0].subversion, "Identified wrong subversion of tag")
        self.assertEqual(tagstart, mfile.other[0].position, "failed to identify correct starting location")
        
    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_short_06_numpy_id3_junk_test(self):
        """tests identifying mp3 with junk data before and after"""
        config.OPTS.use_numpy = True
        self.id3_junk_test()
        
    def test_short_07_python_id3_junk_test(self):
        """tests identifying mp3 with junk data before and after"""
        config.OPTS.use_numpy = False
        self.id3_junk_test()
        
    def id3_junk_test(self):
        """implements the above"""
        config.OPTS.consecutive_frames_to_id = 3 
        temp = SampleMP3File()
        temp.add_valid_frames(5)
        temp.add_bytes(10)
        tagstart = temp.get_size()
        temp.add_id3v1_tag("a title","an artist", "an album")
        temp.add_bytes(10)
        temp.add_valid_frames(5)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(3, len(mfile.other),"More than one tag found")
        self.assertEqual(id3.ID3v1x, type(mfile.other[0]), "failed to identify v1 tag")
        self.assertEqual(0, mfile.other[0].subversion, "Identified wrong subversion of tag")
        self.assertEqual(tagstart, mfile.other[0].position, "failed to idenitfy correct starting location")
        
    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_short_08_numpy_id3_1_1_test(self):
        """tests identifying version 1.1"""
        config.OPTS.use_numpy = True
        self.id3_1_1_test()
        
    def test_short_09_python_id3_1_1test(self):
        """tests identifying version 1.1"""
        config.OPTS.use_numpy = False
        self.id3_1_1_test()
        
    def id3_1_1_test(self):
        """impliments the above"""
        config.OPTS.consecutive_frames_to_id = 3 
        temp = SampleMP3File()
        temp.add_id3v1_tag("a title","an artist", "an album",track=5)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(1, len(mfile.other),"More than one tag found")
        self.assertEqual(id3.ID3v1x, type(mfile.other[0]), "failed to identify v1 tag")
        self.assertEqual(1, mfile.other[0].subversion, "Identified wrong subversion of tag")
        self.assertEqual(0, mfile.other[0].position, "failed to idenitfy correct starting location")
        
    @unittest.skipIf(not config.OPTS.use_numpy, "Numpy not available to test")
    def test_short_08_numpy_multiple_junk(self):
        """tests identifying version 1.1"""
        config.OPTS.use_numpy = True
        self.multiple_junk()
        
    def test_short_09_python_multiple_junk(self):
        """tests identifying version 1.1"""
        config.OPTS.use_numpy = False
        self.multiple_junk()
        
    def multiple_junk(self):
        """implements the above"""
        config.OPTS.consecutive_frames_to_id = 3 
        temp = SampleMP3File()
        temp.add_bytes(200)
        temp.add_valid_frames(5)
        tagstart = temp.get_size()
        temp.add_id3v1_tag("a title","an artist", "an album",track=5)
        mfile = mp3file.MP3File(temp.get_file())
        mfile.scan_file()
        self.assertEqual(2, len(mfile.other),"More than one tag found")
        tag = mfile.other[0]
        self.assertEqual(id3.ID3v1x, type(tag), "failed to identify v1 tag")
        self.assertEqual(1, tag.subversion, "Identified wrong subversion of tag")
        self.assertEqual(tagstart, tag.position, "failed to idenitfy correct starting location")
