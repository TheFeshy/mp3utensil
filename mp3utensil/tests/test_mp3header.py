# pylint: disable=import-error, invalid-name
# pylint: disable=too-many-public-methods
# Pylint options disabled due to poor Python 3 support.
'''Test Module for mp3protocol module'''

import unittest

class Test_MP3Header(unittest.TestCase):
    """Unit test class for MP3Header"""

    def setUp(self):
        pass

    def test_short_todo(self):
        """Test Method?"""
        #TODO: find some tests to do here? MP3Header
        pass

if __name__ == '__main__':
    import test_all #@UnresolvedImport
    test_all.run_tests([Test_MP3Header])
        