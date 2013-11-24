# pylint: disable=trailing-whitespace, old-style-class
# pylint: disable=no-member
"""This module is for interacting with a given mp3 file.

   Its goals are to break up an mp3 file into its constituent parts, such as
   groups of mp3 frames, metadata, and unknown chunks (which may be broken
   frames or anything else."""

from collections import namedtuple
import array

import mp3frame
import mp3header
import config

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("Numpy not installed.  This program is much faster with numpy.")
    NUMPY_AVAILABLE = False

DataFrame = namedtuple("DataFrame", ["position", "length"])

class MP3File():
    '''This class contains methods to break an mp3 file into its
       constituent parts, including frames and (tbd) other parts (id3)'''
    def __init__(self, filename):
        self.filename = filename
        self.frames = []
        self.other = []
        if NUMPY_AVAILABLE and not config.OPTS.no_numpy:
            self._array_type = NumpyArrays
        else:
            self._array_type = PythonArrays
            
    def scan_file(self):
        """Identifies valid mp3 frames in a file, and separates out anything
           that isn't a valid mp3 frame as 'data'."""
        #TODO: Pre-scan for ID3 and similar tags?
        with open(self.filename, "rb") as file:
            byte_array = self._array_type(file)
            if config.OPTS.verbosity >= 3:
                print("File {}: {} bytes".format(self.filename, 
                                                 byte_array.get_size()))
            lockon = False
            prev = -1 #Last identified byte
            arraysize = byte_array.get_size()
            consecutive = config.OPTS.consecutive_frames_to_id
            while True:
                if not lockon:
                    if config.OPTS.verbosity >= 3:
                        print("Searching for {} consecutive frames at offset{}"\
                              .format(consecutive, prev))
                    nexth = self.get_lockon(byte_array, prev, consecutive)
                    if None == nexth: #EOF reached while searching; save junk
                        if prev < arraysize:
                            self.other.append(DataFrame(prev, arraysize - prev))
                        break #We've found all the frames we can
                    elif nexth > (prev + 1): #Tag the parts we skipped as junk
                        self.other.append(DataFrame(prev, nexth - prev))
                    lockon = True #If we haven't exited, we should be locked on.
                if arraysize <= nexth: #EOF check
                    self.other.append(DataFrame(prev, arraysize - prev))
                    break 
                header = byte_array.read_header_struct(nexth)
                if mp3header.MP3Header.quick_test(header.h): #expected header
                    frame = mp3frame.MP3Frame(header, nexth)
                    self.frames.append(frame)
                    nexth += frame.length
                    if nexth == prev: #Sanity check for "free" bitrate
                        print("Error: we don't support 'free' bitrate files.")
                        #TODO: throw error; no support for "free" bitrate mp3
                    prev = nexth - 1
                else: #We found something else; start searching again
                    print("lockon lost")
                    lockon = False
                    
    def identify_junk(self):
        """This tries to identify data that was previously excluded as
           "non-frame" data."""
        for j in self.other:
            print("Offset {}, size {}".format(j.position, j.length))

    #pylint: disable=no-self-use                    
    def get_lockon(self, byte_array, prev, consecutive_check):
        """The tags that identify MP3 frames can appear by chance.  To
           avoid picking these "false" frames, we try to identify several
           frames in a row.  The chances of real frames, with flags
           indicating sizes that line up with each other, happening
           consecutively by chance is small."""
        #TODO: "lockon" by identifying valid crc frames too?
        start = prev
        potentials = byte_array.generate_potential_h_structs(start)
        ctdn = consecutive_check #TODO: Verify this is sane >0, < 1k?
        for potential in potentials:
            next_pos = potential[0]
            header = potential[1]
            while ctdn:
                if mp3header.MP3Header.quick_test(header.h):
                    header = mp3header.MP3Header(header)
                    size = header.get_framesize()
                    next_pos += size
                    ctdn -= 1
                    header = byte_array.read_header_struct(next_pos)
                else:
                    break
            if ctdn: #We didn't make the required consecutive frames
                ctdn = consecutive_check #reset the counter for the next pass
            else:
                return potential[0]
          

class NumpyArrays():
    """One of the possible implementations of the array representing the mp3 
       file.  This one uses numpy to boost speed on error-riddled files."""
    def __init__(self, file):
        self.bytearray = np.fromfile(file,dtype=np.dtype('B'))
        byte_array = self.bytearray
        size = len(byte_array)
        self.intarrays = []
        for i in range(4): #build an byte_array view of ints, offset by 1 byte
            extra = (size - i) % 4
            if i and extra:
                self.intarrays.append(byte_array[i:-extra].view("<I4"))
            elif i:
                self.intarrays.append(byte_array[i:].view("<I4"))
            elif extra:
                self.intarrays.append(byte_array[:-extra].view("<I4"))
            else:
                self.intarrays.append(byte_array.view("<I4"))
        self.possibleheaders = np.where(byte_array[:-3] > 254)[0]
        
    def generate_potential_h_structs(self, skip=-1):
        """Uses our list of possible headers (an index of bytes = 255),
           to find potential headers.  Skip is the last byte we have
           already identified (-1 if we haven't started identifying
           yet and want the beginning of the file)
        """
        if skip >= 0: #Start at the next potential after the skip offset
            split = np.searchsorted(self.possibleheaders, skip + 1)
            locations = self.possibleheaders[split:]
        else:
            locations = self.possibleheaders
        for location in locations:
            yield (location, self.read_header_struct(location))
        
    def read_header_struct(self, pos):
        """Returns a header struct if given a position in the array."""
        int_index = divmod(pos, 4)
        header = mp3header.HeaderStruct()
        header.d = self.intarrays[int_index[1]][int_index[0]]
        return header
    
    def get_size(self):
        """Returns the size of the file in bytes"""
        return self.bytearray.size
    
class PythonArrays():
    """One of the possible implementations of the array representing the mp3 
       file.  This is the fall-back if other options aren't available"""
       
    def __init__(self, file):
        self.bytearray = array.array('B')
        file.seek(0,2)
        size = file.tell()
        file.seek(0,0)
        self.bytearray.fromfile(file, size)
        
    def generate_potential_h_structs(self, skip=-1):
        """Gets the next potential header (byte = 255, first 8 of seek tag."""
        if skip < 0:
            skip = 0
        else:
            skip = skip + 1
        for offset, byte in enumerate(self.bytearray[skip:]):
            if 255 == byte:
                yield (offset+skip, self.read_header_struct(offset+skip))
        return None
        
        
        
    def read_header_struct(self, pos):
        """Returns a header struct if given a position in the array."""
        h_int = int.from_bytes(self.bytearray[pos:pos+4], byteorder="little")
        header = mp3header.HeaderStruct()
        header.d = h_int
        return header
        
    def get_size(self):
        """Returns the size of the file in bytes"""
        return len(self.bytearray)
    