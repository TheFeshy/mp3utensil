
import mp3header
import ctypes
import struct

def test_1():
    testheaders = [0b11111111111110101010100100001111, 0xFF0F2315, 0x12345678, 0x87654321]
    head = mp3header.Header_struct()
    for i in range(len(testheaders)):
        testheaders[i] = struct.unpack('>I',struct.pack('<I', testheaders[i]))[0]
        #print(testheaders[i])
    for i in range(50000):
        for j in range(len(testheaders)):
            head.d = testheaders[j]
            h = head._h
            valid = h.seek_tag == 2047 and h.bitrate != 15 and h.version != 1 and \
                    h.layer != 0 and h.emphasis != 2 and h.frequency != 3

def test_2():
    testheaders = [0b11111111111110101010100100001111, 0xFF0F2315, 0x12345678, 0x87654321]
    #head = mp3header.Header_struct()
    for i in range(len(testheaders)):
        testheaders[i] = struct.unpack('>I',struct.pack('<I', testheaders[i]))[0]
        #print(testheaders[i])
    for i in range(5000):
        for j in range(len(testheaders)):
            #head.d = testheaders[j]
            #valid = mp3header.MP3Header.quick_test(head)
            valid = mp3header.MP3Header(testheaders[j]).quick_test()

def test_speed():
    #for i in range(100000):
     #   int.from_bytes((0xFF,0xFA,0xA9,0x0F),byteorder='little')
        #_h = mp3header.MP3Header(struct.unpack('>I',struct.pack('<I', 0b11111111111110101010100100001111))[0])
    h = mp3header.Header_struct()
    import sys
    h.d = int.from_bytes((0xFF,0xFA,0xA9,0x0F), sys.byteorder)
    head = mp3header.MP3Header(h.d)
    print(head.get_frame_time())
    #test_1()
    #test_2()
        
def playtime():
    import numpy as np
    
    a = np.array([1,3,5,7,2,12,1,9,9,0,0,5])
    b = np.where(a > 3)
    print(b)
    c = np.searchsorted(b[0], 6)
    print(c)
    return None
    
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
            temp = mp3header.Header_struct()
            temp.d = i[l[1]][l[0]]
            #if temp._h.seek_tag == 2047:
                #pass
                #print(temp._h.seek_tag)
                #if temp._h.version != 1:
                    #print(temp._h.version)
                    #pass 
        #a = np.array([0xFF,0xFB,0x01,0x11], dtype=np.dtype('B'))
        #b = a.view("<i2")
        #print(b)


    