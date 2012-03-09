#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"

import os
import logging

logging.basicConfig(level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p',
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(name='DARE')


version = "latest"

try:
    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','VERSION')
    version = open(version_file).read().strip()
    logger.info("Loading DARE version: " + version)

except IOError:
    logger.error("cannot read the verison file")

