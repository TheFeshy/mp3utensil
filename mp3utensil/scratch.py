import ctypes

c_uint8 = ctypes.c_uint8
c_uint32 = ctypes.c_uint32

class Header_bits(ctypes.BigEndianStructure):
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
    
class Fourbytes(ctypes.BigEndianStructure):
    _fileds_ = [("a", c_uint8),
                ("b", c_uint8),
                ("c", c_uint8),
                ("d", c_uint8)]
    
class Header_struct(ctypes.Union):
    _fields_ = [("h", Header_bits),
                ("d", c_uint32)]

def scratch():
    head = Header_struct()
    head.as_32 = 0xFFFA3D5B
    print("seek {}".format(head.h.seek_tag))
    print("version {}".format(head.h.version))
    print("crc_flag {}".format(head.h.crc_flag))
    
def test_bitrate():
    import mp3protocol
    v = mp3protocol.MP3HeaderValues.bitrates
    print(v[2][1][3])
        
def playtime():
    import numpy as np
    with open("testdata/test.mp3", "rb") as f:
        f.seek(0,2)
        size = f.tell()
        f.seek(0,0)
        extra = size % 4
        a = np.fromfile(f,dtype=np.dtype('B'), count=size)
        i = []
        for z in range(4):
            if z:
                cut = extra + (4-z)
                i.append(a[z:-cut].view("<I4"))
            else:
                i.append(a[:-extra].view("<I4")) #Note: if extra or cut is zero t his won't work.
            print(len(i[z]))
        c = np.where(a[:-3] > 254)
        lookups = map(lambda x: divmod(x,4), c[0])
        for l in lookups:
            #print("array {} index {}".format(l[1],l[0]))
            #print(i[l[1]][l[0]])
            #if l[0] > 2000:
                #break
            temp = Header_struct()
            temp.d = i[l[1]][l[0]]
            #if temp.h.seek_tag == 2047:
                #pass
                #print(temp.h.seek_tag)
                #if temp.h.version != 1:
                    #print(temp.h.version)
                    #pass 
        #a = np.array([0xFF,0xFB,0x01,0x11], dtype=np.dtype('B'))
        #b = a.view("<i2")
        #print(b)


    