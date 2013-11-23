'''
This file contains a class to wrap an MP3 frame header, as well
as access and interpret the information it contains.  This
includes derived information such as frame length
'''

import ctypes

c_uint8 = ctypes.c_uint8
c_uint32 = ctypes.c_uint32

class Header_bits(ctypes.BigEndianStructure):
    '''This defines the layout of the data within the 32 bit frame header'''
    _fields_ = [("seek_tag", c_uint32, 11),
                ("version", c_uint32, 2),
                ("layer", c_uint32, 2),
                ("crc_flag", c_uint32, 1),
                ("bitrate", c_uint32, 4),
                ("frequency", c_uint32, 2),
                ("padding_flag", c_uint32, 1),
                ("private_flag", c_uint32, 1),
                ("channel", c_uint32, 2),
                ("mode_extension", c_uint32,2),
                ("copyright_flag", c_uint32, 1),
                ("original_flag", c_uint32, 1),
                ("emphasis", c_uint32,2)]

    
class Header_struct(ctypes.Union):
    '''Allows us to access both the individual data items, as well as the
       entire header data at once'''
    _fields_ = [("h", Header_bits),
                ("d", c_uint32)]    

class MP3Header():
    """This class represents one 32 bit frame header."""
    __slots__ = ["_h", "valid"]
    
    #All tables below use None type to indicate reserved (invalid) values.
    
    #To use these tables, use the value of the bits of that header field as the index.
    #i.e. if checking the "version" field, if the result is 0b10, versions[2] returns
    #the appropriate value.  And yes, emphases is the plural of emphases.
    versions = ("MPEG Version 2.5", None, "MPEG Version 2", "MPEG Version 1")
    layers = (None, "Layer III", "Layer II", "Layer I")
    channels = ("Stereo", "Joint Stereo", "Dual channels", "Single channels")
    emphases = ("none", "50/15 ms", None, "CCIT J.17")
    
    #frequency depends on the version and the frequency value from the header.
    #If the frequency field in the header is 0b10, and the version field
    #is 0b11, frequencies[3][2] would return the appropriate value.
    #frequencies[version][frequency]
    frequencies = ((11025,12000,8000,None), #MPEG v2.5
                   (None, None, None, None), #reserved version: no valid values
                   (22050, 24000, 16000, None), #MPEG v2
                   (44100, 48000, 32000, None)) #MPEG v1
    
    #The number of samples per frame.  This is dependent on the version and
    #the layer.
    #samples[version][layer].
    #TODO: Verify all of version 2.5, and version 2 layer 1.
    samples = ((None, 576, 1152, 384), #MPEG v2.5: Reserved, Layer III, Layer II, Layer I.
               (None, None, None, None), #Reserved version; no valid values.
               (None, 576, 1152, 384), #MPEG v2, Reserved, Layer III, Layer II, Layer I.
               (None, 1152, 1152, 384)) #MPEG v1, Reserved, Layer III, Layer II, Layer I.

    #The bitrate is dependent on the version and layer, as well as on the 
    #bitrate value.
    #"Free" kbitrate is represented as zero
    #kbitrates[version][layer][bitrate]
    kbitrates = (#MPEG v2.5
                ((None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None), #Reserved
                 (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None), #Layer III
                 (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None), #Layer II
                 (0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256, None)), #Layer I
               #Reserved Version
                ((None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None), #Reserved
                 (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None), #Layer III
                 (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None), #Layer II
                 (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)), #Layer I
               #MPEG v2
                ((None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None), #Reserved
                 (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None), #Layer III
                 (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None), #Layer II
                 (0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256, None)), #Layer I
               #MPEG v1
                ((None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None), #Reserved
                 (0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, None), #Layer III
                 (0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384, None), #Layer II
                 (0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448, None))) #Layer I
    
    def __init__(self, head):
        self._h = head
        self.valid = MP3Header.quick_test(self._h.h)
    
    @staticmethod
    def quick_test(head_h):
        '''Does a quick check of a header to see if the flags it contains are 
           valid.  This does not guarantee the header leads a valid frame!
           Only that it can't be trivially excluded.  Returns true if valid'''
        return head_h.seek_tag == 2047 and head_h.bitrate != 15 and head_h.version != 1 and \
               head_h.layer != 0 and head_h.emphasis != 2 and head_h.frequency != 3 
    
    def get_framesize(self):
        '''Returns the length of the frame (including the header) in bytes.'''
        if self.valid:
            kbitrate = MP3Header.kbitrates[self._h.h.version][self._h.h.layer][self._h.h.bitrate]
            samplebits = MP3Header.samples[self._h.h.version][self._h.h.layer]
            frequency = MP3Header.frequencies[self._h.h.version][self._h.h.frequency]
            padding = self._h.h.padding_flag
            if 3 == self._h.h.layer:
                padding = padding * 4 #Slot size is 4 bytes for layer 1, 1 byte for layers 2 and 3.
            return ((kbitrate * 1000 * (samplebits//8)) // frequency) + padding
        return None #TODO: throw error instead?
    
    def get_frame_time(self):
        '''Returns the time in ms that this frame takes to play'''
        return MP3Header.samples[self._h.h.version][self._h.h.layer] * 1000.0 / MP3Header.frequencies[self._h.h.version][self._h.h.frequency]
    
    def __str__(self):
        v = self._h.h.version
        l = self._h.h.layer
        b = self._h.h.bitrate
        f = self._h.h.frequency
        return "{} {}, {} kbs @ {} hz (Valid? {})".format(MP3Header.versions[v], 
                               MP3Header.layers[l],
                               MP3Header.kbitrates[v][l][b],
                               MP3Header.frequencies[v][f],
                               self.valid)
    
    