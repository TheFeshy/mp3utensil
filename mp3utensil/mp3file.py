# pylint: disable=old-style-class
# pylint: disable=no-member
"""This module is for interacting with a given mp3 file.

   Its goals are to break up an mp3 file into its constituent parts, such as
   groups of mp3 frames, metadata, and unknown chunks (which may be broken
   frames or anything else."""

import array

import mp3framelist
import mp3header
import config
import id3
import id3v2
import binslice as bs

if config.OPTS.use_numpy:
    import numpy as np

_MAX_INDEX_METHOD_SEARCHES = 1

class MP3File():
    '''This class contains methods to break an mp3 file into its
       constituent parts, including frames and (tbd) other parts (id3)'''
    def __init__(self, filename):
        self.filename = filename
        self.frames = None
        self.other = []
        if config.OPTS.use_numpy:
            self._array_type = NumpyArrays
        else:
            self._array_type = PythonArrays
        self.byte_array = None

    def scan_file(self):
        """Identifies valid mp3 frames in a file, and separates out anything
           that isn't a valid mp3 frame as 'data'."""
        with open(self.filename, "rb") as file:
            self.scan_file_python_or_numpy(file)
        self.scan_non_frame_data([id3v2.find_and_identify_v2_tags,
                                  id3.find_and_identify_v1_tags])

    def scan_non_frame_data(self,identify_functions):
        """Scans each binary slice we identified, using a list of functions
           to match each type of metadata."""
        matched = []
        unmatched = []
        for bin_slice in self.other:
            hit, miss = bin_slice.search_within(identify_functions)
            if hit:
                matched += hit
            unmatched += miss
        self.other = matched + unmatched

    def scan_file_python_or_numpy(self, file):
        """Python and numpy implementation of the file scanner"""
        self.byte_array = self._array_type(file)
        array_size = self.byte_array.get_size()
        self.frames = mp3framelist.MP3FrameList(file_size=array_size)
        if config.OPTS.verbosity >= 3:
            print("File {}: {} bytes".format(self.filename,
                                             self.byte_array.get_size()))
        lockon = False
        prev_byte = 0 #Last identified byte
        #local variables for quick access inside loop
        consecutive = config.OPTS.consecutive_frames_to_id
        header_s = mp3header.HeaderStruct()
        verbosity = config.OPTS.verbosity
        append_frame = self.frames.conditional_append_frame
        byte_array = self.byte_array
        while True:
            if not lockon:
                if verbosity >= 3:
                    print("Searching for {} consecutive frames at offset {}"\
                          .format(consecutive, prev_byte))
                next_pos, first_pos = self.get_lockon(byte_array, prev_byte-1,
                                                      consecutive)
                if verbosity >= 3:
                    print("found {} frames at offset {}"\
                          .format(consecutive, first_pos))
                if None == next_pos: #EOF reached while searching; save junk
                    if prev_byte < array_size:
                        self.other.append(bs.BinSlice(prev_byte,
                            byte_array.get_slice(prev_byte, array_size),
                                                 self.byte_array))
                    break #We've found all the frames we can
                elif first_pos > prev_byte: #Tag the parts we skipped
                    self.other.append(bs.BinSlice(prev_byte,
                            byte_array.get_slice(prev_byte, first_pos),
                                                 self.byte_array))
                lockon = True #If we haven't exited, we should be locked on.
                prev_byte = next_pos #If we locked on, we identified to here.
            if array_size <= next_pos: #EOF check
                break
            header_s = byte_array.read_header_struct(next_pos)
            length = append_frame(header_s, next_pos)
            if length: #If the header was valid, it's info was added
                next_pos += length #TODO: free bitrate frames?
                prev_byte = next_pos
            else: #We found something else; start searching again
                if verbosity >=3:
                    print("lockon lost")
                lockon = False

    def get_lockon(self, byte_array, prev, consecutive_check):
        """The tags that identify MP3 frames can appear by chance.  To
           avoid picking these "false" frames, we try to identify several
           frames in a row.  The chances of real frames, with flags
           indicating sizes that line up with each other, happening
           consecutively by chance is small."""
        #TODO: "lockon" by identifying valid crc frames too?
        potentials = byte_array.generate_potential_matches(prev)
        ctdn = consecutive_check
        #local methods for speed
        read_header = byte_array.read_header_struct
        conditional_append = self.frames.conditional_append_frame
        discard_quarantine = self.frames.discard_quarantine
        for next_pos in potentials:
            first_pos = next_pos
            while ctdn: #TODO: use local variables for speed
                header = read_header(next_pos)
                length = conditional_append(header, next_pos, quarantine=True)
                if length:
                    ctdn -= 1
                    next_pos += length
                    #header = byte_array.read_header_struct(next_pos)
                else:
                    break
            if ctdn: #We didn't make the required consecutive frames
                ctdn = consecutive_check #reset the counter for the next pass
                discard_quarantine()
            else:
                self.frames.accept_quarantine()
                return next_pos, first_pos
        return None, None

class NumpyArrays():
    """One of the possible implementations of the array representing the mp3
       file.  This one uses numpy to boost speed on error-riddled files."""
    def __init__(self, file):
        self.byte_array = np.fromfile(file,dtype=np.dtype('B'))
        byte_array = self.byte_array
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
        #self.possibleheaders = np.where(byte_array[:-3] > 254)[0]

    def generate_potential_matches(self, skip=-1, match=255, chunk=None):
        """Uses our list of possible headers (an index of bytes = 255),
           to find potential headers.  Skip is the last byte we have
           already identified (-1 if we haven't started identifying
           yet and want the beginning of the file)
        """
        skip += 1
        if None == chunk:
            size = self.get_size() - 3 #Skip the last bytes (too small)
            chunk = self.byte_array
        else:
            size = len(chunk)
        skip = min(max(skip,0),size) #sanity check that skip is reasonable
        lookahead = 65535
        max_peek = min(size, skip+lookahead)
        possibleheaders = np.where(chunk[skip:max_peek] == match)[0]
        while size != skip:
            for location in possibleheaders:
                location = int(location)
                location += skip
                yield location
            max_peek += 65535
            skip += 65535
            max_peek = min(size, skip+lookahead)
            skip = min(size, skip)
            possibleheaders = np.where(chunk[skip:max_peek] == 255)[0]

    def read_header_struct(self, pos):
        """Returns a header struct if given a position in the array."""
        int_index = divmod(pos, 4)
        header = mp3header.HeaderStruct()
        header.d = self.intarrays[int_index[1]][int_index[0]]
        return header

    def get_size(self):
        """Returns the size of the file in bytes"""
        return self.byte_array.size

    def get_slice(self, start, end):
        "gets a slice of the byte_array"
        return self.byte_array[start:end]

class PythonArrays():
    """One of the possible implementations of the array representing the mp3
       file.  This is the fall-back if other options aren't available"""

    def __init__(self, file):
        self.byte_array = array.array('B')
        file.seek(0,2)
        size = file.tell()
        file.seek(0,0)
        self.byte_array.fromfile(file, size)

    def generate_potential_matches(self, skip=-1, match=255, chunk=None):
        """Gets the next potential header (byte = 255, first 8 of seek tag."""
        skip += 1
        if None == chunk:
            chunk = self.byte_array
        #The index method is considerably faster under certain circumstances,
        #but is also considerably (and pathologically) slower under other
        #circumstances.  The index method is much faster for large areas
        #without a hit, but can take far longer for files with many evenly
        #distributed hits.  Limiting the number of index searches we do
        #per generator is a compromise that allows the generator to skip
        #large tags (which have few hits) quickly, yet still quickly identify
        #files with no hits at all.
            index_method = _MAX_INDEX_METHOD_SEARCHES
        #Additionally, the slice and index overhead increases dramatically with
        #size, so reduce the index attempts for large files.  (These operations
        #should be O(n), but it doesn't appear to be the case.)
            divisor = min(len(self.byte_array)//10*1024*1024,1)
            index_method = min(max(index_method // divisor,10),1)
        else:
            index_method = 0 #use least volatile method for small chunks.
        skip = min(max(skip,0),len(chunk)) #sanity check the skip value
        while index_method:
            try:
                skip += chunk[skip:].index(match)
            except ValueError:
                break
            yield skip
            skip += 1
            index_method -= 1
        cut_array = chunk[skip:]
        for offset, byte in enumerate(cut_array):
            if match == byte:
                yield offset + skip

    def read_header_struct(self, pos):
        """Returns a header struct if given a position in the array."""
        h_int = int.from_bytes(self.byte_array[pos:pos+4], byteorder="little")
        header = mp3header.HeaderStruct()
        header.d = h_int
        return header

    def get_size(self):
        """Returns the size of the file in bytes"""
        return len(self.byte_array)

    def get_slice(self, start, end):
        "gets a slice of the byte_array"
        return self.byte_array[start:end]
    