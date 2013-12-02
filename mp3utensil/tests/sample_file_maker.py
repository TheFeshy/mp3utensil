# pylint: disable=trailing-whitespace, import-error
# Pylint options disabled due to poor Python 3 support.

"""Helper module for test cases.  This generates sample mp3 files for
   use in unit testing."""
   
import tempfile
import random
import os
from copy import copy

import mp3header

class SampleMP3File():
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
        r = []
        for i in range(length):
            r.append(random.randint(0,255))
        self.file.write(bytes(r))
        
    def add_char(self, char):
        self.file.write(bytes((char,)))
        
    def _update_header_field(self, header_struct, key, value):
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
            
    def add_header(self, header_dict=_DEFAULT):
        h_dict = copy(header_dict)
        h = mp3header.HeaderStruct()
        h.h.seek_tag = 2047
        for i in self._RANGES.keys():
            if None == h_dict[i]:
                self._update_header_field(h, i, random.getrandbits(self._RANGES[i]))
            else:
                self._update_header_field(h, i, h_dict[i])
                #h.h[i] = h_dict[i]
        self.last_header = h_dict
        self.file.write(h.h)
        return h
    
    def add_frame(self, header_dict=_DEFAULT):
        h = self.add_header(header_dict)
        _TABLES = mp3header.HeaderStruct
        kbitrate = _TABLES.kbitrates[h.h.version][h.h.layer][h.h.bitrate]
        samplebits = _TABLES.samples[h.h.version][h.h.layer]
        frequency = _TABLES.frequencies[h.h.version][h.h.frequency]
        padding = h.h.padding_flag
        if 3 == h.h.layer:
            padding = padding << 2 #is 4 bytes /w layer 1, 1 byte /w 2 & 3
        framesize = ((kbitrate * 125 * samplebits) // frequency) + padding
        self.add_bytes(framesize-4) #four bytes for header
        
    def add_valid_frame(self, header_dict=_DEFAULT):
        h_dict = copy(header_dict)
        for i in SampleMP3File._INVALID.keys():
            while None == h_dict[i] or h_dict[i] == SampleMP3File._INVALID[i]:
                h_dict[i] = random.getrandbits(self._RANGES[i])
        while h_dict['bitrate'] == 0 or h_dict['bitrate'] == 15: #bitrate has two values we don't support.
            h_dict['bitrate'] = random.getrandbits(self._RANGES['bitrate'])
        self.add_frame(h_dict)
        
    def add_valid_frames(self, count=1, header_dict=_DEFAULT):
        h_dict = copy(header_dict)
        if count >= 1:
            self.add_valid_frame(h_dict)
            h_dict = self.last_header
            count -= 1
            for i in range(count):
                self.add_valid_frame(h_dict)
                
    def add_mixed_valid_frames(self, count=1, header_dict=_DEFAULT):
        h_dict = copy(header_dict)
        for i in range(count):
            self.add_valid_frame(h_dict)
            
    def get_default_header(self):
        return copy(SampleMP3File._DEFAULT)
    
    def get_file(self):
        self.file.delete=False
        self.name = self.file.name
        self.file.close()
        return self.name
    
    def __del__(self):
        if self.name:
            os.remove(self.name)
    
    def get_size(self):
        """Only valid if we haven't gotten the file yet."""
        return self.file.tell()
        
if __name__ == '__main__':
    temp = SampleMP3File()
    temp.add_valid_frame()
    
    
    temp.file.seek(0,0)
    print(temp.file.read())
        
                
        
        