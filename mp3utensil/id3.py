# pylint: disable=trailing-whitespace, old-style-class
"""This module contains the methods and classes necessary to identify and
   represent ID3 tags."""
   
import config

# pylint: disable=incomplete-protocol
# ^ we don't "get" members from this binary blob, we "carve them out"
class BinSlice():
    """This class represents an unknown bit of non-frame data within the mp3"""
    def __init__(self, position, chunk, data_class, timecode=None):
        self.position = position
        self.data = chunk
        self.time = timecode
        self.data_class = data_class
        
    def __len__(self):
        return len(self.data)
    
    def carve_out(self, _class, start, end):
        """Carves out a _class from the binary data, and returns a list 
           containing any preceding data (as a new BinSlice, the class
           carved from the data, and any postceding data (again as a
           BinSlice."""
        new_slices = []
        if start: #We have data before the tag, scan it too:
            new_slices.append(BinSlice(self.position, self.data[0:start], 
                                       self.data_class, timecode = self.time))
        carved = _class(data=self.data[start:end],
                        position=self.position+start, time=self.time)
        if len(self.data) > end: #data after tag, scan too:
            new_slices.append(BinSlice(self.position, self.data[end:], 
                                       self.data_class, timecode=self.time))
        return carved, new_slices
    
    def search_within(self, function_list):
        """Searches within a binary bit of data, using a list of search
           functions to identify various types of metadata.  Returns a
           list of any matched metadata, along with a list of any
           binary data we were unable to match."""
        matches = []
        misses = []
        for index, func in enumerate(function_list):
            match, splits = func(self)
            if match:
                matches.append(match)
                for split in splits:
                    split_matches, split_splits = \
                        split.search_within(function_list[index:])
                    if split_matches:
                        matches.append(split_matches)
                    misses += split_splits
        if len(matches):
            return matches, misses
        else:
            return None, [self,]            
# pylint: enable=incomplete-protocol

class ID3v1x():
    """Represents an ID3v1 or ID3v1.1 tag"""
    #These values guide the heuristic "is this really a tag" check.
    HEURISTIC = {0:(29,59,89,123),
                  1:(29,59,89,121)}
    HEURISTIC_MIN = 5
    _FIELDS = ((('title',0,30), ('artist',30,30), ('album',60,30), 
                ('year',90,4), ('comment',94,30), ('genre',124,1)),
               (('title',0,30), ('artist',30,30), ('album',60,30), 
                ('year',90,4), ('comment',94,28), ('track',122,2), 
                ('genre',124,1)))
    def __init__(self, data=None, **kwargs):
        """ignore keyword args; these are here because a common way to create
           this tag is from a BinSlice, which passes information we don't care
           about."""
        self.fields = [x[0] for x in ID3v1x._FIELDS[1]]
        self.data = data
        self.subversion = 0
        if None != data:
            if 0 == data[125] and data[126]:
                self.subversion = 1 #If we have a null then track, it's v1.1
            self.data = bytes(self.data)
        else:
            self.data = bytes([0]*128)
        if 'position' in kwargs:
            self.position = kwargs['position']
        if config.OPTS.verbosity >= 3 and self.position:
            print("Identified ID3v1.{} tag at {}".format(
                    self.subversion, self.position))
            
    def __getattr__(self, index):
        """This should enable tag.title style syntax"""
        if self.fields and index in self.fields:
            return self.data[ID3v1x._FIELDS[index][1]:ID3v1x._FIELDS[index][1]+
                             ID3v1x._FIELDS[index][2]]
        else:
            return self.__dict__[index]
    
    def __setattr__(self, index, value):
        """allow us to use convenient tag.title = "something" syntax"""
        if index != 'fields' and self.fields and index in self.fields:
            start = ID3v1x._FIELDS[self.subversion][index][1]
            for position, char in value:
                self.data[start + position] = ord(char)
            end = len(value)
            #zero pad the value if necessary
            for position in ID3v1x._FIELDS[self.subversion][index][1] - end:
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

def find_and_idenitfy_v1_tags(bin_slice):
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
                