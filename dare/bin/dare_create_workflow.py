#!/usr/bin/env python
__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"

import sys
sys.path.insert(0,"..")
import optparse
parser = optparse.OptionParser()

import daresrc.runtime
from daresrc.utils.cfgparser import CfgParser


if __name__ == "__main__":
    
    # parse conf files
    #parser = optparse.OptionParser()
    #parser.add_option("-c", "--conf_job", dest="conf_job", help="job configuration file")
    #(options, args) = parser.parse_args()

    #confjob = options.conf_job
    conffile = sys.argv[1]
    
    dareconf = CfgParser(conffile)
    info_dare = dareconf.SectionDict('main') 
    
    dare = DareManager()
    
    pass
   