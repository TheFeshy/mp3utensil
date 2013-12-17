# pylint: disable=old-style-class
"""This module contains the methods and classes necessary to identify and
   represent ID3 tags."""

import config

# pylint: disable=too-few-public-methods
class ID3v1x():
    """Represents an ID3v1 or ID3v1.1 tag"""
    #These values guide the heuristic "is this really a tag" check.
    HEURISTIC = {0:(29,59,89,123),
                  1:(29,59,89,121)}
    HEURISTIC_MIN = 5
    _FIELDS = ({'title':(3,30), 'artist':(33,30), 'album':(63,30),
                'year':(93,4), 'comment':(97,30), 'genre':(127,1)},
               {'title':(3,30), 'artist':(33,30), 'album':(63,30),
                'year':(93,4), 'comment':(97,28), 'track':(125,2),
                'genre':(127,1)})
    def __init__(self, data=None, **kwargs):
        """ignore keyword args; these are here because a common way to create
           this tag is from a BinSlice, which passes information we don't care
           about."""
        self.subversion = 0
        if None != data:
            if 0 == data[125] and data[126]:
                self.subversion = 1 #If we have a null then track, it's v1.1
            self.data = bytearray(data)
        else:
            self.data = bytearray([0]*128)
        if 'position' in kwargs:
            self.position = kwargs['position']
        if config.OPTS.verbosity >= 3 and None != self.position:
            print("Identified ID3v1.{} tag at {}".format(
                    self.subversion, self.position))

    def __getattr__(self, index):
        """This should enable tag.title style syntax"""
        if index in ID3v1x._FIELDS[1].keys():
            item = ID3v1x._FIELDS[self.subversion][index]
            if 'track' == index:
                return int(self.data[item[0]+1])
            if 'genre' == index:
                return int(self.data[item[0]])
            field = self.data[item[0]:item[0]+item[1]]
            field = bytes([x for x in field if x != 0 and x != 32])
            return field.rstrip().decode('latin-1')
        else:
            return self.__dict__[index]

    def __setattr__(self, index, value):
        """allow us to use convenient tag.title = "something" syntax"""
        if index in ID3v1x._FIELDS[1].keys():
            if 'track' == index: #special handling for this field
                self.subversion = 1
                item = ID3v1x._FIELDS[self.subversion][index]
                self.data[item[0]] = 0
                self.data[item[0]+1] = value
                return
            if 'genre' == index:
                item = ID3v1x._FIELDS[self.subversion][index]
                self.data[item[0]] = value
                return
            try:
                value = value.encode(encoding='latin-1')
            except TypeError:
                pass #This means we probably got passed bytes anyway
            item = ID3v1x._FIELDS[self.subversion][index]
            if len(value) > item[1]: #data too big:
                ValueError("The ID3 field is not large enough")
            for position, char in enumerate(value):
                self.data[item[0] + position] = char
            end = len(value)
            #zero pad the value if necessary
            for position in range(item[1] - end):
                self.data[end+position] = 0
        else:
            object.__setattr__(self, index, value)

def heuristic_verify(data):
    """Since the normal way to verify ID3 tags is to find them where you
       expect them, and the whole point of this parser is to handle badly
       cut and merged mp3 files, we need another way to validate the tag.
       The only way is by the sheer uselessness of the ID3v1 standard:
       most of the tag will be empty padding.  We'll use the amount of
       padding on the end as HEURISTIC to verify the tag.

       We could improve this by checking that the majority of characters
       in the beginning are ascii as well, though I am uncertain if ID3v1
       supported UTF-8 (most likely not.)

       This should only check for null characters, but some brain-dead
       taggers use spaces instead."""
    if config.OPTS.no_id31_heuristics:
        return True #Skip this if the user doesn't want it.
    subversion = 0
    if 0 == data[125] and data[126]:
        subversion = 1
    heuristic_count = 0
    for stop in ID3v1x.HEURISTIC[subversion]:
        for character in data[stop - 4:stop]:
            if 0 == character or 32 == character:
                heuristic_count += 1
    return heuristic_count >= ID3v1x.HEURISTIC_MIN

def find_and_identify_v1_tags(bin_slice):
    """takes the offset and slice of previously identified "junk" data
       which is stored in one of the data_classes (our python or numpy
       implementation) and tries to identify ID3 tags in it."""
    chunk=bin_slice.data
    data_class = bin_slice.data_class
    generator = data_class.generate_potential_matches(skip=-1,
                                                      match=84, #'T'
                                                      chunk=chunk[:-3])
    for i in generator:
        if 65 == chunk[i+1] and 71 == chunk[i+2] and i + 128 <= len(chunk):
            #We found a v1 or 1.1 tag. Verify it as best we can.
            block = chunk[i:i+128]
            if heuristic_verify(block):
                return bin_slice.carve_out(ID3v1x, i, i+128)
    return None, [bin_slice,]
                