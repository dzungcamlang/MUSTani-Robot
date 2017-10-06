#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt
import mustani.util as util
import mustani.recorder as recorder
import mustani.err_logger as err_logger
import mustani.hatch as hatch
from mustani.version import __version__

def main(argv):
    endless_loop = False
    debug = False
    outfile = None
    infile = None
    dict = None
    plot = False
    wave = False

    print ("mustani "+__version__)

    if (len(argv) > 0):
        try:                                
            opts, args = getopt.getopt(argv, "ahelpv~cos:w:r:t:d:",
             ["analysis", "help", "error", "loop", "plot", "verbose", "wave", "create", "overview",
              "show=", "write=", "read=", "train=", "delete="
             ])
        except getopt.GetoptError:
            usage()
            sys.exit(2)
        for opt, arg in opts: 
            if (opt in ("-h", "--help")):
                usage()
                sys.exit(0)
            if (opt in ("-e", "--error")):
                errlog = err_logger.err_logger()
            if (opt in ("-l", "--loop")):
                endless_loop = True
            if (opt in ("-p", "--plot")):
                if (endless_loop == False):
                    plot = True
                else:
                    print ("Plotting only works without loop option!")
                    sys.exit(0)
            if (opt in ("-v", "--verbose")):
                debug = True
            if (opt in ("-~", "--wave")):
                wave = True
            if opt in ("-c", "--create"):
                recreate_dict(debug)
                sys.exit(0)
            if opt in ("-o", "--overview"):
                show_dict_ids(debug)
                sys.exit(0)
            if opt in ("-a", "--analysis"):
                show_dict_analysis(debug)
                sys.exit(0)
            if opt in ("-s", "--show"):
                show_word_entries(arg, debug)
                sys.exit(0)
            if opt in ("-w", "--write"):
                outfile = arg
            if opt in ("-r", "--read"):
                infile = arg
            if opt in ("-t", "--train"):
                dict = arg
            if opt in ("-d", "--delete"):
                delete_word(arg, debug)
                sys.exit(0)

    hatched = hatch.hatch()
    hatched.add("endless_loop", endless_loop)
    hatched.add("debug", debug)
    hatched.add("plot", plot)
    hatched.add("wave", wave)
    hatched.add("outfile", outfile)
    hatched.add("infile",infile )
    hatched.add("dict", dict)
    recorder.recorder(hatched)

def recreate_dict(debug):
    print ("recreating dictionary from raw input files...")
    utilities = util.util(debug)
    utilities.recreate_dict_from_raw_files()

def delete_word(dict, debug):
    if (dict != "*"):
        print ("deleting "+dict+" from dictionary")
    else:
        print ("deleting all enttries from dictionary")
    utilities = util.util(debug)
    utilities.deletefromdict(dict)

def show_word_entries(dict, debug):
    print (dict+" entries in dictionary:")
    print
    utilities = util.util(debug)
    utilities.showdictentry(dict)

def show_dict_ids(debug):
    print ("current entries in dictionary:")
    utilities = util.util(debug)
    utilities.showdictentriesbyid()

def show_dict_analysis(debug):
    print ("dictionary analysis:")
    utilities = util.util(debug)
    print (utilities.compile_analysis(utilities.getDICT()))

def usage():
    print ("usage:\n")
    print (" -h --help           : this help\n")
    print (" -l --loop           : loop forever\n")
    print (" -e --error          : redirect sdterr to error.log\n")
    print (" -p --plot           : plot results (only without loop option)\n")
    print (" -v --verbose        : enable verbose mode\n")
    print (" -~ --wave           : create *.wav files (token/tokenN.wav) for")
    print ("                       each detected word\n")
    print (" -c --create         : create dict from raw input files\n")
    print (" -o --overview       : list all dict entries\n")
    print (" -s --show   [word]  : show detailed [word] entry information")
    print ("                       '*' shows all entries!\n")
    print (" -w --write  [file]  : write raw to [dir/filename]\n")
    print (" -r --read   [file]  : read raw from [dir/filename]\n")
    print (" -t --train  [word]  : add raw data to raw dictionary file\n")
    print (" -d --delete [word]  : delete [word] from dictionary and exit.")
    print ("                       '*' deletes everyting!\n")
    print (" -a --analysis       : show dictionary analysis and exit.\n")


main(sys.argv[1:])
