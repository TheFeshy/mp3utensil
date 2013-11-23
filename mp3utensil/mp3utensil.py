
import argparse
import numpy as np
import scratch

from mp3frame import MP3Frame

#Global options data
opts = None

def get_options():
    """Gets all options from command line and (tbd) config file"""
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs='+', help="Files to be processed")
    parser.add_argument("-v","--verbosity", action="count", default=0,
                        help="increase output verbosity (max -vvvv)")
    parser.add_argument("-s", "--sort", action="store_true",
                        help="sort the files alphabetically rather than\
                              using their given order")
    return parser.parse_args()

def sort_files(opts):
    print("File sorting TBD")

def make_numpy(f):
    #return np.array(f, dtype=np.dtype('b'))
    with open("testdata/test.mp3", "rb") as f:
        return np.fromfile(f,dtype=np.dtype('I'))

def filter_headers(f,i):
    h = scratch.Header_struct()
    h.d = f[i//4]
    #_h.fourb.b = f[i+1]
    #_h.fourb.c = f[i+2]
    #_h.fourb.d= f[i+3]
    #print(_h.fourb.a)
    print(_h._h.seek_tag)
    if _h._h.seek_tag == 2047:
        return True
    return False

def identify_possible_frames(f, max=-1, frames=None, pos=None):
    """Identifies possible frames, using the seek tag and ruling out 
       some false positives with invalid parameters."""
    if not frames:
        frames = []
    if not pos:
        pos = 0
    print("looking for frames at {}".format(pos))
    f = make_numpy(f)
    possibles = np.where(f[:-3]>254)
    #tmp = f.view("<i4")
    #possibles = filter(lambda x: f[x+1]>224,possibles[0])
    possibles = filter(lambda x: filter_headers(f,x),possibles[0])
    #possibles = map(lambda x: f[x:x+4], possibles[0])
    count = 0
    for p in possibles:
        #if p[1] > 224:
        count += 1
    print(possibles, count)
    '''for i in range(pos, size - 3):
        if 255 == f[i]:# and 224 <= f[i+1]: #pre-screen header values for speed?
            header = MP3Frame.parse_header(f[i:i+4])
            if header:
                frames.append((i, i + header.framesize))
                try:
                    frames.append((i, i + header.framesize))
                except TypeError: #This is what happens when the bitrate is "free"
                    frames.append((i,i)) #TODO: throw an error; we don't actually support "free" bitrate
                max -= 1
                if max <= 0:
                    break'''
    return frames

def lock_on_stream(f, pos=None, consecutive=4):
    """Attempt to find consecutive frames in a stream.  
       Returns the first such frame position"""
    scalar = 2 #How many extra frames do we examine?
    headers = identify_possible_frames(f, max=consecutive * scalar, pos=pos)
    for i, hstart in enumerate(headers):
        nexth = hstart[1]
        found = consecutive
        for hnext in headers[i:]:
            if hnext[0] == nexth:
                found -= 1
                nexth = hnext[1]
                if found <= 0:
                    if opts.verbosity >=3:
                        print("locked on to consecutive mp3 frames at {}".format(hstart[0]))
                    return hstart[0]
    #If we fail, we either ran out of data (do the best we can)
    #or we should expand our window.
    if len(headers) < consecutive *scalar: #ran out of headers
        #TBD: handle this by maximizing the number of headers returned?
        if headers:
            if opts.verbosity >=3:
                print("Insufficient headers found for lock-on")
            return headers[0][0]
        else:
            if opts.verbosity >=3:
                print("No more headers found")
            return None #TBD: this means there is no audio data left
    else:
        return lock_on_stream(f, pos, consecutive * 2)

def read_frames(f, pos=None):
    """Continues to read frames as long as there are no surprises
       Surprises consist of not finding a frame at the end of the previous frame.
       Should we be surprised we will attempt to lock on again."""
    frames = []
    nexth = lock_on_stream(f,pos)
    while None != nexth:
        frame = MP3Frame.read_frame(f,nexth)
        if frame:
            frames.append(frame)
            nexth = frame.get_original_file_position()[1]
        else:
            if opts.verbosity >= 2:
                print("Lock-on lost, attempting to skip non-frame data from byte {}".format(nexth))
            nexth = lock_on_stream(f, nexth)
    return frames
        
    
    
def main():
    global opts
    opts = get_options()
    if opts.sort:
        sort_files(opts)
    if opts.verbosity >=1:
        print("Files to process: {}".format(opts.files))
    frames = []
    for fname in opts.files:
        with open(fname, "rb") as f:
            #end = f.seek(0,2)
            #f.seek(0,0)
            allbytes = f.read()
            frames = read_frames(allbytes)
            
            
if __name__ == '__main__':
    
    import cProfile
    import pstats
    from io import StringIO
    
    import scratch
    
    pr = cProfile.Profile()
    pr.enable()

    #main()
    
    scratch.get_hex()
    #scratch.test_speed()
    
    pr.disable()
    s = StringIO()
    sortby = 'tottime'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(10)
    print(s.getvalue())
    
    