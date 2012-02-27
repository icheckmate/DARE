#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"


import os

from daresrc.api import DareUnit


class WorkUnit(DareUnit):
     
    def __init__(self):
          
        self.type = "job"
        self.UnitInfo = {}        
         
    def define_param(self, wu_info):
        """
        sj = description()
        sj.executable =  sj_desc['executable']
        sj.arguments = sj_desc['arguments']
        sj.environment = sj_desc['environment']
        sj.number_of_processes = sj_desc['number_of_processes']
        sj.working_directory = sj_desc['working_directory']
        sj.spmd_variation = sj_desc['spmd_variation']
        sj.output= sj_desc['output']
        sj.error = sj_desc['error']
        """
        self.UnitInfo = {
            "type" : "compute",
            "name" : wu_info["name"],
            "step_id" : wu_info["step_id"],
            "wu_id" : wu_info["wu_id"],  
            "executable" : wu_info["wu_desc"]["executble"],
            "number_of_processes" : wu_info["number_of_processes"],
            "spmd_variation" : wu_info["spmd_variation"],
            "environment" : wu_info["environment"],    
            "output" : os.path.join(wu_info["working_directory"], "stdout-"+ wu_info["wu_id"] +".txt"),
            "error" : os.path.join(wu_info["working_directory"], "stderr-"+ wu_info["wu_id"] +".txt" ),
            "appname" : "simple",
    
             #varrying
            "resource" : resource,
            "working_directory" : working_directory,
            "arguments" : args
        }
       
    
    
    def get_status(self):
        pass
     
    def get_param(self):
        pass

