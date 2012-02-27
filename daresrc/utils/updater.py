#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"


import os
import sys

if os.getenv("DARENGS_HOME")!=None:
    DARE_WEB_LIB= os.getenv("DARENGS_HOME")
else:
    DARE_WEB_LIB = "/Users/Sharath/workspace/projects/DARE-CACTUS/darecactus"
 

sys.path.insert(0, os.path.join(DARE_WEB_LIB, 'lib'))
import ormconnector as jobmodel_helper





class Updater():
    def __init__(self,check,jobid):
        try:
            jobmodel_helper.update_job_detail_status('jobid', 'detail_status')
            self.load_update_env = True
        except:
            self.load_update_env = False

    def update_status(self,status, detail_status=""):
	
        if self.load_update_env:
            jobmodel_helper.update_job_detail_status(jobid, detail_status)
            jobmodel_helper.update_job_status(jobid, status)

