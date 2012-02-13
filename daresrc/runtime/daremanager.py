#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"

from .dareunits import DataUnit

from .bigjobservices import ResourceService, SubjobService
from .data import Data

from .updater import Updater

import uuid

from daresrc import logging

import uuid

class DareManager(object):
    
    def __init__(self, webupdate = False, webid = ""):
        
        
        self.dare_id = "dare-" + str(uuid.uuid1())

        self.dare_web_id = webid    
        self.darecfg = {}

        self.webupdater = Updater()

        self.wus_count = 0
        self.dus_count = 0

        self.webupdate = webupdate

    def create_static_workflow():
	    pass

    def start(self):         
	    
        #create multiple manyjobs
        logging.debug("Create Compute Engine service ")

        cmps = Compute()
        cmps.ComputeService(self.resource_repo)
        data = Data()
        total_number_of_jobs=0

        ### run the steps
        for STEP in self.steps:
            starttime = time.time()

            #job started update status
            self.webupdater.update_status(self.webupdate, self.dare_web_id,\
                                          "Running"," In step " + str(STEP.get_position))
            
            p = []
            
            if STEP.get_type() == "Compute":
                
                for unit in STEP.get_units():
                    
                    wu = cmps.submit_wu(unit)
                    wus_count = wus_count +1

                cmps.wait_for_wus()
            
            else:
                for unit in STEP.get_units():
                    p = data.submit_filetransfer(unit)
                    wus_count = wus_count +1

                data.wait_for_transfers()

            runtime = time.time()-starttime

            #all jobs done update status
            self.webupdater.update_status(self.webupdate, self.DAREJOB["jobid"], "Done","")


    def add_resource(self, name = "qb", cfgfile = "resource.cfg", corecount = "8", walltime = "10"):        
        
        rsrc_uuid = "resource-" + str(uuid.uuid1())
        rcfp = CfgParser(cfgfile)                 
        info_resource = rcfp.SectionDict(name)        
        info_resource["Walltime"] = walltime
        info_resource["TotalCoreCount"] = corecount
        r1 = ResourceUnit()                    
        r1.def_param(info_resource)
                   
        self.resources_repo.append(r1)


    def add_step(self, name = "name", type = "data"):        
        step_uuid = "step-" + str(uuid.uuid1())
        
        info_steps = {
                      "step_uuid":step_uuid,
                      "name":name,
                      "type":type , 
                      "units":[]
                      }
        
        self.steps_repo.append(info_steps)
        
        return step_uuid                
        
    def add_wu(self, step = "s1", resource = "r1", conffile = "steps_filename",  add_args = ""):
        
        wu_uuid = "wu-" + str(uuid.uuid1())
                
        scfp    = CfgParser(resource_conf_file)
        info_wu =  {
                   "wu_id"   : wu_uuid,
                   "step_id" : step.get_id(),
                                      
                   }        
        
        # add this wu to step
        self.steps[step.get_id()][units].append(wu_uuid)
        
        self.wus_repo.append(info_wu)



    def add_du(self, step = "0", filename ="file.txt", form_resource = "local", to_resource = "r1"):                
        du_uuid = "du-" + str(uuid.uuid1())
        
        tourl = self.resources[to_resource]["ft_url"]
          
        info_du =  {
                    "du_id"   : du_uuid,
                    "step_id" : step.get_id(),
                    "fromurl":filename,
                    "tourl":tourl,
                    "type":"scp"
                     "Status":"New"
                    }

        # add this du to step
        self.steps[step][units].append(wu_uuid)        
        
        self.dus_repo.append(info_du)
