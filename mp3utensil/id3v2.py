# pylint: disable=trailing-whitespace, old-style-class
"""This module contains the methods and classes necessary to identify and
   represent ID3v2 tags."""
   
import config

# pylint: disable=too-few-public-methods
class ID3v2x():
    """A class representing an ID3v2.x tag"""
    def __init__(self, data=None, **kwargs):
        """ignore keyword args; these are here because a common way to create
           this tag is from a BinSlice, which passes information we don't care
           about."""
        #TODO: for now just treat this as a binary chunk; but we'll parse and
        #manipulate it later.
        self.data = bytearray(data)
        self.subversion = self.data[3]
        self.subsubversion = self.data[4]
        if 'position' in kwargs:
            self.position = kwargs['position']
        if config.OPTS.verbosity >= 3 and None != self.position:
            print("Identified ID3v2.{}.{} tag at {}".format(
                    self.subversion, self.subsubversion, self.position))
           
def find_and_identify_v2_tags(bin_slice):
    """takes the offset and slice of previously identified "junk" data
       which is stored in one of the data_classes (our python or numpy
       implementation) and tries to identify ID3v2 tags in it."""
    chunk=bin_slice.data
    data_class = bin_slice.data_class
    generator = data_class.generate_potential_matches(skip=-1,
                                                      match=73, #'I'
                                                      chunk=chunk[:-10])
    for i in generator:
        if 68 == chunk[i+1] and 51 == chunk[i+2] and 255 > chunk[i+3] and \
            255 > chunk[i+4] and 128 > chunk[i+6] and 128 > chunk[i+7] and \
            128 > chunk[i+8] and 128 > chunk[i+9]:
            #Highest bit is masked off in length; covered by the "if" above
            tag_length = (chunk[i+6] << 21) + (chunk[i+7] << 14) + \
                         (chunk[i+8] << 7) + chunk[i+9]
            #remember that header length (10 bytes) is not included in frame
            return bin_slice.carve_out(ID3v2x, i, i+10+tag_length)
    return None, [bin_slice,]
