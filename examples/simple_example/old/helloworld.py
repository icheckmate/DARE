#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"


import os
import sys
import time
import uuid

import optparse

sys.path.insert(0,"..")

from dare.dare import DareManager

from hello.hello import *

APP_PWD = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
       
       
    resources = []   
    dm = DareManager()
    
    """
    #optional
    dm.add_resource("TG") #or LONI or FG-Cloud or machine name
    
    dm.add_step(name = "name", 
    #                  type = "data")    
    
    du1 = dm.add_du(
                     step = s1, 
                     filename ="file.txt", 
                     form_resource = "local", 
                     to_resource = r1
                     )

    s2 = dm.add_step(
                      name = "name", 
                      type = "compute")       
    wu1 = dm.add_wu(
                    step = s2,"dsa" , 
                    resource = r1, 
                    conffile = "steps_filename",  
                    add_args = "")
    
    #or 
    register_hello = dm.add_wu_import(hello())
   
    
    s3 = dm.add_step(
                      name = "name",
                      type = "data")    
    du2 = dm.add_du(
                    step = s3, 
                    filename ="file.txt", 
                    form_resource = r1, 
                    to_resource = "local")
    
    """
    print "running the steps in the following order" #, dm.steps.get_order()
        
    print "Dare is starting"
    dm.start()
