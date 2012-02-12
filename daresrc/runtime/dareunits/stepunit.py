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
            "step_name": step_info["name"],
            "step_type": step_info["type"],
            "step_order_num": step_info["order_num"],
            "step_uuid":  step_info["step_uuid"],
            "step_units":  step_info["units"],        
        }

         
    def get_status(self):
        pass
     
    def get_param(self):
        pass
