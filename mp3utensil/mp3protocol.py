
class MP3HeaderValues():
    """This contains tables to interpret the various bits in an mp3 header"""
    
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
    #"Free" bitrate is represented as zero
    #bitrates[version][layer][bitrate]
    bitrates = (#MPEG v2.5
                (#Reserved
                 (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
                 #Layer III
                 (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None),
                 #Layer II
                 (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None),
                 #Layer I
                 (0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256, None)),
               #Reserved
                (#Reserved
                 (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
                 #Layer III
                 (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
                 #Layer II
                 (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
                 #Layer I
                 (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)),
               #MPEG v2
                (#Reserved
                 (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
                 #Layer III
                 (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None),
                 #Layer II
                 (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None),
                 #Layer I
                 (0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256, None)),
               #MPEG v1
                (#Reserved
                 (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None),
                 #Layer III
                 (0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, None),
                 #Layer II
                 (0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384, None),
                 #Layer I
                 (0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448, None)))
    
    '''bitrates = {"MPEG Version 1":{"Layer I":{0:"free", 1:32,  2:64,  3:96,
                                            4:128, 5:160, 6:192, 7:224,
                                            8:256, 9:288, 10:320, 11:352,
                                            12:384, 13:416, 14:448, 15:"reserved"},
                                "Layer II":{0:"free", 1:32,  2:48,  3:56,
                                            4:64, 5:80, 6:96, 7:112,
                                            8:128, 9:160, 10:192, 11:224,
                                            12:256, 13:320, 14:384, 15:"reserved"},
                               "Layer III":{0:"free", 1:32,  2:40,  3:48,
                                            4:56, 5:64, 6:80, 7:96,
                                            8:112, 9:128, 10:160, 11:192,
                                            12:224, 13:256, 14:320, 15:"reserved"}},
               "MPEG Version 2":{"Layer I":{0:"free", 1:32,  2:48,  3:56,
                                            4:64, 5:80, 6:96, 7:112,
                                            8:128, 9:144, 10:160, 11:176,
                                            12:192, 13:224, 14:256, 15:"reserved"},
                                "Layer II":{0:"free", 1:8,  2:16,  3:24,
                                            4:32, 5:40, 6:48, 7:56,
                                            8:64, 9:80, 10:96, 11:112,
                                            12:128, 13:144, 14:160, 15:"reserved"},
                                "Layer III":{0:"free", 1:8,  2:16,  3:24,
                                            4:32, 5:40, 6:48, 7:56,
                                            8:64, 9:80, 10:96, 11:112,
                                            12:128, 13:144, 14:160, 15:"reserved"}},
                "MPEG Version 2.5":{"Layer I":{0:"free", 1:32,  2:48,  3:56,
                                            4:64, 5:80, 6:96, 7:112,
                                            8:128, 9:144, 10:160, 11:176,
                                            12:192, 13:224, 14:256, 15:"reserved"},
                                "Layer II":{0:"free", 1:8,  2:16,  3:24,
                                            4:32, 5:40, 6:48, 7:56,
                                            8:64, 9:80, 10:96, 11:112,
                                            12:128, 13:144, 14:160, 15:"reserved"},
                                "Layer III":{0:"free", 1:8,  2:16,  3:24,
                                            4:32, 5:40, 6:48, 7:56,
                                            8:64, 9:80, 10:96, 11:112,
                                            12:128, 13:144, 14:160, 15:"reserved"}}}'''
