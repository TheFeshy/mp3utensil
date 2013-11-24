# pylint: disable=trailing-whitespace, import-error
# pylint: disable=too-many-public-methods, invalid-name
'''Test Module for mp3frame module'''

import unittest
import sys

import mp3frame
import mp3header

class Test_MP3Frame(unittest.TestCase):
    """Test suite for the MP3Frame module"""
    
    def setUp(self):
        pass
    
    def test_short_init(self):
        """Tests the MP3Frame's init method"""
        h_struct = mp3header.HeaderStruct()
        h_struct.d = int.from_bytes((0xFF,0xFA,0xA9,0x0F), sys.byteorder)
        frame = mp3frame.MP3Frame(h_struct, 0)
        self.assertEqual(frame.length, 720)
        h_struct.d = int.from_bytes((0xFF,0xFA,0x51,0x0F), sys.byteorder)
        frame = mp3frame.MP3Frame(h_struct, 0)
        self.assertEqual(frame.length, 208)
        