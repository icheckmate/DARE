#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"


import os
import sys

if os.getenv("DARENGS_HOME")!=None:
    DARENG_HOME= os.getenv("DARENGS_HOME")
else:
    DARENGS_HOME = "/home/cctsg/software/DARE-NGS/"


sys.path.insert(0,DARENGS_HOME)



class Updater():
    def __init__(self):
        try:
            import darengs.lib.ModelConnector as jobmodel_helper
            load_update_env = "true"
        except:
            load_update_env = "false"

    def update_status(self,check,jobid,status, detail_status=""):
        if check == "true":
            jobmodel_helper.update_job_detail_status(jobid, detail_status)
            jobmodel_helper.update_job_status(jobid, status)
        else:
            pass
