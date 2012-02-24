#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"

import uuid
import os

from daresrc import logging

from daresrc.utils.updater import Updater

from daresrc.utils.dareunits import DataUnit, StepUnit, ResourceUnit, WorkUnit
from daresrc.utils.bigjobservices import ResourceService, SubjobService
from daresrc.utils.data import Data
from daresrc.utils.cfgparser import CfgParser



class DareManager(object):
    
    def __init__(self, conffile="/path/to/conf/file"):
        
        self.dare_conffile = conffile
        self.updater = Updater()

        self.dare_id = "dare-" + str(uuid.uuid1())
 
        self.darecfg = {}

        self.resource_units_repo = []
        self.step_units_repo = []
        self.step_units_order = {}
        self.work_units_repo = []
        self.data_units_repo = []
      
        self.create_static_workflow()

        self.start()


    def process_config_file(self):
    
        self.dare_conf_full = CfgParser(self.dare_conffile)
        self.dare_conf_main = self.dare_conf_full.SectionDict('main')
        self.update_site_db = self.dare_conf_main.get('update_web_db', False)
        self.dare_web_id = self.dare_conf_main.get('web_id', False)

    def create_static_workflow(self):
        self.process_config_file()
        logging.debug("Done Reading DARE Config File")

        self.prepare_resource_units()
        logging.debug("Done Creating Resource Units")
        self.prepare_step_units()
        logging.debug("Done Creating Step Units")
        self.prepare_work_units()
        logging.debug("Done Creating SubJobs")
        self.prepare_data_units()
        logging.debug("Done Creating Data Units ")


    def prepare_resource_units(self):        
              
        resource_config_file = self.dare_conf_main.get('resource_config_file', 'default')


        for resource in self.dare_conf_main['used_resources'].split(','):
            resource =  resource.strip()
            logging.debug("preparing resource: %s"%resource)
            resource_info_from_main_cfg = self.dare_conf_full.SectionDict(resource)

            resource_config_file = resource_info_from_main_cfg.get('resource_config_file', "undefined_resource_file")
             
            if resource_config_file.lower() == 'default' or resource_config_file.lower() == 'undefined_resource_file':
                resource_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'daredb', 'resource.cfg')                

            resource_config_from_db = CfgParser(resource_config_file)
            info_resource = resource_config_from_db.SectionDict(resource)        

            resource_unit_uuid = "resource-%s-%s"%(resource, self.dare_id) 
            info_resource["walltime"] = int(resource_info_from_main_cfg['walltime'])
            info_resource["total_core_count"] = int(resource_info_from_main_cfg['total_core_count'])
            info_resource["name"] = resource_unit_uuid
            r1 = ResourceUnit()                    
            r1.define_param(info_resource) #check for sufficient info and abort if error.

            self.resource_units_repo.append(r1)


    def prepare_step_units(self, name = "name", type = "data"):        

        self.steps_repo = []
        step_uuid = "step-" + str(uuid.uuid1())
#        import pdb; pdb.set_trace()  
        
        step_order_num = 0

        resource_unit_uuid = "resource-%s-%s"%(step_order_num, self.dare_id)

        info_steps = {
                      "step_uuid":step_uuid,
                      "name":"working_dir_creation",
                      "type":"" , 
                      "units":[]
                      }

        self.step_units_order[step_order_num] = step_uuid 
        
        for step in self.dare_conf_main['steps'].split(','):
            resource_unit_uuid = "resource-%s-%s"%(step_order_num, self.dare_id)
            step_order_num=step_order_num+1
            info_steps = {
                      "step_uuid":step_uuid,
                      "name":step.strip(),
                      "type":'' ,
                      "status":'New', 
                      "units":[]
                      }
            self.step_units_order[step_order_num] = step_uuid 

            self.steps_repo.append(info_steps)
        
    def get_step_id(name):

        for i in  self.steps_repo:
            if i.get("name", None) == name:
               return i.step_uuid
            else:
               return "Unkown"
                    
        
    def prepare_work_units(self, step = "s1", resource = "r1", conffile = "steps_filename",  add_args = ""):

        self.subjobs_repo = []
        #add prepare work dir 

        for wus in self.dare_conf_full.sections:
            wu_uuid = "wu-" + str(uuid.uuid1())                
            info_wu =  {
                       "wu_id"   : wu_uuid,
                       "step_id" : self.get_step_id(),
                       }        
            #read from wu info
            #append it to wu repo
            
        # add this wu to step
        self.steps[step.get_id()][units].append(wu_uuid)
        self.wus_repo.append(info_wu)

    def workunit_resource_match():
        pass

    def prepare_data_units(self, step = "0", filename ="file.txt", form_resource = "local", to_resource = "r1"):                
        du_uuid = "du-" + str(uuid.uuid1())
        
        tourl = self.resources[to_resource]["ft_url"]
          
        info_du =  {
                    "du_id"   : du_uuid,
                    "step_id" : step.get_id(),
                    "fromurl":filename,
                    "tourl":tourl,
                    "type":"scp",
                    "Status":"New"
                    }

        # add this du to step
        self.steps[step][units].append(wu_uuid)        
        self.dus_repo.append(info_du)

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

