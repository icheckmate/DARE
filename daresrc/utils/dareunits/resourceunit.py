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
        self.id = info_resource["ru_id"]
        self.name =  info_resource["name"]

        self.UnitInfo = {
                        "ru_id" : info_resource["ru_id"], 
                        "name" : info_resource["name"],
                        "resource_url" : info_resource["resource_url"], 
                        "processes_per_host" : info_resource["cores_per_node"], 
                        "allocation" : info_resource["allocation"], 
                        "queue" : info_resource["queue"],
                        "userproxy" : info_resource["userproxy"], 
                        "working_directory" : info_resource["working_directory"],
                        "input_directory" :  info_resource["input_directory"],
                        "walltime" : info_resource["walltime"],
                        "total_core_count" :  info_resource["total_core_count"]
                        }

        self.extrainfo = {"filetransfer_url" : info_resource["filetransfer_url"],  
                          "name" : info_resource["name"], 
                          "type" : "resource", 
                           }
        
    
    def get_status(self):
        pass

    def get_id(self):
        return self.UnitInfo['step_id']

    def get_desc(self):

        ru_list_item = {}
        ru_list_item['resource_url'] = self.UnitInfo['resource_url']
        ru_list_item['processes_per_host'] = self.UnitInfo['processes_per_host']
        ru_list_item['allocation'] = self.UnitInfo['allocation']
        ru_list_item['queue'] = self.UnitInfo['queue']
        ru_list_item['working_directory'] = self.UnitInfo['working_directory']
        ru_list_item['input_directory'] = self.UnitInfo['input_directory']
        ru_list_item['walltime'] = self.UnitInfo['walltime']
        ru_list_item['number_of_processes'] = self.UnitInfo['total_core_count']

        return ru_list_item

    def get_param(self):
        pass
