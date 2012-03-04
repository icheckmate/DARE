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

        self.compute_pilot_repo = {}
        self.data_pilot_repo= {}

        self.compute_pilot_pilotjobs=[]
        self.data_pilot_pilotjobs = [] 
             
        self.step_units_repo = {}

        self.compute_units_repo = {}
        self.data_units_repo = {}

        self.create_static_workflow()

        self.start()

    def start(self):         
        try:
           #create multiple manyjobs
            logging.info("Create Compute Engine service ")

            pilot_compute_service = PilotComputeService()
            pilot_data_service = PilotDataService()

            for compute_pilot, desc in self.compute_pilot_repo.items():
                self.compute_pilot_pilotjobs.append(pilot_compute_service.create_pilot(pilot_compute_description=desc))

            for data_pilot, desc in self.data_pilot_repo.items():            
                self.data_pilot_pilotjobs.append(pilot_data_service.create_pilot(pilot_data_description=desc))
    
            self.compute_data_service = ComputeDataService()
            self.compute_data_service.add_pilot_compute_service(pilot_compute_service)
            self.compute_data_service.add_pilot_data_service(pilot_data_service) 

            ### run the steps
            for step_id in self.step_units_repo.keys():
                #import pdb; pdb.set_trace()
                if self.check_to_start_step(step_id):
                    step = self.start_step(step_id)                    
        except KeyboardInterrupt:
            self.dare_cancel()


    def check_to_start_step(self, step_id):
        flags = []
        
        if self.step_units_repo[step_id].get_status() == "New":  
           for dep_step_id in self.step_units_repo[step_id].UnitInfo['start_after_steps']:
               if self.step_units_repo[dep_step_id].get_status() == "Done":
                  flags.append(True)
               else:
                  flags.append(False)
        return False if False in flags else True
    
    def start_step(self, step_id):

        starttime = time.time()

        #job started update status 
        self.step_units_repo[step_id].change_status(self.updater,'Running')
    
        p = []
        logging.debug(" Started running %s "%step_id)
        for du_id in self.step_units_repo[step_id].UnitInfo['transfer_input_data_units']:
                data_unit = data_service.submit_filetransfer(self.get_du_desc(du_id))
                logging.debug("Pilot Data URL: %s Description: \n%s"%(data_unit, str(pilot_data_description)))
                data_unit.wait()
        #        self.compute_data_service.wait()
        logging.debug(" input tranfer for step %s complete"%step_id)
        for cu_id in self.step_units_repo[step_id].UnitInfo['work_units']:                    
                compute_unit = self.compute_data_service.submit_compute_unit(self.get_cu_desc(cu_id))
                logging.debug("Finished setup of PSS and PDS. Waiting for scheduling of PD")
 
        logging.debug(" Compute jobs for step %s complete"%step_id)

        self.compute_data_service.wait()

        for du_id in self.step_units_repo[step_id].UnitInfo['transfer_output_data_units']:
                data_unit = self.compute_data_service.submit_data_unit(data_unit_description)
                logging.debug("Pilot Data URL: %s Description: \n%s"%(data_unit, str(pilot_data_description)))
                data_unit.wait()
        logging.debug(" Output tranfer for step %s complete"%step_id)

        #        self.compute_data_service.wait()

        runtime = time.time()-starttime

        #all jobs done update status
        self.step_units_repo[step_id].change_status(self.updater,'Running')

        
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
            compute_pilot_uuid = "compute-pilot-%s-%s"%(pilot, str(uuid.uuid1()))
            data_pilot_uuid = "compute-pilot-%s-%s"%(pilot, str(uuid.uuid1()))

            pilot_info_from_main_cfg = self.dare_conf_full.SectionDict(pilot)
 
            logging.info("Preparing pilot unit for  %s"%pilot)
            
            pilot_config_file = pilot_info_from_main_cfg.get('pilot_config_file', "undefined_pilot_file")
             
            if pilot_config_file.lower() == 'default' or pilot_config_file.lower() == 'undefined_pilot_file':
                pilot_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'daredb', 'pilot.cfg')                


            pilot_config_from_db = CfgParser(pilot_config_file)

            info_pilot = pilot_config_from_db.SectionDict(pilot)        


            # create pilot job service and initiate a pilot job
            pilot_compute_description = {
                             "service_url": info_pilot['service_url'],
                             "working_directory": info_pilot['working_directory'],
                             'affinity_datacenter_label': pilot,              
                             'affinity_machine_label': pilot ,
                             "number_of_processes":  int(pilot_info_from_main_cfg['number_of_processes']),                             
                             "walltime" : int(pilot_info_from_main_cfg['walltime'])
                            }


            self.compute_pilot_repo[compute_pilot_uuid] = pilot_compute_description


            pilot_data_description={
                                "service_url": info_pilot['data_service_url'],
                                "size": 100,   
                                "affinity_datacenter_label": pilot+'-dcl',              
                                "affinity_machine_label": pilot + '-aml'                              
                             }

            self.data_pilot_repo[data_pilot_uuid] = pilot_data_description

        logging.info("Done preparing Pilot Units ")


                      
       
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

                      "pilot": step_info_from_main_cfg.get('pilot'),

                      "start_after_steps":start_after_steps ,
                      "work_units":[],
                      "transfer_input_data_units":[],
                      "transfer_output_data_units":[]
                      }

            su = StepUnit()
            su.define_param(info_steps)
            self.step_units_repo[step_unit_uuid] = su
#        import pdb; pdb.set_trace()  

        logging.info("Done preparing Step Units ")

        
    def prepare_work_units(self):

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
            all_cu_confs= CfgParser(step_cfg_file) 

            cu_conf = all_cu_confs.SectionDict( step_info_from_main_cfg.get('cu_type', 'default').strip())
            #print step_cfg_file           
            for input_file in step_info_from_main_cfg.get('input_names', '').split(','):

                input_file = input_file.strip()
                cu_uuid = "cu-%s"%(uuid.uuid1(),)
                cu_working_directory = '/tmp/'  #data_unit.url
                cu_step_id  = "step-%s-%s"%(step_info_from_main_cfg.get('step_name').strip(), self.dare_id),
                # start work unit
                compute_unit_description = {
                        "executable": cu_conf["executable"],
                        "arguments": cu_conf["arguments"],
                        "total_core_count": 1,
                        "number_of_processes": 1,
                        "working_directory": cu_working_directory,
                        "output":"dare-cu-stdout-"+ cu_uuid +".txt",
                        "error": "dare-cu-stderr-"+ cu_uuid +".txt",   
                        "affinity_datacenter_label": "eu-de-south",              
                        "affinity_machine_label": "mymachine-1" 
                       }    


                self.compute_units_repo[cu_uuid]=compute_unit_description
                # add this cu to step
                self.add_cu_to_step(cu_step_id, cu_uuid)

        logging.info("Done preparing Work Units ")

    def add_cu_to_step(self, step_id, cu_uuid):

        for key in self.step_units_repo.keys():        
            if key == step_id:
                self.step_units_repo[key].add_cu(cu_uuid)

    def add_du_to_step(self, step_id, cu_uuid):

        for key in  self.step_units_repo.keys():        
            if key == step_id:
                self.step_units_repo[key].add_du(cu_uuid)
                    

    def prepare_data_units(self):                

        logging.info("Starting to prepare Data Units ")

        for step in self.dare_conf_main['steps'].split(','):
            logging.info("Preparing Work Units: %s"%step)

            try:
                step_info_from_main_cfg = self.dare_conf_full.SectionDict(step.strip())
            except:
                logging.info("step description section not found for step %s"%step)  
                sys.exit()    


            #print step_cfg_file 
            absolute_url_list = step_info_from_main_cfg.get('input_names', '').split(',')
       
            # Create Data Unit Description
            #   base_dir = "/Users/Sharath/workspace/projects/backups"
            #   url_list = os.listdir(base_dir)
            #   absolute_url_list = [os.path.join(base_dir, i) for i in url_list]

            du_uuid = "du-%s"%(uuid.uuid1(),)
            # make absolute paths
            du_step_id  = "step-%s-%s"%(step.strip(), self.dare_id),

            data_unit_description = {
                                      "file_urls":absolute_url_list,
                                      "affinity_datacenter_label": "eu-de-south",              
                                      "affinity_machine_label": "mymachine-1"
                                     }    

                # submit pilot data to a pilot store    

            self.data_units_repo[du_uuid]=data_unit_description
            # add this cu to step
            self.add_du_to_step(du_step_id, du_uuid)


    def dare_cancel(self):
        logging.debug("Terminate Pilot Compute/Data Service")
        self.compute_data_service.cancel()
        for pilot_data_service in self.data_pilot_pilotjobs:
            pilot_data_service.cancel()         
        for pilot_compute_service in self.compute_pilot_pilotjobs:
            pilot_compute_service.cancel() 