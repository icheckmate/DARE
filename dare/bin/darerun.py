#!/usr/bin/env python
__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"

import sys
import os
import optparse
parser = optparse.OptionParser()

sys.path.insert(0, os.path.abspath( "../.."))

from dare import darelogger
from dare.core.daremanager import DareManager

def main():
    
    # parse conf files
    #parser = optparse.OptionParser()
    #parser.add_option("-c", "--conf_job", dest="conf_job", help="job configuration file")
    #(options, args) = parser.parse_args()

    #confjob = options.conf_job

    if (len(sys.argv)> 1): 
       conffile = sys.argv[1] 
    else:
       raise Exception, "missing dare configurtion file"


    darelogger.debug("starting DARE")
    try:
       dare = DareManager(conffile)
       #dare.start()
    except KeyboardInterrupt:
       dare.cancel()

    darelogger.debug("DARE Exec Done")
     
if __name__ == "__main__":
    if (len(sys.argv)> 1): 
       conffile = sys.argv[1] 
    else:
       raise Exception, "missing dare configurtion file" 
    main()