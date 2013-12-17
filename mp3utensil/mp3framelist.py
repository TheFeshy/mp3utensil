# pylint: disable=old-style-class
# pylint: disable=no-member
# no-member because pylit isn't handling numpy imports properly.
""" Used for storing and interpreting individual frames in an mp3 file. """
import mp3header
import config

class MP3FrameList():
    """Encapsulates and provides methods to work with individual mp3 frames."""
    if config.OPTS.use_numpy:
        import numpy as np
        _INIT = np.zeros
        _FRAMETYPE = [('header',np.uint32),
                      ('position',np.uint64),
                      ('length',np.uint16)]
    else:
        import pythonrecordarray
        _INIT = pythonrecordarray.PythonRecordArray
        _FRAMETYPE = [('header','L'),
                      ('position','L'),
                      ('length','H')]

    def __init__(self, file_size=0):
        #max framesize=2880, min framesize=24, ebook=208, music=576
        approximate_frame_size = 300
        quarantine_size = config.OPTS.consecutive_frames_to_id * 3
        #This will yield about 10 chunks for a file with "average" frame length
        self._chunksize = file_size // (approximate_frame_size * 10)
        self._chunksize = max(self._chunksize, 10000) #avoid pathological cases
        self._next_frame = 0
        self._current_chunk = 0
        self._chunks = [MP3FrameList._INIT(self._chunksize,
                        dtype=MP3FrameList._FRAMETYPE)]
        self._quarantine = MP3FrameList._INIT(quarantine_size,
                                    dtype=MP3FrameList._FRAMETYPE)
        self._next_quarantine_frame = 0

    def append_frame(self, frame_data, quarantine=False):
        """Appends a new frame and its associated info to the frame list."""
        if quarantine:
            self._quarantine[self._next_quarantine_frame] = frame_data
            self._next_quarantine_frame += 1
        else:
            if self._next_frame >= self._chunksize: #chunk's full, add another
                self._chunks.append(MP3FrameList._INIT(self._chunksize,
                                    dtype=MP3FrameList._FRAMETYPE))
                self._next_frame = 0
                self._current_chunk += 1
            self._chunks[self._current_chunk][self._next_frame] = frame_data
            self._next_frame += 1

#pylint:disable=too-many-locals
#locals used for speed because this is an inner-loop function
    def conditional_append_frame(self, header_struct, position,
                                 quarantine=False):
        """Adds a frame to the list if it is valid.  Returns None if invalid,
           or frame size if valid.  quarantine means that the frame will be
           added to a special conditional array, which will only be accepted
           when accept_quarantine is called"""
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
        tables = mp3header.HeaderStruct
        kbitrate = tables.kbitrates[version_raw][layer_raw][bitrate_raw]
        samplebits = tables.samples[version_raw][layer_raw]
        frequency = tables.frequencies[version_raw][frequency_raw]
        padding = head_h.padding_flag
        if 3 == layer_raw:
            padding = padding << 2 #is 4 bytes /w layer 1, 1 byte /w 2 & 3
        framesize = ((kbitrate * 125 * samplebits) // frequency) + padding
        #Finally, add it to our array and report success
        self.append_frame((header_struct.d, position, framesize), quarantine)
        return framesize
#pylint:enable=too-many-locals

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
                    