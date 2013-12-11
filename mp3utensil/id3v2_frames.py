# pylint: disable=trailing-whitespace, old-style-class
"""This module implements all of the ID3v2.x frames"""

import zlib
from codecs import BOM_UTF16_BE

import id3v2common

class ID3v2_ID_Generic():
    """This is the frame base class, and also represents an unknown frame.
       Since we don't know anything about the nature of its contents, we 
       store it as bytes.  Derived classes can also call this class's 
       read_from_position method to read in all flags, and leave the bytes
       to be parsed in self.data"""
    def __init__(self, version, data=None):
        #Set some default values.
        self.version = version
        self.name = None
        self.tag_alter_discard = False
        self.file_alter_discard = False
        self.read_only = False
        self.compressed_flag = False
        self.encrypted_flag = False
        self.group_flag = False
        self.data_length_size = None
        self.encryption = None
        self.group = None
        self.data = None
        self.read_size = None
        self.unsync_flag = False
        self.data_length_flag = False
        if None != data:
            self.data = data
            self.read()
        
    def read(self):
        """Reads a single frame from buffer data that starts at position.
           Handles reading all flags and extended frame headers."""
        data = self.data
        #Version-specific setups
        name_size = 3
        frame_size_size = 3
        size_reader = id3v2common.read_non_syncsafe
        if self.version >= 3:
            name_size = 4
            frame_size_size = 4
        if self.version == 4:
            size_reader = id3v2common.read_syncsafe
        self.name = bytes(data[:name_size]).decode("latin-1")
        self.read_size = size_reader(name_size, data, frame_size_size)
        flags_start = name_size + frame_size_size
        data_start = flags_start
        #Version 2.2 has no flags to read, nor extended header info.
        if self.version == 3:
            data_start += 2 #two bytes of flags
            bits = data[flags_start]
            self.tag_alter_discard = bool(bits & 128) #discard frame w/ tag alt
            self.file_alter_discard = bool(bits & 64) #discard frame w/file alt
            self.read_only = bool(bits & 32)
            if bits & 31:
                pass #TODO: warn user; these should not be set.
            bits = data[flags_start+1]
            self.compressed_flag = bool(bits & 128)
            self.encrypted_flag = bool(bits & 64)
            self.group_flag = bool(bits & 32)
            if bits & 31:
                raise Exception("Frame contains unknown flags which alter its header_size")
            if self.compressed_flag:
                self.data_length_size = size_reader(data[data_start:data_start + 4])
                data_start += 4
            if self.encrypted_flag:
                self.encryption = data[data_start:data_start + 1]
                data_start += 1
            if self.group_flag:
                self.group = data[data_start:data_start + 1]
                data_start += 1
        if self.version == 4:
            data_start += 2 #two bytes of flags
            bits = data[flags_start]
            self.tag_alter_discard = bool(bits & 64) #discard frame w/ tag alt
            self.file_alter_discard = bool(bits & 32) #discard frame w/file alt
            self.read_only = bool(bits & 16)
            if bits & 143:
                pass #TODO: warn user; these flags should not be set.
            bits = data[flags_start+1]
            self.group_flag = bool(bits & 64)
            self.compressed_flag = bool(bits & 8)
            self.encrypted_flag = bool(bits & 4)
            self.unsync_flag = bool(bits & 2)
            self.data_length_flag = bool(bits & 1)
            if bits & 79:
                raise Exception("Frame contains unknown flags which alter its header_size")
            if self.group_flag:
                self.group = data[data_start:data_start + 1]
                data_start += 1
            #Compressed flag uses data length indicator for size
            if self.encrypted_flag:
                self.encryption = data[data_start:data_start + 1]
                data_start += 1
            if self.data_length_flag:
                self.data_length_size = size_reader(data[data_start:data_start + 4])
                data_start += 4
        #Now we can read the data.  We're all done with header info now, so
        #discard that 'data' block for a copy of the frame's internal data.
        self.data = bytes(data[data_start:flags_start + self.read_size])
        if self.unsync_flag:
            raise ValueError("Unsynced tags are currently not supported")
        if self.compressed_flag:
            self.data = zlib.decompress(self.data)
            if self.version == 3:
                if len(self.data) != self.data_length_size:
                    raise ValueError("Frame data did not decompress to the \
                          expected size.")
        if self.encrypted_flag:
            raise ValueError("Encrypted tags are currently not supported.")
        self.read_size = self.read_size + flags_start #include header in read
        
    def _header_bytes(self, data_size=None):
        """Converts the header part to a string of bytes.  Used by this class
           and any derived classes for their __bytes__method."""
        write_size = 3
        int_write_type = id3v2common.write_normal
        if self.version > 2:
            write_size = 4
        if self.version == 4:
            int_write_type = id3v2common.write_syncsafe
        try:
            name = self.name.encode('latin-1') #pylint:disable=no-member
        except AttributeError: #If we can't encode it, it is likely already bytes.
            name = self.name
        if len(name) != write_size:
            raise ValueError("ID3v2 tag has wrong size name")
        buf = name
        if None == data_size:
            data_size = len(self.data)
        buf += int_write_type(data_size, write_size)
        #version 2 has no flags
        if self.version == 3:
            flags = self.tag_alter_discard << 7
            flags &= self.file_alter_discard << 6
            flags &= self.read_only << 5
            buf += flags
            flags = self.compressed_flag << 7
            flags &= self.encrypted_flag << 6
            flags &= self.group_flag << 5
            buf += flags
            if self.compressed_flag:
                buf += int_write_type(len(self.data), write_size)
            if self.encrypted_flag:
                buf += int_write_type(self.encryption, 1)
            if self.group_flag:
                buf += int_write_type(self.group, 1)
        if self.version == 4:
            flags = self.tag_alter_discard << 6
            flags &= self.file_alter_discard << 5
            flags &= self.read_only << 4
            buf += flags
            flags = self.group_flag << 6
            flags &= self.compressed_flag << 3
            flags &= self.encrypted_flag << 2
            flags &= self.unsync_flag << 1
            flags &= self.data_length_flag
            buf += flags
            if self.group_flag:
                buf += id3v2common.write_normal(self.group, 1)
            if self.encrypted_flag:
                buf += id3v2common.write_normal(self.encryption, 1)
            if self.data_length_flag:
                buf += int_write_type(len(self.data), write_size)
        return buf
                
    def _data_bytes(self, data):
        """Takes byte-ified data, and applies any transformations that are
           needed for storage.""" 
        if self.unsync_flag:
            raise ValueError("not yet supported") #TODO implement
        if self.compressed_flag:
            data = bytes(zlib.compress(data))
        if self.encrypted_flag:
            raise ValueError("not yet supported") #TODO implement
        return data       
        
    def __bytes__(self):
        """Returns a bytearray object containing the binary representation of this
           frame to be stored in an mp3 file."""
        buf = self._header_bytes()
        buf += self._data_bytes(self.data)
        return buf
    
    def __repr__(self):
        rep = "Frame [{} {}] | ".format(self.name,self.read_size)
        if self.file_alter_discard:
            rep += "file discard "
        if self.tag_alter_discard:
            rep += "tag discard "
        if self.read_only:
            rep += "read only "
        if self.compressed_flag:
            rep += "compressed "
        if self.encrypted_flag:
            rep += "encrypted_flag "
        if self.group_flag:
            rep += "group {} ".format(self.group)
        rep += "| {}".format(self.data)
        return rep
    
class ID3v2_ID_Generic_Text(ID3v2_ID_Generic):
    def __init__(self, version, data=None):
        super().__init__(version, data)
        if self.data:
            self.parse_string_from_data()
            
    def parse_string_from_data(self):
        encoding = id3v2common.text_encoding[self.data[0]]
        self.data = self.data[1:].decode(encoding)
        
    def __bytes__(self):
        data = bytearray()
        if self.version == 2:
            try:
                temp = self.data.encode(id3v2common.text_encoding[0])
                data += bytes([0,])
                data += temp
            except UnicodeError:
                data += bytes([1,])
                data += self.data.encode(id3v2common.text_encoding[1])
        else:
            data += bytes([3,])
            data = self.data.encode(id3v2common.text_encoding[3])
        buf = self._header_bytes(len(data) + 1)#1 extra byte for encode type
        buf += self._data_bytes(data)
        return buf
        
if __name__ == '__main__':
    import tests.test_id3v2_frames
    tests.test_id3v2_frames.test_me()