#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"

import os
#import logging

#logging.basicConfig(level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#darelogger = logging.getLogger(name='DARE')

class DL():
    def debug(self, p):
        print "DARE-Debug-%s"%p

    def info(self, p):
        print "DARE-info-%s"%p
        
    def error(self, p):
        print "DARE-error-%s"%p
        
darelogger = DL()

version = "latest"

try:
    version_file = os.path.join(os.path.abspath('.'), 'VERSION')
    version = open(version_file).read().strip()
    darelogger.info("Loading DARE version: " + version)

except IOError:
    darelogger.error("Cannot read the verison file")


try:
    import ConfigParser
    try:
        _conf_file = os.path.expanduser('~/.darerc')
        darelogger.error("found ~/.darerc file using it for settings")
    except:
        _conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dare.conf')
        darelogger.error("usning default dare config file")       

    cfgparser = ConfigParser.ConfigParser()
    cfgparser.read(_conf_file)
    cfgdict = cfgparser.defaults()
    COORDINATION_URL = str(cfgdict.get('coordination_url', "redis://gw68.quarry.iu.teragrid.org:2525"))

except:
    darelogger.error("dare conf file does not exist. using default coordination mechanism")
    COORDINATION_URL = "redis://gw68.quarry.iu.teragrid.org:6379"

