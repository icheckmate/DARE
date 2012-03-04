#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"


import os

from daresrc.api import DareUnit

class DataUnit(DareUnit):
     
    def __init__(self):          
        self.type = "data"
        self.UnitInfo = {}

    def define_param(self, du_info):

        #define data units here, assign some default param
        
        self.UnitInfo = {
            "name" : du_info["name"],
            "type" :"data",
            "step_name" :du_info["step_name"],
            "appname" : du_info["file_transfer"],
            "ft_type" : du_info["scp"],
            "source_url" : os.path.join(du_info["source_url"] , du_info["source_fullpath"]),
            "dest_url" : os.path.join(du_info["dest_url"], du_info["dest_dir"])          
            }    
    def define_param_2(self):
        
        self.UnitInfo = {        
            "name" :du_info["name"],
            "type" :"compute" ,
            "step_name" :du_info["step_name"], 
            "executable" :du_info["/bin/ln"], 
            "number_of_processes" : "1",
            "spmd_variation" :"single",
            "arguments" :"-s " + os.path.join(du_info["input_dir"],du_info["input_name"]) +" "+ os.path.join(du_info["working_directory"],du_info["input_name"]), 
            "environment" :"",
            "working_directory" :working_directory,
            "output" : os.path.join(du_info["working_directory"], "stdout-"+ str(du_info["du_id"])+".txt"),
            "error" : os.path.join(du_info["working_directory"], "stderr-"+ str(du_info["du_id"])+".txt" ),
            "appname" :"linking",
            "resource" :du_info["resource"]
            }
            

    def get_status(self):
        pass
     
    def get_param(self):
        pass


