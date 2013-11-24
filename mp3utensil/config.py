# pylint: disable=trailing-whitespace
"""This handles setting up the configuration of the program,
   currently via command line options."""
   
import sys   

import argparse

def get_options():
    """Gets all options from command line and (tbd) config file"""
    parser = argparse.ArgumentParser(prog="mp3utensil", add_help=False)
    parser.description = \
    "mp3utensil: A tool for verifying, merging, and splitting mp3 files."
    standard_options = parser.add_argument_group("Standard Options")
    advanced_options = parser.add_argument_group("Advanced Options", 
                        "Nitty-gritty MP3 format options.  Use with care.")
    debug_options = parser.add_argument_group("Debug Options",
                        "Used for poking around the program for performance \
                        and bug repair.")
    standard_options.add_argument("files", nargs='*', 
                        help="Files to be processed")
    standard_options.add_argument("-v","--verbosity", action="count", default=0,
                        help="increase output verbosity (max -vvvv)")
    standard_options.add_argument("-s", "--sort", action="store_true",
                        help="sort the files alphabetically rather than\
                              using their given order")
    standard_options.add_argument("-h", "--help", action="store_true",
                        help="display this help menu.")
    advanced_options.add_argument("--consecutive-frames-to-id", type=int,
                        default=5, help="We identify valid frames by finding \
                        consecutive valid frames back-to-back.  You can set \
                        the number of such consecutive frames required for a \
                        positive ID here.", metavar="[integer 1 to 50]", 
                        choices=range(1,50))
    debug_options.add_argument("--no-numpy", action="store_true",
                        help="Don't use numpy for processing, even if it\
                              is available")
    debug_options.add_argument("--profile-cpu", help=argparse.SUPPRESS, 
                        action="store_true")
    debug_options.add_argument("--profile-mem", help=argparse.SUPPRESS, 
                        action="store_true")
    parser.epilog = "Example:\nmp3utensil.py myfile.mp3"
    opts = parser.parse_args()
    if opts.help:
        print(parser.print_help())
        sys.exit(0)        
    return opts

#Global options data
OPTS = get_options()
