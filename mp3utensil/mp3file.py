
import mp3frame
import mp3header
from collections import namedtuple

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
        if NUMPY_AVAILABLE:
            self.array_type = NumpyArrays
            
    def scan_file(self):
        """Identifies valid mp3 frames in a file, and separates out anything
           that isn't a valid mp3 frame as 'data'."""
        #ToDo: Pre-scan for ID3 and similar tags?
        with open(self.filename, "rb") as file:
            array = self.array_type(file)
            lockon = False #Used to determine if we (think) we know where our next frame should be
            prev = 0 #Last identified byte; i.e. the end of the previous found frame
            arraysize = len(array)
            consecutive = 5 #ToDo: Make this a command line variable?
            while True:
                if not lockon:
                    nexth = self.get_lockon(array, prev, consecutive) #nexth is a position in bytes
                    if not nexth: #EOF reached while searching; save junk
                        self.other.append(DataFrame(prev, arraysize - prev))
                        break #We've found all the frames we can
                    elif nexth != prev: #Tag the parts we skipped as junk ("data")
                        self.other.append(DataFrame(prev, nexth - prev))
                if arraysize <= nexth:
                    break #Exit if we've just read the last frame and it ends on the file boundary
                header = array.read_header_struct(nexth)
                if mp3header.MP3Header.quick_test(header): #If we find a header where we expect
                    frame = mp3frame.MP3Frame(header), nexth
                    self.frames.append(frame)
                    nexth += frame.length
                else: #We found something else; start searching again
                    lockon = False
                    
    def get_lockon(self, array, prev, consecutive_check):
        """The tags that identify MP3 frames can appear by chance.  To
           avoid picking these "false" frames, we try to identify several
           frames in a row.  The chances of real frames, with flags
           indicating sizes that line up with each other, happening
           consecutively by chance is small."""
        #ToDo: "lockon" by identifying valid crc frames too?
        start = prev
        potentials = array.generate_potential_header_structs(start)
        ctdn = consecutive_check #ToDo: Verify this is sane (>0, < 1k?)
        found = None
        for p in potentials:
            nexth = p
            while ctdn:
                if mp3header.MP3Header.quick_test(nexth):
                    header = mp3header.MP3Header(next)
                    size = header.get_framesize()
                    nexth += size
                    ctdn -= 1
                else:
                    break
            if ctdn: #We didn't make the required consecutive frames
                ctdn = consecutive_check #reset the counter for the next pass
            else:
                found = p
                break
        return found
            
            
            
'''Separate arrays backed by file:
numpy, no numpy

what they do different:
Create themselves
find potentials (generator)
read headers (as header)
read frames /data (eventually)

What's the same:
taking potentials (header + position) and locking on
realizing the lock is broken
'''            

class NumpyArrays():
    def __init__(self, file):
        self.bytearray = np.fromfile(file,dtype=np.dtype('B'))
        a = self.bytearray
        size = len(a)
        self.intarrays = []
        for i in range(4): #build an array view of ints, each offset one byte
            extra = (size - i) % 4
            if i and extra:
                self.intarrays.append(a[i:-extra].view("<I4"))
            elif i:
                self.intarrays.append(a[i:].view("<I4"))
            elif extra:
                self.intarrays.append(a[:-extra].view("<I4"))
            else:
                self.intarrays.append(a.view("<I4"))
        self.possibleheaders = np.where(a[:-3] > 254)[0]
        
    def generate_potential_header_structs(self, start):
        """Uses our list of possible headers (an index of bytes = 255),
           cuts out the part we're already passed, then gets the index
           and offset of the equivalent integer array."""
        split = np.searchsorted(self.possibleheaders, start) + 1 #find next element after the start
        self.locations = self.possibleheaders[split:]
        for l in self.locations:
            yield self.read_header_struct(l)
        
    def read_header_struct(self, pos):
        int_index = divmod(pos, 4) #Get the int index and int array for fast lookup
        h = mp3header.Header_struct()
        h.d = self.intarrays[int_index[1]][int_index[0]]
        return h

class generate_potentials_numpy():
    """generator for getting potential headers
       (that is, valid headers that may or may not have valid frames"""
    def __init__(self, a, pos=0):
        """Pass this a NumpyArrayViews"""
        