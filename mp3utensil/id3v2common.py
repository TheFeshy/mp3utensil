# pylint: disable=trailing-whitespace, old-style-class
"""This module contains functions that are used both by the ID3v2 tag and
   the frames it contains, as well as some general ID3v2  informatin."""
   
text_encoding={0:'latin-1',1:'utf-16',2:'utf-16-be',3:'utf-8'}
REVERSE_TEXT_ENCODING={v: k for k, v in text_encoding.items()} #reversed
   
def read_syncsafe(pos, data, count=4):
    """Reads a sync-safed integer of arbitrary size"""
    return _read_various(pos, data, count, 7)

def read_non_syncsafe(pos, data, count=4):
    """Reads a non-syncsafed integer of arbitrary size"""
    return _read_various(pos, data, count, 8)

def _read_various(pos, data, count, shift=8):
    """Used to read syncsafe or normal multibyte ints from ID3v2 files.
       Some versions use  normal ints, some use ints with the most significant
       bit zeroed and ignored.  Example:  b'0xxxxxxx', where 00000001 00000000
       is 128 because the most significant bit of the lower byte is skipped."""
    mask = 255
    mask = ((mask << shift) & 255)
    value = 0
    if sum([x & mask for x in data[pos:pos+count]]): #Verify no unsync bits set
        raise ValueError("Illegal bytes in ID3v2 size headers")
    for offset in range(count):
        value += (data[pos+offset] << (((count - offset)-1) * shift))
    return value
    
def write_syncsafe(data, max_bytes=4):
    """Writes a syncsafed integer to a bytearray and returns it"""
    return _write_various(data, max_bytes, 7)

def write_normal(data, max_bytes=4):
    """Writes a non-syncsafed integer to a bytearray and returns it"""
    return _write_various(data, max_bytes, 8)    

def _write_various(data, max_bytes=4, shift=8):
    """Used to write syncsafe or normal multibyte ints from ID3v2 files."""
    mask = 255
    mask = (mask >> (8 - shift))
    buf = bytearray([0] * max_bytes)
    for offset in range(max_bytes):
        buf[max_bytes - (1+offset)] = data & mask
        data = data >> shift
    if data:
        raise ValueError("Id3v2 Frame data exceeded allowed limits")
    return buf

def syncsafe_data(data):
    data = bytearray(data)
    for index in range(len(data)-1):
        if 255 == data[index]:
            if 0 == data[index+1] or 224 <= data[index+1]:
                data.insert(index, 0)
    return data

def un_syncsafe_data(data):
    slices = []
    last_index = 0
    size = len(data)
    while last_index >= 0 and last_index < size:
        index = data.find(255, last_index, -1)
        if index >= 0 and data[index+1] == 0:
            slices.append(data[last_index:index])
            last_index = index +1 #skip zero byte
        elif index < 0:
            slices.append(data[last_index:])
    return bytearray().join(slices)
                