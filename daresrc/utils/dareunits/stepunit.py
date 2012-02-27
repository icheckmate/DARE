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
            "step_id": step_info["step_id"],
            "dare_job_id":step_info["dare_job_id"],
            "name": step_info["name"],
            "status": step_info["status"],
            "work_units":  step_info["work_units"],
            "transfer_input_data_units":  step_info["transfer_input_data_units"],        
            "transfer_output_data_units":  step_info["transfer_output_data_units"],
        }

    def get_step_id(self):
        return self.UnitInfo['step_id']

    def add_work_unit(self, wu_id):
        self.UnitInfo['work_units'].append(wu_id)  
        return True 
    
    def change_status(self, updater,status):        
        self.UnitInfo['status'] =  status
        updater.update_status( self.dare_web_id, status, self.UnitInfo['name'])

    def get_status(self):
        return self.UnitInfo['status'] 
     
    def get_param(self):
        pass
