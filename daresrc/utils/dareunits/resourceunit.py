#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"


import os


from daresrc.api import DareUnit

#import saga

class ResourceUnit(DareUnit):
     
    def __init__(self):          
        self.type = "resources"
        self.UnitInfo = {}
        
        
    def define_param(self, info_resource):    
        
        self.UnitInfo= {            
            "name" : info_resource["name"], 
            "type" : "resource", 
            "resource_url" : info_resource["resource_url"], 
            "processes_per_host" : info_resource["cores_per_node"], 
            "allocation" : info_resource["allocation"], 
            "queue" : info_resource["queue"],
            "userproxy" : info_resource["userproxy"], 
            "working_directory" : info_resource["working_directory"],
            "input_directory" :  info_resource["input_directory"],
            "filetransfer_url" : resource_conf["filetransfer_url"],  
            "walltime" : info_resource["walltime"],
            "total_core_count" :  info_resource["total_core_count"]
            }
        
    
    def get_status(self):
        pass
     
    def get_param(self):
        pass
