# pylint: disable=trailing-whitespace, import-error, old-style-class, 
# pylint: disable=no-self-use
# Pylint options disabled due to poor Python 3 support.

"""Helper module for test cases.  This generates sample mp3 files for
   use in unit testing."""
   
import tempfile
import random
import os
from copy import copy

import mp3header

class SampleMP3File():
    """Class to wrap a NamedTempFile and give it mp3 frame utility functions"""
    _RANGES = {'version':2, 
               'layer':2, 
               'crc_flag':1,
               'bitrate':4,
               'frequency':2,
               'padding_flag':1,
               'private_flag':1,
               'channel':2,
               'mode_extension':2,
               'copyright_flag':1,
               'original_flag':1,
               'emphasis':2}
    _DEFAULT = {'version':None, 
               'layer':None, 
               'crc_flag':None,
               'bitrate':None,
               'frequency':None,
               'padding_flag':None,
               'private_flag':None,
               'channel':None,
               'mode_extension':None,
               'copyright_flag':None,
               'original_flag':None,
               'emphasis':None}
    _INVALID = {'version':1,
                'layer':0,
                'bitrate':15,
                'frequency':3,
                'emphasis':2}
    def __init__(self):
        self.file = tempfile.NamedTemporaryFile(delete=False)
        self.name = None
        self.last_header = None
        
    def add_bytes(self, length):
        """Adds length number of random bytes to the file"""
        random_bytes = [random.randint(0,255) for _ in range(length)]
        self.file.write(bytes(random_bytes))
        
    def add_char(self, char):
        """Adds a single given byte to the file."""
        self.file.write(bytes((char,)))
        
    def add_string(self, string, size):
        """adds a string as ascii bytes to the file"""
        for character in string:
            self.add_char(ord(character))
        for _ in range(size - len(string)):
            self.add_char(0)

#pylint: disable=too-many-arguments        
    def add_id3v1_tag(self,title='',artist='',album='',year='',
                      comment='',track=None,genre=''):
        """Make sure these tags do not exceed the allowed lenghts (usually
           30 bytes) as this is a testing class and no real checking is done."""
        self.add_string("TAG",3)
        self.add_string(title, 30)
        self.add_string(artist,30)
        self.add_string(album,30)
        self.add_string(year,4)
        comment_size = 30
        if track:
            comment_size = 28
        self.add_string(comment,comment_size)
        if track:
            self.add_char(0)
            self.add_char(track)
        self.add_string(genre,1)
        

#pylint:disable=too-many-branches
#Unfortunately the struct methods aren't indexable!        
    def _update_header_field(self, header_struct, key, value):
        """Updates a single header field of a given HeaderStruct"""
        if "seek_tag" == key:
            header_struct.h.seek_tag = value
        elif "version" == key:
            header_struct.h.version = value
        elif "layer" == key:
            header_struct.h.layer = value
        elif "crc_flag" == key:
            header_struct.h.crc_flag = value
        elif "bitrate" == key:
            header_struct.h.bitrate = value
        elif "frequency" == key:
            header_struct.h.frequency = value
        elif "padding_flag" == key:
            header_struct.h.padding_flag = value
        elif "private_flag" == key:
            header_struct.h.private_flag = value
        elif "channel" == key:
            header_struct.h.channel = value
        elif "mode_extension" == key:
            header_struct.h.extension = value
        elif "copyright_flag" == key:
            header_struct.h.copyright_flag = value
        elif "original_flag" == key:
            header_struct.h.original_flag = value
        elif "emphasis" == key:
            header_struct.h.emphasis = value
            
    def add_header(self, header_dict=None):
        """Writes a given (or random) header to the temp file."""
        h_dict = header_dict or SampleMP3File._DEFAULT
        header_s = mp3header.HeaderStruct()
        header_s.h.seek_tag = 2047
        for i in self._RANGES.keys():
            if None == h_dict[i]:
                self._update_header_field(header_s, i, 
                                          random.getrandbits(self._RANGES[i]))
            else:
                self._update_header_field(header_s, i, h_dict[i])
                #header_s.header_s[i] = h_dict[i]
        self.last_header = h_dict
        self.file.write(header_s.h)
        return header_s
    
    def add_frame(self, header_dict=None):
        """Adds a frame based on the header given.
           The frame need not be valid.  Any values not present in the header
           will be randomly generated."""
        header_dict = header_dict or SampleMP3File._DEFAULT
        header_s = self.add_header(header_dict)
        tables = mp3header.HeaderStruct
        kbitrate = tables.kbitrates[header_s.h.version][header_s.h.layer]\
                                   [header_s.h.bitrate]
        samplebits = tables.samples[header_s.h.version][header_s.h.layer]
        frequency = tables.frequencies[header_s.h.version][header_s.h.frequency]
        padding = header_s.h.padding_flag
        if 3 == header_s.h.layer:
            padding = padding << 2 #is 4 bytes /w layer 1, 1 byte /w 2 & 3
        try:
            framesize = ((kbitrate * 125 * samplebits) // frequency) + padding
        except TypeError:
            framesize = 0
        self.add_bytes(framesize-4) #four bytes for header
        
    def add_valid_frame(self, header_dict=None):
        """Adds a valid frame based on the given header.  Any values not
           specified in the given header will be randomly generated, but
           will result in a valid header."""
        h_dict = header_dict or SampleMP3File._DEFAULT
        for i in SampleMP3File._INVALID.keys():
            while None == h_dict[i] or h_dict[i] == SampleMP3File._INVALID[i]:
                h_dict[i] = random.getrandbits(self._RANGES[i])
        #bitrate has two values we don't support.  Hacky, but only a test class
        while h_dict['bitrate'] == 0 or h_dict['bitrate'] == 15: 
            h_dict['bitrate'] = random.getrandbits(self._RANGES['bitrate'])
        self.add_frame(h_dict)
        
    def add_valid_frames(self, count=1, header_dict=None):
        """Adds multiple valid frames, all based on a single header."""
        h_dict = header_dict or SampleMP3File._DEFAULT
        if count >= 1:
            self.add_valid_frame(h_dict)
            h_dict = self.last_header
            count -= 1
            for _ in range(count):
                self.add_valid_frame(h_dict)
                
    def add_mixed_valid_frames(self, count=1, header_dict=None):
        """Adds multiple valid frames, but randomly generates each frame
           separately."""
        h_dict = header_dict or SampleMP3File._DEFAULT
        for _ in range(count):
            self.add_valid_frame(h_dict)
            
    def get_default_header(self):
        """Gives a copy of the default header, so we can change the fields
           that interest us."""
        return copy(SampleMP3File._DEFAULT)
    
    def get_file(self):
        """Gets the file (closes it first, so assumes you are now going to
           use the file for testing."""
        self.file.delete=False
        self.name = self.file.name
        self.file.close()
        return self.name
    
    def __del__(self):
        """Attempts to clean up the temp file.  Doesn't always work; no
           checking is done."""
        if self.name:
            os.remove(self.name)
    
    def get_size(self):
        """Only valid if we haven't gotten the file yet."""
        return self.file.tell()   
        