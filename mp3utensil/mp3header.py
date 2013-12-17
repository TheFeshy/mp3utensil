# pylint: disable=old-style-class

""" This file contains a class to wrap an MP3 frame header, as well
    as access and interpret the information it contains.  This
    includes derived information such as frame length
"""

import ctypes

C_UINT32 = ctypes.c_uint32

#pylint: disable=too-few-public-methods
class HeaderBits(ctypes.BigEndianStructure):
    '''This defines the layout of the data within the 32 bit frame header'''
    _fields_ = [("seek_tag", C_UINT32, 11),
                ("version", C_UINT32, 2),
                ("layer", C_UINT32, 2),
                ("crc_flag", C_UINT32, 1),
                ("bitrate", C_UINT32, 4),
                ("frequency", C_UINT32, 2),
                ("padding_flag", C_UINT32, 1),
                ("private_flag", C_UINT32, 1),
                ("channel", C_UINT32, 2),
                ("mode_extension", C_UINT32,2),
                ("copyright_flag", C_UINT32, 1),
                ("original_flag", C_UINT32, 1),
                ("emphasis", C_UINT32,2)]

class HeaderStruct(ctypes.Union):
    '''Allows us to access both the individual data items, as well as the
       entire header data at once'''
    _fields_ = [("h", HeaderBits),
                ("d", C_UINT32)]
    #All tables below use None type to indicate reserved (invalid) values.

    # To use these tables, use the value of the bits of that header field as
    # the index. i.e. if checking the "version" field, if the result is 0b10,
    # versions[2] returns the appropriate value.  And yes, emphases is the
    # plural of emphases.
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
    samples = ((None, 576, 1152, 384), #MPEG v2.5: Reserved, Layer III, II, I
               (None, None, None, None), #Reserved version; no valid values.
               (None, 576, 1152, 384), #MPEG v2, Reserved, Layer III, II, I
               (None, 1152, 1152, 384)) #MPEG v1, Reserved, Layer III, II, I

    #The bitrate is dependent on the version and layer, as well as on the
    #bitrate value.
    #"Free" kbitrate is represented as zero
    #kbitrates[version][layer][bitrate]
    #pylint: disable=line-too-long
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
    #pylint:enable=line-too-long
    def __str__(self):
        version = self.h.version
        layer = self.h.layer
        bitrate = self.h.bitrate
        frequency = self.h.frequency
        return "{} {}, {} kbs @ {} hz".format(\
                               HeaderStruct.versions[version],
                               HeaderStruct.layers[layer],
                               HeaderStruct.kbitrates[version][layer][bitrate],
                               HeaderStruct.frequencies[version][frequency])
