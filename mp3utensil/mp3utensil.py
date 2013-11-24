# pylint: disable=trailing-whitespace,old-style-class
"""This is the main module of the mp3utensil app.  Call it with
   mp3utensil --help
   for options."""

import config
import mp3file

def conditional_profile(func):
    """Decorator to do nothing if memory profiling is disabled"""
    if config.OPTS.profile_mem:
        print("real profile")
        from memory_profiler import profile
        return profile(func)
    else:
        print("identity profile")
        return func

@conditional_profile
def main():
    """Program entry point"""
    if config.OPTS.verbosity >= 4:
        print(config.OPTS)
    if config.OPTS.sort:
        pass #TODO: implement sorting of file names
    if config.OPTS.verbosity >=1:
        print("Files to process: {}".format(config.OPTS.files))
    for file in config.OPTS.files:
        mfile = mp3file.MP3File(file)
        mfile.scan_file()
        mfile.identify_junk()

class Profiler():
    """Handles profiling our program for performance."""
    def __init__(self,cpu=False, mem=False):
        self.cpu = cpu
        self.mem = mem
        if cpu:
            import cProfile
            from io import StringIO
            self._profiler = cProfile.Profile()
            self._text = StringIO()
            self._stats = None
            self._done = False
        
    def start(self):
        """Begin collecting profile data"""
        if self.cpu:
            self._profiler.enable()
    
    def finish(self):
        """Finish collecting profile data"""
        if self.cpu:
            self._profiler.disable()
        
    def get_results(self, sort='tottime', max_rows=10):
        """Report profile data"""
        if self.cpu:
            if not self._done:
                self.finish()
            import pstats
            self._stats = pstats.Stats(self._profiler, 
                                       stream=self._text).sort_stats(sort)
            self._stats.print_stats(max_rows)
            return self._text.getvalue()
    
if __name__ == '__main__':
    _PERFORMANCE = Profiler(config.OPTS.profile_cpu, config.OPTS.profile_mem)
    _PERFORMANCE.start()

    main()
    
    print(_PERFORMANCE.get_results())
