#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"

import uuid
import os
import sys
import time

from daresrc import logging

from daresrc.utils.dareunits import DataUnit, StepUnit, ResourceUnit, WorkUnit
from daresrc.utils.bigjobservices import ResourceService, SubjobService
from daresrc.utils.data import Data
from daresrc.utils.cfgparser import CfgParser

from daresrc.utils.updater import Updater


COORDINATION_URL = "advert//:localhost"


class DareManager(object):
    
    def __init__(self, conffile="/path/to/conf/file"):
        
        self.dare_conffile = conffile


        self.dare_id = "dare-" + str(uuid.uuid1())
 
        self.darecfg = {}

        self.resource_units_repo = []
        self.step_units_repo = []
        self.work_units_repo = []
        self.data_units_repo = []
      
        self.create_static_workflow()

        self.start()

    def start(self):         
        
        #create multiple manyjobs
        logging.debug("Create Compute Engine service ")

        cmps = ResourceService(self.resource_units_repo, COORDINATION_URL)
        #data = Data()
        #total_number_of_jobs=0

        ### run the steps
        for step in self.step_units_repo:
            starttime = time.time()

            #job started update status 
            step.change_status(self.updater,'Running')
            
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
            self.updater.update_status("Done")




    def process_config_file(self):
    
        self.dare_conf_full = CfgParser(self.dare_conffile)
        self.dare_conf_main = self.dare_conf_full.SectionDict('main')
        self.update_site_db = self.dare_conf_main.get('update_web_db', False)
        self.dare_web_id = self.dare_conf_main.get('web_id', False)
        self.updater = Updater(self.update_site_db, self.dare_web_id)

    def create_static_workflow(self):
        self.process_config_file()
        logging.debug("Done Reading DARE Config File")

        self.prepare_resource_units()

        self.prepare_step_units()
        self.prepare_work_units()
        #self.prepare_data_units()


    def prepare_resource_units(self):        
        logging.debug("Starting to prepare Resource Units")
              
        resource_config_file = self.dare_conf_main.get('resource_config_file', 'default')


        for resource in self.dare_conf_main['used_resources'].split(','):
            resource =  resource.strip()
            logging.debug("Preparing Resource unit for  %s"%resource)
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

        logging.debug("Done preparing Resource Units ")

    def prepare_step_units(self):        
        logging.debug("Starting to prepare Step Units ")
        
        #TODO:: check for same names
        
        for step in self.dare_conf_main['steps'].split(','):
            logging.debug("Preparing Step Units: %s"%step)

            try:
                step_info_from_main_cfg = self.dare_conf_full.SectionDict(step.strip())
            except:
                logging.debug("step description section not found for step %s"%step)  
                sys.exit()    
            start_after_steps = []
            if step_info_from_main_cfg.get('start_after_steps'):
               start_after_steps = ["step-%s-%s"%(k.strip(),self.dare_id) for k in step_info_from_main_cfg.get('start_after_steps').split(',')]
            step_unit_uuid = "step-%s-%s"%(step_info_from_main_cfg.get('step_name').strip(), self.dare_id)
            info_steps = {
                      "step_id":step_unit_uuid,
                      "dare_job_id":self.dare_web_id ,
                      "name":step_info_from_main_cfg.get('step_name').strip(),
                      "status":'New', 
                      "start_after_steps":start_after_steps ,
                      "work_units":[],
                      "transfer_input_data_units":[],
                      "transfer_output_data_units":[]
                      }

            su = StepUnit()
            su.define_param(info_steps)
            self.step_units_repo.append(su)

#        import pdb; pdb.set_trace()  

        logging.debug("Done preparing Step Units ")

        
    def prepare_work_units(self):
        self.work_units_repo = []
        logging.debug("Starting to prepare Work Units ")

        #add prepare work dir 

        for step in self.dare_conf_main['steps'].split(','):
            logging.debug("Preparing Work Units: %s"%step)

            try:
                step_info_from_main_cfg = self.dare_conf_full.SectionDict(step.strip())
            except:
                logging.debug("step description section not found for step %s"%step)  
                sys.exit()    


            step_cfg_file = step_info_from_main_cfg.get('step_cfg_file', 'undefined_step_file').strip()

            if step_cfg_file.lower() == 'default' or step_cfg_file.lower() == 'undefined_step_file':
                step_cfg_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'daredb', 'echo_hello.wu')    

            # check if file exists
            wu_conf_full = CfgParser(step_cfg_file) 

            print step_cfg_file
            
            for input_file in step_info_from_main_cfg.get('input_names').split(','):

                input_file = input_file.strip()
                wu_uuid = "wu-%s"%(uuid.uuid1(),)
                wu_working_directory = '/tmp/'      
                info_wu =  {"wu_id"   : wu_uuid,
                            "step_id" : "step-%s-%s"%(step_info_from_main_cfg.get('step_name').strip(), self.dare_id),
                            "resource" : 'any',

                            "arguments" : input_file,
                            "after_units":[],
                            "wu_desc" : wu_conf_full.SectionDict(step_info_from_main_cfg['wu_type']),
                            "output": os.path.join(wu_working_directory , "dare-wu-stdout-"+ wu_uuid +".txt"),
                            "error": os.path.join(wu_working_directory , "dare-wu-stderr-"+ wu_uuid +".txt" ),
                            "working_directory": ''
                           }  
      
                wu = WorkUnit()
                wu.define_param(info_wu)
                self.work_units_repo.append(wu)
                # add this wu to step
                self.add_wu_to_step(info_wu['step_id'], wu_uuid)

        logging.debug("Done preparing Work Units ")

    def add_wu_to_step(self, step_id,wu_uuid):

        for i in  range(0, len(self.step_units_repo)):        
            if self.step_units_repo[i].get_step_id() == step_id:
                self.step_units_repo[i].add_work_unit(wu_uuid)


		        
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

    def get_step_id(name):

        for i in  self.steps_repo:
            if i.get("name", None) == name:
               return i.step_uuid
            else:
               return "Unkown"
                    

    def workunit_resource_match():
        pass

