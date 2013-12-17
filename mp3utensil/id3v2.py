# pylint: disable=old-style-class
"""This module contains the methods and classes necessary to identify and
   represent ID3v2 tags."""

import config
import id3v2_frames
import id3v2common

# pylint: disable=too-few-public-methods
class ID3v2x():
    """A class representing an ID3v2.x tag.  Currently handles version
    ID3v2.2, ID3v2.3, and ID3v2.4"""
    def __init__(self, data=None, position=None, **kwargs):

        #Initialize with defaults (v2 options)
        self.data = data
        self.position = position
        self.version = 4 #default to the newest version we support
        if 'version' in kwargs:
            self.version = kwargs['version']
        self.subversion = 0
        self.unsynch_flag = False
        #v3 options
        self.extended_header_flag = False
        self.experimental_flag = False
        self.extended_size = None
        self.crc_flag = False
        self.crc = None
        self.padding = None
        #v4 options
        self.extended_flag_bytes = None
        self.footer_flag = False
        self.is_update_flag = False
        self.restrictions_flag = False
        self.restrictions = None
        #internal values:
        self._frames = []
        self.read_position = None
        if position:
            self.read_position = position
        self.read_size = None

        #If we are reading from a file, construct the class from the data read
        if None != data and None != position:
            if position < 0 or position > len(data):
                raise ValueError("invalid offset into data given to ID3v2 \
                constructor.")
            position = self._read_flags(position)
            #TODO: handle unsync processing for v2 &3 here
            position = self._read_extended_header(position)
            #TODO: handle crc processing for v3 &4 here
            position = self._read_frames(position)
            position = self._read_footer(position)

    def _read_flags(self, pos):
        """Reads the flags and other bits of the ID3v2 header."""
        #All versions
        self.version = self.data[pos + 3]
        self.subversion = self.data[pos + 4]
        flag_bits = self.data[pos +5]
        self.unsynch_flag = bool(flag_bits & 128)
        self.extended_header_flag = bool(flag_bits & 64)
        self.read_size = id3v2common.read_syncsafe(pos + 6, self.data, 4) + 10
        #version 2:
        if self.version == 2 and self.extended_header_flag: #v2 doesn't actually support this flag
            raise ValueError("ID3v2.2 Tag using unknown compression")
        #version 3 and 4:
        if self.version >= 3:
            self.experimental_flag = bool(flag_bits & 32)
        if self.version == 4:
            self.footer_flag = bool(flag_bits & 16)
            self.read_size += 10
        return pos + 10 #Header is always 10 bytes

    def _read_extended_header(self, pos):
        """Reads the extended header, if present.  The extended header has
           some of the most differences between versions."""
        if self.version == 2 or not self.extended_header_flag:
            return pos #Version 2 has no extended header
        if self.version == 3:
            #This value is always 6 or 10; but is 4 bytes wide.
            self.extended_size = self.data[pos + 3]
            self.crc_flag = self.data[pos + 4] #two bytes, and only one flag.
            self.padding = id3v2common.read_non_syncsafe(pos+6, self.data)
            if self.crc_flag:
                if self.extended_size < 10:
                    raise ValueError("Invalid combination of flags in ID3v2:\
                                     CRC but extended header too small.")
                self.crc = id3v2common.read_non_syncsafe(pos+9, self.data)
            if self.data[pos + 4] & 127 or self.data[pos + 5]:
                raise ValueError("Extended header contains unknown flags that \
                                 may affect length.")
            return pos + self.extended_size + 4 #size excludes size bytes
        if self.version >= 4:
            #New way of handling extended headers in v4
            self.extended_size = id3v2common.read_syncsafe(pos, self.data)
            self.extended_flag_bytes = self.data[pos+4]
            flag_bits = self.data[pos+5]
            self.is_update_flag = flag_bits & 64
            self.crc_flag = flag_bits & 32
            offset = 6
            if self.crc_flag:
                self.crc = id3v2common.read_syncsafe(pos+offset, self.data, 5)
                offset += 5
            self.restrictions_flag = flag_bits & 16
            if self.restrictions_flag:
                self.restrictions = self.data[pos + offset]
                offset += 1
            return self.extended_size #in v4 size includes header

    def _read_frames(self, pos):
        """Reads frames until it runs out of data or finds empty frames."""
        size = self.read_size
        id_size = 4
        length_size = 4
        #make changes as necessary for other versions
        if self.version == 2:
            id_size = 3
            length_size = 3
        while pos < (size - (id_size + length_size + 1)):
            #first get some information about the header so we can construct
            #the correct one.
            name = bytes(self.data[pos:pos+id_size]).decode('latin-1')
            class_name = "ID3v2_ID_{}".format(name)
            frame_class = getattr(id3v2_frames, class_name, None)
            if None == frame_class: #We don't have a specific class,use generic
                if 'T' == name[0:1]:
                    frame_class = id3v2_frames.ID3v2_ID_Generic_Text
                else:
                    frame_class = id3v2_frames.ID3v2_ID_Generic
            frame = frame_class(version=self.version, data=self.data[pos:])
            self._frames.append(frame)
            pos += frame.read_size
        if pos > self.read_size:
            raise ValueError("ID3v2 tag had more headers than it reported.")
        #respect the reported size, if possible - the rest is padding.
        return self.read_size

    def _read_footer(self, pos):
        if self.version == 4:
            name = bytes(self.data[pos:pos+3]).decode('latin-1')
            version = self.data[pos + 4]
            subversion = self.data[pos + 5]
            size = id3v2common.read_syncsafe(pos + 6, self.data)
            if '3DI' != name or self.version != version or \
            self.subversion != subversion or self.read_size != size:
                if config.OPTS.verbosity >= 2:
                    print("ID3v2 footer values do not match header.")
            self.read_position += 10

    def __repr__(self):
        rep = "ID3v{}.{} ({} bytes) | ".format(self.version, self.subversion, len(self.data))
        if self.unsynch_flag:
            rep += "unsynched "
        if self.experimental_flag:
            rep += "experimental "
        if self.extended_header_flag:
            rep += "| Extended: size{}, padding {} ".format(self.extended_size, self.padding)
            if self.crc:
                rep += "crc "
        rep += "| "
        for frame in self._frames:
            rep += " -> {}".format(frame.__repr__())
        return rep

def find_and_identify_v2_tags(bin_slice):
    """takes the offset and slice of previously identified "junk" data
       which is stored in one of the data_classes (our python or numpy
       implementation) and tries to identify ID3v2 tags in it."""
    chunk=bin_slice.data
    data_class = bin_slice.data_class
    generator = data_class.generate_potential_matches(skip=-1,
                                                      match=73, #'I'
                                                      chunk=chunk[:-10])
    for i in generator:
        if 68 == chunk[i+1] and 51 == chunk[i+2] and 255 > chunk[i+3] and \
            255 > chunk[i+4] and 128 > chunk[i+6] and 128 > chunk[i+7] and \
            128 > chunk[i+8] and 128 > chunk[i+9]:
            try:
                tag = ID3v2x(data=chunk, position=i)
                _, slices = bin_slice.carve_out(None, i, i+tag.read_size)
                return tag, slices
            except (TypeError, ValueError) as e:
                if config.OPTS.verbosity >=1:
                    print("Malformed ID3v2 tag: {}".format(e))
    return None, [bin_slice,]
