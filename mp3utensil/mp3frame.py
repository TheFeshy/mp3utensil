# pylint: disable=trailing-whitespace, old-style-class, slots-on-old-class
""" Used for storing and interpreting individual frames in an mp3 file. """
import mp3header

class MP3Frame():
    """Encapsulates and provides methods to work with individual mp3 frames."""
    __slots__ = ["header", "position", "length"]
    
    def __init__(self, header_struct, position, validated=False):
        self.header = mp3header.MP3Header(header_struct, validated)
        if not self.header.valid:
            pass #TODO: raise exception if header is invalid.
        self.position = position
        self.length = self.header.get_framesize()
        
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
                    