# pylint: disable=trailing-whitespace
"""This handles setting up the configuration of the program,
   currently via command line options."""
   

import argparse

def get_options():
    """Gets all options from command line and (tbd) config file"""
    parser = argparse.ArgumentParser()
    parser.description = \
    "mp3utensil: A tool for verifying, merging, and splitting mp3 files."
    parser.add_argument("files", nargs='*', help="Files to be processed")
    parser.add_argument("-v","--verbosity", action="count", default=0,
                        help="increase output verbosity (max -vvvv)")
    parser.add_argument("-s", "--sort", action="store_true",
                        help="sort the files alphabetically rather than\
                              using their given order")
    parser.add_argument("--profile", help=argparse.SUPPRESS, 
                        action="store_true")
    parser.epilog = "Example:\nmp3utensil.py myfile.mp3"
    return parser.parse_args()

#Global options data
OPTS = get_options()
