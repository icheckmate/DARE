#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"


import os

from daresrc.api import DareUnit
from bigjob import description

class WorkUnit(DareUnit):
     
    def __init__(self):
          
        self.type = "job"
        self.UnitInfo = {}        
         
    def define_param(self, wu_info):


        self.UnitInfo = {
           # for dare   
            "resource" : wu_info["resource"],
            "appname" : "simple",
            "type" : "compute",
            "step_id" : wu_info["step_id"],
            "wu_id" : wu_info["wu_id"],  
            "status": 'New',

            #for saga/BJ
            "executable" : wu_info["wu_desc"]["executable"],
            "number_of_processes" : wu_info["wu_desc"]["number_of_processes"],
            "spmd_variation" : wu_info["wu_desc"]["spmd_variation"],
            "output" : wu_info["output"],
            "error" : wu_info["error"],

            #varrying
            "working_directory" : wu_info["working_directory"],

            # processes these args
            "arguments": '',
            "environment" : '',    

        }
       
    def prepare_arguments(self):
        pass
    
    def prepare_environment(self):
	    pass

    def get_desc(self):

        sj = description()
        sj.executable =  self.UnitInfo['executable']
        sj.arguments = [self.UnitInfo['arguments']]
        sj.environment = [self.UnitInfo['environment']]
        sj.number_of_processes = self.UnitInfo['number_of_processes']
        sj.working_directory = self.UnitInfo['working_directory']
        sj.spmd_variation = self.UnitInfo['spmd_variation']
        sj.output= self.UnitInfo['output']
        sj.error = self.UnitInfo['error']

        return sj

    def get_wu_id(self):
        return self.UnitInfo['wu_id']
	    
    def get_status(self):
        return self.UnitInfo['status']
     
    def get_param(self):
        pass

