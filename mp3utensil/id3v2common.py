# pylint: disable=trailing-whitespace, old-style-class
"""This module contains functions that are used both by the ID3v2 tag and
   the frames it contains, as well as some general ID3v2  informatin."""
   
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
    buf = bytearray()
    for _ in range(max_bytes):
        buf.append(data & mask)
        data = data >> shift
    if data:
        raise ValueError("Id3v2 Frame data exceeded allowed limits")
    return buf
