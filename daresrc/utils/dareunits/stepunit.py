#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"


import os

from daresrc.api import DareUnit

class StepUnit(DareUnit):
     
    def __init__(self):
          
        self.type = "steps"
        self.UnitInfo = {}       
    
    def define_param(self, step_info):
        self.UnitInfo = {        
            "step_uuid": step_info["step_uuid"],
            "name": step_info["name"],
            "status": step_info["status"],
            "work_units":  step_info["work_units"],
            "transfer_input_data_units":  step_info["transfer_input_data_units"],        
            "transfer_output_data_units":  step_info["transfer_output_data_units"],        

        }

         
    def get_status(self):
        pass
     
    def get_param(self):
        pass
