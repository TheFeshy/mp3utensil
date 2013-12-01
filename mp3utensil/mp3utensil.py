# pylint: disable=trailing-whitespace,old-style-class
"""This is the main module of the mp3utensil app.  Call it with
   mp3utensil --help
   for options."""

from  functools import wraps

import config
import mp3file

def conditional_memory_profile(func):
    """Enables memory profiling if set in the command line options."""
    if config.OPTS.profile_mem:
        from memory_profiler import profile
        return profile(func)
    else:
        return func
    
def conditional_cpu_profile(sort, max_rows):
    """Enables CPU time profiling if set in the command line options."""
    def profile_decorator(func):
        """decorator function with required function signature"""
        @wraps(func)
        def wrapped(*args, **kwargs):
            """allows us to wrap the call we want in other functions"""
            import cProfile
            import pstats
            from io import StringIO
            profiler = cProfile.Profile()
            text = StringIO()
            profiler.enable()
            wrap_func = func(*args, **kwargs)
            profiler.disable()
            stats = pstats.Stats(profiler, stream=text).sort_stats(sort)
            stats.print_stats(max_rows)
            print(text.getvalue())
            return wrap_func           
        if config.OPTS.profile_cpu:
            return wrapped
        else:
            return func
    return profile_decorator
    
@conditional_cpu_profile(sort='tottime', max_rows=100)
@conditional_memory_profile
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
         
if __name__ == '__main__':
    main()
