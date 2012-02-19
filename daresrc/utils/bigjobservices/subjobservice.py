#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"

"""
A tool to run applications in Distributed environments
depends on BigJob and local file trasfer mechanisms like
"""

import sys
import os
import time
import traceback

#add troy path

try:
   from bigjob import bigjob, subjob, description
   from bigjob_dynamic.many_job import *

except:
   if os.getenv("BIGJOB_HOME")!=None:
       PSTAR_HOME= os.getenv("BIGJOB_HOME")
   sys.path.insert(0,BIGJOB_HOME)

   from bigjob import bigjob, subjob, description
   from bigjob_dynamic.many_job import *


COORDINATION_URL = "redis://gw68.quarry.iu.teragrid.org:2525"


class SubjobService(object):
    
    def __init__(self,ResourceService):
	
        self.starttime  = time.time()
        self.jobs = []
        self.job_start_times = {}
        self.job_states = {}
        
        self.resourceservice = ResourceService
        self.NUMBER_JOBS = 0

    def submit_sj(self, sj_desc):
       # print "[INFO]", wu_desc_conf
        self.NUMBER_JOBS = self.NUMBER_JOBS + 1
        subjob = self.resourceservice.create_job(sj_desc)

    def reset(self):
        self.NUMBER_JOBS = 0
        self.starttime  = time.time()
        self.jobs = []
        self.job_start_times = {}
        self.job_states = {}

    def wait_for_subjobs(self):
        while 1: 
            finish_counter=0
            result_map = {}
            for i in range(0, self.NUMBER_JOBS):
                old_state = self.job_states[self.jobs[i]]
                state = self.jobs[i].get_state()
                if result_map.has_key(state) == False:
                    result_map[state]=0
                result_map[state] = result_map[state]+1
                #print "counter: " + str(i) + " job: " + str(jobs[i]) + " state: " + state
                if old_state != state:
                    print "Job " + str(jself.obs[i]) + " changed from: " + old_state + " to " + state
                if old_state != state and has_finished(state)==True:
                    print "Job: " + str(self.jobs[i]) + " Runtime: " + str(time.time()-self.job_start_times[self.jobs[i]]) + " s."
                if has_finished(state)==True:
                    finish_counter = finish_counter + 1
                job_states[jobs[i]]=state
                                
            print "Current states: " + str(result_map) 
            time.sleep(5)
            if finish_counter == self.NUMBER_JOBS:
                break

