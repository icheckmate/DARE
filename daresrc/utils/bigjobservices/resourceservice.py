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

class ResourceService(object):

    def __init__(self, resource_units_list,COORDINATION_URL):
        self.subjobs = {}
        self.starttime  = time.time()
        #Flags for controlling dynamic BigJob
        self.resource_units_list = resource_units_list
        self.COORDINATION_URL = COORDINATION_URL
        self.add_additional_resources=True
        self.remove_additional_resources=False

    def start_manyjob_service(self):

        """
        resource_list = []
        resource_dictionary = {"resource_url" : "fork://localhost/", "number_of_processes" : "32", 
                               "processes_per_node":"1", "allocation" : None, "queue" : None, 
                               "working_directory": (os.getcwd() + "/agent"), "walltime":3600 }
        resource_list.append(resource_dictionary)
        """    
        print "Create Dynamic BigJob Service "
        self.mjs = many_job_service(self.resource_units_list, self.COORDINATION_URL)

    def add_resource_to_manyjob_service(self, resource_dictionary):
       # Dynamic BigJob add resources at runtime
       # if more than 30 s - add additional resource
       if time.time()- self.starttime > 10 and self.add_additional_resources==True:
                print "***add additional resources***"
                self.mjs.add_resource(resource_dictionary)
                self.add_additional_resources=False  

    def remove_resource_to_manyjob_service(self):
       # remove resources from dynamic bigjob
       if (time.time()-self.starttime > 15 and remove_additional_resources==True):
           bj_list = self.mjs.get_resources()
           if len(bj_list)>0:
               print "***remove resources: " + str(bj_list[0])
               mjs.remove_resource(bj_list[0])
           remove_additional_resources=False


    def end_manyjob_service():
        try:
            mjs.cancel()
        except:
            pass

