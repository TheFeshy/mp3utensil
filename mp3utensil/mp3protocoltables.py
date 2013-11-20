
class MP3Prot():
    """This contains tables to interpret the various bits in an mp3 frame"""
    
    from bitstring import Bits
    from collections import namedtuple
    
    FourBitTable = namedtuple("FourBitTable","")
    
    #versions = {Bits('0b00'):"MPEG Version 2.5", Bits('0b01'):"reserved", Bits('0b10'):"MPEG Version 2", Bits('0b11'):"MPEG Version 1"}
    versions = ("MPEG Version 2.5", "reserved", "MPEG Version 2", "MPEG Version 1")
    #layers = {Bits('0b00'):"reserved",Bits('0b01'):"Layer III",Bits('0b10'):"Layer II",Bits('0b11'):"Layer I"}
    layers = ("reserved", "Layer III", "Layer II", "Layer I")
    bitrates = {"MPEG Version 1":{"Layer I":{0:"free", 1:32,  2:64,  3:96,
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
                                            12:128, 13:144, 14:160, 15:"reserved"}}}
    frequency = {"MPEG Version 1":{0:44100,1:48000,2:32000,3:"reserved"},
                 "MPEG Version 2":{0:22050,1:24000,2:16000,3:"reserved"},
               "MPEG Version 2.5":{0:11025,1:12000,2:8000, 3:"reserved"}}
    channel = {0:"Stereo",1:"Joint Stereo",2:"Dual channel",3:"Single channel"}
    emphasis = {0:"none",1:"50/15 ms", 2:"reserved", 3:"CCIT J.17"}
    samples = {"MPEG Version 1":{"Layer I":384, "Layer II":1152, "Layer III":1152},
               "MPEG Version 2":{"Layer I":384, "Layer II":1152, "Layer III":576}, #?? Uncertain about layer 1
               "MPEG Version 2.5":{"Layer I":384, "Layer II":1152, "Layer III":576}} #?? Uncertain if this is right
    test={'10':"two",'01':"one", '00':"zero", "11":"three"}
