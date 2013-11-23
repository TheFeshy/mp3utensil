
import mp3header

class MP3Frame():
    """Encapsulates and provides methods to work with individual mp3 frames."""
    __slots__ = ["header", "position", "length"]
    
    def __init__(self, header_struct, position):
        self.header = mp3header.MP3Header(header_struct) #TODO: raise exception if header is invalid.
        self.position = position
        self.length = self.header.get_framesize()

                        
                                     
                    