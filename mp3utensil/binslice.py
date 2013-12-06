# pylint: disable=trailing-whitespace, old-style-class
"""This module contains the methods and classes necessary to identify and
   represent ID3 tags."""

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
