# pylint: disable=trailing-whitespace, old-style-class
"""This module impliments all of the ID3v2.x frames"""

#from id3v2 import size_helper
import zlib

def size_helper(data):
    """ID3v2 tags use four-byte size tags, with each byte trunkated to 7 bits
       to avoid false sync values.  This helper function calculates sizes
       given four such truncated bytes."""
    if sum(map(lambda x: x&128, data[:4])): #header sanity check
        raise Exception("Illegal bytes in ID3v2 size headers")
    #return (data[0] << 21) + (data[1] << 14) + (data[2] << 7)+ data[3]
    return (data[0] << 24) + (data[1] << 16) + (data[2] << 8)+ data[3]
    

def truncated_size(size):
    buf = bytearray()
    for _ in range(4):
        buf.append(size & 127)
        size >> 7
    if size:
        raise Exception("Id3v2 Frame size exceeded allowed limits")
    return buf

class ID3v2_ID_Generic():
    """This is the frame base class, and also represents an unknown frame.
       Since we don't know anything about the nature of its contents, we 
       store it as bytes.  Derived classes can also call this class's 
       read_from_position method to read in all flags, and leave the bytes
       to be parsed in self.data"""
    def __init__(self):
        #Set some default values.
        self.name = None
        self.tag_alter_discard = False
        self.file_alter_discard = False
        self.read_only = False
        self.compression = False
        self.encrypted = False
        self.group_flag = False
        self.uncompressed_size = None
        self.encryption = None
        self.group = None
        self.data = None
        self.read_size = None
        
    def get_header_size(self):
        """Returns the full header size as expanded by flags"""
        return 10 + (self.compression << 2) + self.encrypted + self.group
        
    def read_from_position(self, version, data):
        """Reads a single frame from buffer data that starts at position.
           Handles reading all flags and extended frame headers."""
        header_size = 10
        position = 0 #TODO remove position it's not needed
        self.name = bytes(data[position:position+4]).decode('latin-1')
        self.read_size = size_helper(data[position+4:position+8])
        #if true discard this frame when tag is altered
        bits = data[position+8]
        self.tag_alter_discard = bool(bits & 128)
        #if true discard this frame when file is altered
        self.file_alter_discard = bool(bits & 64)
        self.read_only = bool(bits & 32)
        if bits & 31:
            #TODO: according to spec if these flags are set we leave the frame alone
            pass
        bits = data[position+9]
        self.compression = bool(bits & 128)
        self.encrypted = bool(bits & 64)
        self.group_flag = bool(bits & 32)
        #Use those flags to determine if there are extended header bytes
        if bits & 31:
            raise Exception("Frame contains unknown flags which alter its header_size")
        if self.compression:
            #TODO: verify that this is '7 bits/byte' header_size; reference doc is unclear
            self.uncompressed_size = size_helper(data[header_size:header_size+4])
            header_size += 4
        else:
            self.uncompressed_size = None
        if self.encrypted:
            self.encryption = data[header_size]
            header_size += 1
        else:
            self.encryption = None
        if self.group_flag:
            self.group = data[header_size]
            header_size += 1
        else:
            self.group = None 
        self.read_size += header_size
        self.data = bytes(data[header_size+position:self.read_size+position])
        if self.encrypted:
            #TODO: Fuss to the user about this, as we don't support it
            pass
        if self.compression:
            self.data = zlib.decompress(self.data)
            if len(self.data) != self.uncompressed_size:
                raise Exception("Error uncompressing compressed frame")
        return self.read_size
            
    def update_data(self, something):
        """All tags that are assigned data will have it done by calling
           this method.  For the generic class, this is easy: just store
           some bytes.  If it can be stored as bytes, it's valid."""
        self.data = bytes(something)
        
    def __bytes__(self):
        """Returns a bytearray object containing the binary representation of this
           frame to be stored in an mp3 file."""
        #first pack the header:
        buf = bytearray()
        name = self.name.encode('latin-1')
        if len(name) != 4:
            raise Exception("Wrong size frame ID")
        buf += name
        buf += truncated_size(self.data + self.get_header_size() - 10)
        buf.append((self.tag_alter_discard << 8) + \
                   (self.file_alter_discard << 7) + \
                   (self.read_only << 6))
        buf.append((self.compression << 8) + \
                   (self.encrypted << 7) + \
                   (self.group_flag << 6))
        if self.compression:
            buf += truncated_size(len(self.data))
            self.data = zlib.compress(self.data)
            buf += truncated_size(len(self.data))
            new_size = truncated_size(self.data + self.get_header_size() - 10)
            for i in range(len(new_size)):
                buf[4+i] = new_size[i]
        if self.encrypted:
            raise Exception("Encrypted frames not currently supported!")
        if self.group_flag:
            buf.append(self.group)
        buf += self.data
        return buf
    
    def __repr__(self):
        rep = "Frame [{} {}] | ".format(self.name,self.read_size)
        if self.file_alter_discard:
            rep += "file discard "
        if self.tag_alter_discard:
            rep += "tag discard "
        if self.read_only:
            rep += "read only "
        if self.compression:
            rep += "compressed "
        if self.encrypted:
            rep += "encrypted "
        if self.group_flag:
            rep += "group {} ".format(self.group)
        rep += "| {}".format(self.data)
        return rep