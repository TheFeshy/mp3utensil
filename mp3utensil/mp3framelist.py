# pylint: disable=trailing-whitespace, old-style-class, slots-on-old-class
""" Used for storing and interpreting individual frames in an mp3 file. """
import mp3header
import numpy as np
import config

class MP3FrameList():
    """Encapsulates and provides methods to work with individual mp3 frames."""
    _FRAMETYPE = [('header',np.uint32),
                  ('position',np.uint64),
                  ('length',np.uint16)]
    
    def __init__(self, file_size=0):
        #max framesize=2880, min framesize=24, ebook=208, music=576
        approximate_frame_size = 300
        quarantine_size = config.OPTS.consecutive_frames_to_id * 3
        #This will yield about 10 chunks for a file with "average" frame length
        self._chunksize = file_size // (approximate_frame_size * 10) 
        self._chunksize = max(self._chunksize, 10000) #avoid pathological cases
        self._next_frame = 0
        self._current_chunk = 0
        self._chunks = [np.zeros(self._chunksize, dtype=MP3FrameList._FRAMETYPE),]
        self._quarantine = np.zeros(quarantine_size, dtype=MP3FrameList._FRAMETYPE)
        self._next_quarantine_frame = 0
        
    def append_frame(self, frame_data, quarantine=False):
        """Appends a new frame and its associated info to the frame list."""
        if quarantine:
            self._quarantine[self._next_quarantine_frame] = frame_data
            self._next_quarantine_frame += 1
        else:
            if self._next_frame >= self._chunksize: #chunk's full, add another
                self._chunks.append(np.zeros(self._chunksize, dtype=MP3FrameList._FRAMETYPE))
                self._next_frame = 0
                self._current_chunk += 1
            self._chunks[self._current_chunk][self._next_frame] = frame_data
            self._next_frame += 1
        
    def conditional_append_frame(self, header_struct, position, quarantine=False):
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
        self.append_frame((header_struct.d, position, framesize), quarantine)
        return framesize
    
    def discard_quarantine(self):
        """Invalidate potential frames in quarantine"""
        self._next_quarantine_frame = 0
        
    def accept_quarantine(self):
        """Move frames from quarantine to our accepted frames list"""
        for i in range(self._next_quarantine_frame):
            self.append_frame(self._quarantine[i], False)
        self._next_quarantine_frame = 0
        
        
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
            
    def __len__(self): 
        length = 0
        for chunk in self._chunks[:-1]:
            length += len(chunk)
        length += self._next_frame
        return length 
    
    def __getitem__(self, index):
        chunk = 0
        size = len(self._chunks[0])
        while index > size:
            index -= size
            chunk += 1
            size = len(self._chunks[chunk])
        return self._chunks[chunk][index]                    
                    