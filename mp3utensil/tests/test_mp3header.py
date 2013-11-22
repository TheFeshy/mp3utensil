'''Test Module for mp3protocol module'''

import unittest
import mp3header
import sys

class Test_MP3Header(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_short_version_spotcheck(self):
        self.assertEqual(mp3header.MP3Header.versions[2], "MPEG Version 2")
    
    def test_short_frequency_spotcheck(self):
        self.assertEqual(mp3header.MP3Header.frequencies[3][1], 48000)
    
    def test_short_bitrate_spotcheck(self):
        self.assertEqual(mp3header.MP3Header.kbitrates[3][1][9], 128)
        
    def test_short_quick_accept(self):
        h = mp3header.Header_struct()
        h.d = int.from_bytes((0xFF,0xFA,0xA9,0x0F), sys.byteorder)
        valid = mp3header.MP3Header.quick_test(h.h)
        self.assertTrue(valid)
        
    def test_short_quick_reject(self):
        h = mp3header.Header_struct()
        h.d = int.from_bytes((0xAF,0xFA,0xA9,0x0F), sys.byteorder)
        valid = mp3header.MP3Header.quick_test(h.h)
        self.assertFalse(valid)
        
    def test_short_framesize_spotcheck(self):
        h = mp3header.Header_struct()
        h.d = int.from_bytes((0xFF,0xFA,0xA9,0x0F), sys.byteorder)
        head = mp3header.MP3Header(h)
        self.assertEqual(head.get_framesize(), 720)
        
    def test_short_frametime_spotcheck(self):
        h = mp3header.Header_struct()
        h.d = int.from_bytes((0xFF,0xFA,0xA9,0x0F), sys.byteorder)
        head = mp3header.MP3Header(h)
        self.assertAlmostEqual(head.get_frame_time(), 36.0, delta=0.1)