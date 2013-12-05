# pylint: disable=trailing-whitespace, old-style-class

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
    _HEURISTIC = (0,(29,59,89,123),
                 1,(29,59,89,121))
    _HEURISTIC_MIN = 5
    def __init__(self, position, chunk128, timecode=None):
        self.pos = position
        self.data = chunk128
        self.time = timecode
        if 0 == chunk128[126] and chunk128[127]:
            self.subversion = 1 #If we have a null then track, it's v1.1
        else:
            self.subversion = 0 #otherwise it's 1.0
    
    def heuristic_verify(self):
        """Since the normal way to verify ID3 tags is to find them where you
           expect them, and the whole point of this parser is to handle badly
           cut and merged mp3 files, we need another way to validate the tag.
           The only way is by the sheer uselessness of the ID3v1 standard:
           most of the tag will be empty padding.  We'll use the amount of
           padding on the end as _HEURISTIC to verify the tag."""
        heuristic_count = 0
        for stop in ID3v1x._HEURISTIC[self.subversion]:
            for c in self.data[stop - 4:stop]:
                if 0 == c:
                    heuristic_count += 1
        return heuristic_count >= ID3v1x._HEURISTIC_MIN
        
                
           
        


def find_and_idenitfy_tags(chunk, data_class):
    """takes the offset and length of previously identified "junk" data
       which is stored in one of the data_classes (our python or numpy
       implementation) and tries to identify ID3 tags in it."""
    last_found = 0
    while True:
        generator = data_class.generate_potential_matches(skip=last_found,
                                                          match=84, #'T'
                                                          chunk=chunk[:-3])
        for i in generator:
            if 65 == chunk[i+1] and \
            71 == chunk[i+2] and \
            i + 128 <= len(chunk):
                #We found a v1 or 1.1 tag. Verify it as best we can.
                