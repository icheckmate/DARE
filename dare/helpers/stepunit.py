#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"


import os
from dare.api import StepUnit

class StepUnitStates(object):
    Unknown = 0
    New = 1
    Running = 2
    Done = 3
    Canceled = 4
    Failed = 5
    Queue = 6


class StepUnit(StepUnit):
     
    def __init__(self):
          
        self.type = "steps"
        self.UnitInfo = {}       

    
    def define_param(self, step_info):
        self.UnitInfo = {        
            "step_id": step_info["step_id"],
            "dare_web_id":step_info["dare_web_id"],
            "name": step_info["name"],
            "status": step_info["status"],
            "compute_units":  step_info["compute_units"],
            "transfer_input_data_units":  step_info["transfer_input_data_units"],        
            "transfer_output_data_units":  step_info["transfer_output_data_units"],
            "start_after_steps": step_info["start_after_steps"]
        }

    def get_step_id(self):
        return self.UnitInfo['step_id']

    def add_cu(self, cu_id):
        self.UnitInfo['compute_units'].append(cu_id)  
        return True 

    def add_input_du(self, cu_id):
        self.UnitInfo['transfer_input_data_units'].append(cu_id)  
        return True 
    
    def get_status(self):
        return self.UnitInfo['status'] 

    def set_status(self, status):
        self.UnitInfo['status'] = status 
          

    def get_param(self):
        pass

    def __repr__(self):
        return self.UnitInfo['name']
