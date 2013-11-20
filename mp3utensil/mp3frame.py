
from bitstring import Bits
from mp3protocoltables import MP3Prot
from collections import namedtuple

Header = namedtuple('Header','valid, version, layer, kbitrate, frequency, \
                    emphasis, crc_protect, padding, private, channel, \
                    mode_extension, copyright, original, framesize')

class MP3Frame():
    """Encapsulates and provides methods to work with individual mp3 frames."""
    
    @staticmethod
    def parse_header( fourbytes):
        """Takes four bytes, and tries to parse the header.  Will return 
           none if the data is invalid.  If you are only checking to see 
           if this *is* a valid header, use the "justchecking" to exit 
           early with a truth condition."""
        header = None
        seektag = (fourbytes[0] == 255 and fourbytes[1] >= 224)
        #TBD Verify this is four bytes long
        #seektag = '0b11111111111' == data[:11] #save the seek tag as either true or false
        if seektag: #Quick check to fail early in case this is invalid header data
            data = Bits(fourbytes)
            version = MP3Prot.versions[data[11:13].uint]
            layer = MP3Prot.layers[data[13:15].uint]
            if "reserved" != version and "reserved" != layer: #We need these values to be valid to go on
                kbitrate = MP3Prot.bitrates[version][layer][data[16:20].uint]
                frequency = MP3Prot.frequency[version][data[20:22].uint]
                emphasis = MP3Prot.emphasis[data[30:32].uint]
                if "reserved" != kbitrate and "reserved" != frequency and "reserved" != emphasis:
                    crc_protect = data[15]
                    padding = data[22]
                    private = data[23]
                    channel = MP3Prot.channel[data[24:26].uint]
                    mode_extension = data[26:28]
                    cr = data[28]
                    original = data[29]
                    if "free" != kbitrate:
                        samplebits = MP3Prot.samples[version][layer]
                        framesize = ((kbitrate * 1000 * (samplebits//8)) // frequency) + padding
                    else:
                        framesize = None
                    header = Header(seektag, version, layer, kbitrate, frequency, emphasis, 
                                         crc_protect, padding, private, channel, mode_extension,
                                         cr, original, framesize)

        return header
    
    @staticmethod
    def read_frame(f, pos):
        fourbytes = f[pos:pos+4]
        header = MP3Frame.parse_header(fourbytes)
        if not header:
            return None
        if header.crc_protect:
            crc = f[pos+4:pos+6]
        else:
            crc = None
        data = f[pos + 4 + (2 * header.crc_protect): pos + header.framesize]
        #TBD: what do we do with ancillary data, if anything?
        return MP3Frame(header, crc, data, None, pos)
        
    def __init__ (self, header, crc, data, anc, start):
        self._header = header
        self._crc = crc
        self._data = data
        self._anc = anc
        self._start = start #original start location
        
    def get_original_file_position(self):
        return (self._start,self._header.framesize + self._start)
                        
                                     
                    