# pylint: disable=trailing-whitespace, old-style-class
"""This module contains the methods and classes necessary to identify and
   represent ID3 tags."""
   
import config

# pylint: disable=incomplete-protocol, too-few-public-methods
# The below class just stores binary blobs until we ID them, so it doesn't
# need many methods or a complete protocol
class Unknown():
    """This class represents an unknown bit of non-frame data within the mp3"""
    def __init__(self, position, chunk, timecode=None):
        self.pos = position
        self.data = chunk
        self.time = timecode
        
    def __len__(self):
        return len(self.data)

class ID3v1x():
    """Represents an ID3v1 or ID3v1.1 tag"""
    _HEURISTIC = {0:(29,59,89,123),
                  1:(29,59,89,121)}
    _HEURISTIC_MIN = 5
    def __init__(self, position, chunk128, timecode=None):
        self.pos = position
        self.data = chunk128
        self.time = timecode
        if 0 == chunk128[125] and chunk128[126]:
            self.subversion = 1 #If we have a null then track, it's v1.1
        else:
            self.subversion = 0 #otherwise it's 1.0
    
    def heuristic_verify(self):
        """Since the normal way to verify ID3 tags is to find them where you
           expect them, and the whole point of this parser is to handle badly
           cut and merged mp3 files, we need another way to validate the tag.
           The only way is by the sheer uselessness of the ID3v1 standard:
           most of the tag will be empty padding.  We'll use the amount of
           padding on the end as _HEURISTIC to verify the tag.
           
           We could improve this by checking that the majority of characters
           in the beginning are ascii as well, though I am uncertain if ID3v1
           supported UTF-8."""
        heuristic_count = 0
        for stop in ID3v1x._HEURISTIC[self.subversion]:
            for character in self.data[stop - 4:stop]:
                if 0 == character:
                    heuristic_count += 1
        return heuristic_count >= ID3v1x._HEURISTIC_MIN

def find_and_idenitfy_v1_tags(data, data_class):
    """takes the offset and slice of previously identified "junk" data
       which is stored in one of the data_classes (our python or numpy
       implementation) and tries to identify ID3 tags in it."""
    chunk = data.data
    timecode = data.time
    position = data.pos
    generator = data_class.generate_potential_matches(skip=-1,
                                                      match=84, #'T'
                                                      chunk=chunk[:-3])
    for i in generator:
        if 65 == chunk[i+1] and 71 == chunk[i+2] and i + 128 <= len(chunk):
            #We found a v1 or 1.1 tag. Verify it as best we can.
            tag = ID3v1x(i+position,chunk[i:i+128], timecode)
            if tag.heuristic_verify():
                found = []
                if i: #We have data before the tag, scan it too:
                    found += find_and_idenitfy_v1_tags(\
                                Unknown(position, chunk[0:i], timecode),
                                data_class)
                if config.OPTS.verbosity >= 3:
                    print("Identified ID3v1.{} tag at {}"\
                          .format(tag.subversion, tag.pos))
                found.append(tag)
                if (len(chunk) - i) > 128: #data after tag, scan too:
                    found += find_and_idenitfy_v1_tags(\
                                Unknown(position, chunk[i+128:], timecode),
                                data_class)
                return found
    return [data,] #Meaning we couldn't identify it; so don't change it
                