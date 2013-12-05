# pylint: disable=trailing-whitespace, import-error, invalid-name
# pylint: disable=protected-access,
'''Test Module for id3 module'''

import unittest

import id3

#pylint: disable=too-many-public-methods
#above is a side-effect of using decorators.
class Test_ID3(unittest.TestCase):
    '''Tests the various ID3 classes'''
    
    def setUp(self):
        pass