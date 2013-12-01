# pylint: disable=trailing-whitespace, old-style-class, slots-on-old-class
""" Used for storing and interpreting individual frames in an mp3 file. """
import mp3header
import numpy as np

class MP3FrameList():
    """Encapsulates and provides methods to work with individual mp3 frames."""
    _FRAMETYPE = [('header',np.uint32),
                  ('position',np.uint64),
                  ('length',np.uint16)]
    
    def __init__(self, file_size=0):
        #max framesize=2880, min framesize=24, ebook=208, music=576
        approximate_frame_size = 300
        #This will yield about 10 chunks for a file with "average" frame length
        self._chunksize = file_size // (approximate_frame_size * 10) 
        self._chunksize = max(self._chunksize, 10000)
        self._next_frame = 0
        self._current_chunk = 0
        self._chunks = [np.zeros(self._chunksize, dtype=MP3FrameList._FRAMETYPE),]
        
    def append_frame(self, header, position, size):
        """Appends a new frame and its associated info to the frame list."""
        if self._next_frame >= self._chunksize: #chunk's full, add another
            self._chunks.append(np.zeros(self._chunksize, dtype=MP3FrameList._FRAMETYPE))
            self._next_frame = 0
            self._current_chunk += 1
        self._chunks[self._current_chunk][self._next_frame] = (header, position, size)
        self._next_frame += 1
        
    def conditional_append_frame(self, header_struct, position):
        """Adds a frame to the list if it is valid.  Returns None if invalid,
           or frame size if valid."""
        head_h = header_struct.h
        seek_tag = head_h.seek_tag
        bitrate_raw = head_h.bitrate
        version_raw = head_h.version
        layer_raw = head_h.layer
        emphasis_raw = head_h.emphasis
        frequency_raw = head_h.frequency
        #Test for valid frame, and fail if invalid:
        if seek_tag != 2047 or bitrate_raw == 15 or bitrate_raw == 0 or \
            version_raw == 1 or layer_raw == 0 or emphasis_raw == 2 or \
            frequency_raw == 3:
            return None
        #calculate frame size
        _TABLES = mp3header.HeaderStruct
        kbitrate = _TABLES.kbitrates[version_raw][layer_raw][bitrate_raw]
        samplebits = _TABLES.samples[version_raw][layer_raw]
        frequency = _TABLES.frequencies[version_raw][frequency_raw]
        padding = head_h.padding_flag
        if 3 == layer_raw:
            padding = padding << 2 #is 4 bytes /w layer 1, 1 byte /w 2 & 3
        framesize = ((kbitrate * 125 * samplebits) // frequency) + padding
        #Finally, add it to our array and report success
        self.append_frame(header_struct.d, position, framesize)
        return framesize
        
        
    def verify_crc(self):
        """Verifies that the crc value for the frame is correct."""
        #TODO: verify frame crc check
        #TODO: decide how to differentiate between no crc and crc failed
        pass
    
    def get_bit_reservoir(self):
        """Returns the offset reported by the bit reservoir, which indicates
           a distance into previous frames which contain the rest of this
           frame's data."""
        #TODO: read bit reservoir
        pass 
    
    def __iter__(self):
        """Iterator that iterates over all frames in list, transparently
           Moving from one chucnk to the next."""
        for chunk in self._chunks[:-1]:
            for frame in chunk:
                yield frame 
        chunk = self._chunks[-1]
        for i in range(self._next_frame):
            yield chunk[i]                        
                    