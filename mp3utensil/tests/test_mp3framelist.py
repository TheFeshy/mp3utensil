# pylint: disable=import-error
# pylint: disable=too-many-public-methods, invalid-name
"""Test Module for mp3frame module"""

import unittest

class Test_MP3FrameList(unittest.TestCase):
    """Test suite for the MP3Frame module"""

    def setUp(self):
        pass

    def test_short_init(self):
        """Test method???"""
        #TODO: find some testing to do here (MP3FrameList)?
        self.assertTrue(True)

if __name__ == '__main__':
    import test_all #@UnresolvedImport
    test_all.run_tests([Test_MP3FrameList])
    