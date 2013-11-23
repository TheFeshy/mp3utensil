
import config
import mp3file

def main():
    if not config.opts:
        config.get_options()
    if config.opts.verbosity >= 4:
        print(config.opts)
    if config.opts.sort:
        pass #ToDo: impliment sorting of file names
    if config.opts.verbosity >=1:
        print("Files to process: {}".format(config.opts.files))
    for file in config.opts.files:
        mfile = mp3file.MP3File(file)
        mfile.scan_file()
        mfile.identify_junk()
            
            
if __name__ == '__main__':
    
    if not config.opts:
        config.get_options()
    print(config.opts)
        
    if config.opts.profile:
        import cProfile
        import pstats
        from io import StringIO
        pr = cProfile.Profile()
        pr.enable()

    main()
    
    if config.opts.profile:
        pr.disable()
        sortby = 'tottime'
        s = StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats(10)
        print(s.getvalue())
    
    