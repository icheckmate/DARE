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

from pilot import PilotComputeService, PilotDataService, ComputeDataService, State

from daresrc.utils.dareunits import StepUnit
from daresrc.utils.cfgparser import CfgParser

from daresrc.utils.updater import Updater


COORDINATION_URL = "redis://127.0.0.1:6379"


class DareManager(object):
    
    def __init__(self, conffile="/path/to/conf/file"):
        
        self.dare_conffile = conffile


        self.dare_id = "dare-" + str(uuid.uuid1())
 
        self.darecfg = {}

        self.pilot_units_repo = []
        self.pilot_units_repo_new = {}
             
        self.step_units_repo = []
        self.step_units_repo_new = {} 

        self.work_units_repo = []
        self.work_units_repo_new = {}

        self.data_units_repo = []
        self.data_units_repo_new = {}

        self.create_static_workflow()

        self.start()

    def start(self):         
        try:
           #create multiple manyjobs
            logging.info("Create Compute Engine service ")

            pilotjob = pilot_compute_service.create_pilot(pilot_compute_description=pilot_compute_description)
            pilotjob2 = pilot_compute_service.create_pilot(pilot_compute_description=pilot_compute_description)
            ps = pilot_data_service.create_pilot(pilot_data_description=pilot_data_description)
    
            compute_data_service = ComputeDataService()
            compute_data_service.add_pilot_compute_service(pilot_compute_service)
            compute_data_service.add_pilot_data_service(pilot_data_service) 


            pilots_service = pilotService(self.pilot_units_repo, COORDINATION_URL)
            subjobs_service =  SubjobService(pilots_service)

            data_service = Data()
        
            ### run the steps
            for step in self.step_units_repo:
                if self.check_to_start_step(step):
                    step = self.start_step(step)                    
        except KeyboardInterrupt:
            pilots_service.end_manyjob_service()


    def check_to_start_step(self, step):
        flags = []
        if step.get_status() == "New":  
           for step_id in step.UnitInfo['dependent_steps']:
               if self.step_id_status(step_id) == "Done":
                  flags.append(True)
               else:
                  flags.append(False)
        return False if False in flags else True
    
    def step_id_status(self, step_id):
        for step in self.step_units_repo:
            if step_id == step.get_step_id():             
                return step.get_status
        return False
            
    def start_step(self, step):

        starttime = time.time()

        #job started update status 
        step.change_status(self.updater,'Running')
    
        p = []

        for du_id in step.UnitInfo['transfer_input_data_units']:
                p = data_service.submit_filetransfer(self.get_du_desc(du_id))
        data_service.wait_for_transfers()

        for cu_id in step.UnitInfo['work_units']:                    
                cu = subjobs_service.submit_sj(self.get_sj_desc(cu_id))
        subjobs_service.wait_for_subjobs()

        for du_id in step.UnitInfo['transfer_output_data_units']:
                p = data_service.submit_filetransfer(self.get_du_desc(du_id))
        data_service.wait_for_transfers()

        runtime = time.time()-starttime

        #all jobs done update status
        step.change_status(self.updater,'Done')     
        
        return step

    def process_config_file(self):
    
        self.dare_conf_full = CfgParser(self.dare_conffile)
        self.dare_conf_main = self.dare_conf_full.SectionDict('main')
        self.update_site_db = self.dare_conf_main.get('update_web_db', False)
        self.dare_web_id = self.dare_conf_main.get('web_id', False)
        self.updater = Updater(self.update_site_db, self.dare_web_id)

    def create_static_workflow(self):
        self.process_config_file()
        logging.info("Done Reading DARE Config File")

        self.prepare_pilot_units()

        self.prepare_step_units()
        self.prepare_work_units()

        self.prepare_data_units()


    def prepare_pilot_units(self):        
        logging.info("Starting to prepare pilot Units")
              
        pilot_config_file = self.dare_conf_main.get('pilot_config_file', 'default')

        for pilot in self.dare_conf_main['used_pilots'].split(','):
            pilot =  pilot.strip()
            pilot_unit_uuid = "pilot-%s-%s"%(pilot, str(uuid.uuid1()))
            pilot_info_from_main_cfg = self.dare_conf_full.SectionDict(pilot)
 
            logging.info("Preparing pilot unit for  %s"%pilot)
            
            pilot_config_file = pilot_info_from_main_cfg.get('pilot_config_file', "undefined_pilot_file")
             
            if pilot_config_file.lower() == 'default' or pilot_config_file.lower() == 'undefined_pilot_file':
                pilot_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'daredb', 'pilot.cfg')                


            pilot_config_from_db = CfgParser(pilot_config_file)

            info_pilot = pilot_config_from_db.SectionDict(pilot)        

            pilot_compute_service = PilotComputeService()

            # create pilot job service and initiate a pilot job
            pilot_compute_description = {
                             "service_url": info_pilot['service_url'],
                             "number_of_processes": info_pilot['number_of_processes'],                             
                             "working_directory": info_pilot['working_directory'],
                             'affinity_datacenter_label': pilot,              
                             'affinity_machine_label': pilot ,
                             "walltime" : int(pilot_info_from_main_cfg['walltime'])
                            }



            self.pilot_units_repo['pilot_unit_uuid'] = pilot_compute_description

            pilot_data_service = PilotDataService()
            pilot_data_description={
                                "service_url": info_pilot['data_service_url'],
                                "size": 100,   
                                "affinity_datacenter_label": pilot,              
                                "affinity_machine_label": pilot                              
                             }

        logging.info("Done preparing Pilot Units ")




    def find_pilot_id(self, name = ''):
        for ru in self.pilot_units_repo:
           if name and name.strip() == ru.name:
              return  ru.id
        return  ru.id
                      
       
    def prepare_step_units(self):        
        logging.info("Starting to prepare Step Units ")
        
        #TODO:: check for same names
        
        for step in self.dare_conf_main['steps'].split(','):
            logging.info("Preparing Step Units: %s"%step)

            try:
                step_info_from_main_cfg = self.dare_conf_full.SectionDict(step.strip())
            except:
                logging.info("step description section not found for step %s"%step)  
                sys.exit()    
            start_after_steps = []
            
            if step_info_from_main_cfg.get('start_after_steps'):
               start_after_steps = ["step-%s-%s"%(k.strip(),self.dare_id) for k in step_info_from_main_cfg.get('start_after_steps').split(',')]

            step_unit_uuid = "step-%s-%s"%(step_info_from_main_cfg.get('step_name').strip(), self.dare_id)
            info_steps = {
                      "step_id":step_unit_uuid,
                      "dare_web_id":self.dare_web_id ,
                      "name":step_info_from_main_cfg.get('step_name').strip(),
                      "status":'New',

                      "pilot": self.find_pilot_id(step_info_from_main_cfg.get('pilot')),

                      "dependent_steps": step_info_from_main_cfg.get('start_after_steps', '').split(','),
                      "start_after_steps":start_after_steps ,
                      "work_units":[],
                      "transfer_input_data_units":[],
                      "transfer_output_data_units":[]
                      }

            su = StepUnit()
            su.define_param(info_steps)
            self.step_units_repo.append(su)
            self.step_units_repo_new[step_unit_uuid] = su
#        import pdb; pdb.set_trace()  

        logging.info("Done preparing Step Units ")

        
    def prepare_work_units(self):
        self.work_units_repo = []
        logging.info("Starting to prepare Work Units ")

        #add prepare work dir 

        for step in self.dare_conf_main['steps'].split(','):
            logging.info("Preparing Work Units: %s"%step)

            try:
                step_info_from_main_cfg = self.dare_conf_full.SectionDict(step.strip())
            except:
                logging.info("step description section not found for step %s"%step)  
                sys.exit()    


            step_cfg_file = step_info_from_main_cfg.get('step_cfg_file', 'undefined_step_file').strip()

            if step_cfg_file.lower() == 'default' or step_cfg_file.lower() == 'undefined_step_file':
                step_cfg_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'daredb', 'echo_hello.cu')    

            # check if file exists
            cu_conf_full = CfgParser(step_cfg_file) 


            #print step_cfg_file
            


            for input_file in step_info_from_main_cfg.get('input_names', '').split(','):

               # start work unit
                compute_unit_description = {
                        "executable": "/bin/cat",
                        "arguments": ["test1.txt"],
                        "total_core_count": 1,
                        "number_of_processes": 1,
                        "working_directory": data_unit.url,
                        #"working_directory": os.getcwd(),
                        "output": "stdout.txt",
                        "error": "stderr.txt",   
                        "affinity_datacenter_label": "eu-de-south",              
                        "affinity_machine_label": "mymachine-1" 
                }    
                compute_unit = compute_data_service.submit_compute_unit(compute_unit_description)
                logging.debug("Finished setup of PSS and PDS. Waiting for scheduling of PD")
                compute_data_service.wait()


                input_file = input_file.strip()
                cu_uuid = "cu-%s"%(uuid.uuid1(),)
                cu_working_directory = '/tmp/'      
                info_cu =  {"cu_id"   : cu_uuid,
                            "step_id" : "step-%s-%s"%(step_info_from_main_cfg.get('step_name').strip(), self.dare_id),
                            "pilot" : 'any',
                            
                            "arguments" : input_file,
                            "after_units":[],
                            "cu_desc" : cu_conf_full.SectionDict(step_info_from_main_cfg['cu_type']),
                            "output": os.path.join(cu_working_directory , "dare-cu-stdout-"+ cu_uuid +".txt"),
                            "error": os.path.join(cu_working_directory , "dare-cu-stderr-"+ cu_uuid +".txt" ),
                            "working_directory": '',
                            #process thes
                            "cu":''

                           }  
      
                cu = WorkUnit()
                cu.define_param(info_cu)
                self.work_units_repo.append(cu)
                # add this cu to step
                self.add_cu_to_step(info_cu['step_id'], cu_uuid)

        logging.info("Done preparing Work Units ")

    def add_cu_to_step(self, step_id, cu_uuid):

        for i in  range(0, len(self.step_units_repo)):        
            if self.step_units_repo[i].get_step_id() == step_id:
                self.step_units_repo[i].add_work_unit(cu_uuid)


                    

    def prepare_data_units(self):                
        # Create Data Unit Description
        base_dir = "/Users/luckow/workspace-saga/applications/pilot-store/test/data1"
        url_list = os.listdir(base_dir)
        # make absolute paths
        absolute_url_list = [os.path.join(base_dir, i) for i in url_list]
        data_unit_description = {
                                  "file_urls":absolute_url_list,
                                  "affinity_datacenter_label": "eu-de-south",              
                                  "affinity_machine_label": "mymachine-1"
                                 }    

        # submit pilot data to a pilot store    
        data_unit = compute_data_service.submit_data_unit(data_unit_description)
        data_unit.wait()
        logging.debug("Pilot Data URL: %s Description: \n%s"%(data_unit, str(pilot_data_description)))
    
          

    def dare_cancle(self):
        logging.debug("Terminate Pilot Compute/Data Service")
        compute_data_service.cancel()
        pilot_data_service.cancel()
        pilot_compute_service.cancel()
