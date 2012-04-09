#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"

import uuid
import os
import sys
import time
import pdb
import threading

from daresrc import logger

from pilot import PilotComputeService, PilotDataService, ComputeDataService, State

from daresrc.utils.stepunit import StepUnit ,StepUnitStates
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

        self.compute_pilot_service_repo=[]
        self.data_pilot_service_repo = [] 
             
        self.step_units_repo = {}

        self.compute_units_repo = {}
        self.data_units_repo = {}

        self.create_static_workflow()

        self.start()

    def start(self):         
        try:
           #create multiple manyjobs
            logger.info("Create Compute Engine service ")

            self.pilot_compute_service = PilotComputeService()
            self.pilot_data_service = PilotDataService()

            for compute_pilot, desc in self.compute_pilot_repo.items():
                self.compute_pilot_service_repo.append(self.pilot_compute_service.create_pilot(pilot_compute_description=desc))

            for data_pilot, desc in self.data_pilot_repo.items():            
                self.data_pilot_service_repo.append(self.pilot_data_service.create_pilot(pilot_data_description=desc))
    
            self.compute_data_service = ComputeDataService()
            self.compute_data_service.add_pilot_compute_service(self.pilot_compute_service)
            self.compute_data_service.add_pilot_data_service(self.pilot_data_service) 

            self.step_thread= {}

            ### run the steps
            self.step_start_lock=threading.RLock()
            self.step_run_lock=threading.RLock()

            for step_id in self.step_units_repo.keys():
                    logger.info(" Sumitted step %s "%step_id)
                    self.step_start_lock.acquire()
                    self.start_thread_step_id =step_id
                    self.step_start_lock.release()

                    self.step_thread[step_id] = threading.Thread(target=self.start_step)
                    
                    self.step_thread[step_id].start()
                    
             
            while(1):     
                count_step = [v.is_alive() for k,v in self.step_thread.items()]
                #print 'count_step', count_step
                if not True in count_step and len(count_step)>0:                      
                    break
                time.sleep(10)
                       

            logger.info(" All Steps Done processing")

            self.cancel()
        except:
            self.cancel()


    def check_to_start_step(self, step_id):
        flags = []
        print self.step_units_repo[step_id].UnitInfo['start_after_steps']
        if self.step_units_repo[step_id].get_status() == StepUnitStates.New:  
           for dep_step_id in self.step_units_repo[step_id].UnitInfo['start_after_steps']:
               if self.step_units_repo[dep_step_id].get_status() != StepUnitStates.Done:
                  flags.append(False)
               print self.step_units_repo[dep_step_id].get_status()
        return False if False in flags else True


    def start_step(self):
        self.step_start_lock.acquire()
        step_id = self.start_thread_step_id
        self.step_start_lock.release()

        while(1):
            logger.info(" Checking to start step %s "%step_id)
            if self.check_to_start_step(step_id):
                self.run_step(step_id)
                break
            else:
                logger.info(" Cannot start this step %s sleeping..."%step_id)
                time.sleep(10)
    
    def run_step(self, step_id):
        #self.step_run_lock.acquire()
        starttime = time.time()

        #job started update status 
        self.step_units_repo[step_id].change_status(self.updater,'Running')
    
        p = []
        logger.info(" Started running %s "%step_id)
        for du_id in self.step_units_repo[step_id].UnitInfo['transfer_input_data_units']:
                #data_unit = self.compute_data_service.submit_data_unit(self.data_units_repo[du_id])
                #logger.debug("Pilot Data URL: %s Description: \n%s"%(data_unit, str(self.data_units_repo[du_id])))
                #data_unit.wait()
        #        self.compute_data_service.wait()
            logger.debug(" input tranfer for step %s complete"%step_id)
         
        jobs = []
        job_start_times = {}
        job_states = {}
        NUMBER_JOBS = len(self.step_units_repo[step_id].UnitInfo['compute_units'])
        for cu_id in self.step_units_repo[step_id].UnitInfo['compute_units']:                    
                compute_unit = self.compute_data_service.submit_compute_unit(self.compute_units_repo[cu_id])
                logger.info("Compute Unit: Description: \n%s"%(str(self.compute_units_repo[cu_id])))
                jobs.append(compute_unit)
                job_start_times[compute_unit]=time.time()
                job_states[compute_unit] = compute_unit.get_state()
        

        logger.debug("************************ All Jobs submitted ************************")

        while 1: 
            finish_counter=0
            result_map = {}
            for i in range(0, NUMBER_JOBS):
                old_state = job_states[jobs[i]]
                state = jobs[i].get_state()
                if result_map.has_key(state) == False:
                    result_map[state]=0
                result_map[state] = result_map[state]+1
                #print "counter: " + str(i) + " job: " + str(jobs[i]) + " state: " + state
                if old_state != state:
                    logger.debug( "Job " + str(jobs[i]) + " changed from: " + old_state + " to " + state)
                if old_state != state and self.has_finished(state)==True:
                    logger.info( "%s step Job: "%(self.step_units_repo[step_id].UnitInfo['name']) + str(jobs[i]) + " Runtime: " + str(time.time()-job_start_times[jobs[i]]) + " s.")
                if self.has_finished(state)==True:
                    finish_counter = finish_counter + 1
                job_states[jobs[i]]=state
                
            logger.debug( "Current states: " + str(result_map) )
            time.sleep(5)
            if finish_counter == NUMBER_JOBS:
                break

        #self.compute_data_service.wait() 
        logger.debug(" Compute jobs for step %s complete"%step_id)

        
        #for du_id in self.step_units_repo[step_id].UnitInfo['transfer_output_data_units']:
        #        data_unit = self.compute_data_service.submit_data_unit(self.data_units_repo[du_id])
        #        logger.debug("Pilot Data URL: %s Description: \n%s"%(data_unit, str(pilot_data_description)))
        #        data_unit.wait()
        #logger.debug(" Output tranfer for step %s complete"%step_id)

        #        self.compute_data_service.wait()

        #runtime = time.time()-starttime

        #all jobs done update status

        self.step_units_repo[step_id].change_status(self.updater, StepUnitStates.Done)
        #self.step_run_lock.release()


    def has_finished(self, state):
        state = state.lower()
        if state=="done" or state=="failed" or state=="canceled":
            return True
        else:
            return False

        
    def process_config_file(self):
    
        self.dare_conf_full = CfgParser(self.dare_conffile)
        self.dare_conf_main = self.dare_conf_full.SectionDict('main')
        self.update_site_db = self.dare_conf_main.get('update_web_db', False)
        self.dare_web_id = self.dare_conf_main.get('web_id', False)
        self.updater = Updater(self.update_site_db, self.dare_web_id)

    def create_static_workflow(self):
        self.process_config_file()
        logger.info("Done Reading DARE Config File")

        self.prepare_pilot_units()

        self.prepare_step_units()
        self.prepare_compute_units()

        self.prepare_data_units()


    def prepare_pilot_units(self):        
        logger.info("Starting to prepare pilot Units")
              
        pilot_config_file = self.dare_conf_main.get('pilot_config_file', 'default')

        for pilot in self.dare_conf_main['used_pilots'].split(','):
            pilot =  pilot.strip()
            compute_pilot_uuid = "compute-pilot-%s-%s"%(pilot, str(uuid.uuid1()))
            data_pilot_uuid = "compute-pilot-%s-%s"%(pilot, str(uuid.uuid1()))

            pilot_info_from_main_cfg = self.dare_conf_full.SectionDict(pilot)
 
            logger.info("Preparing pilot unit for  %s"%pilot)
            
            pilot_config_file = pilot_info_from_main_cfg.get('pilot_config_file', "undefined_pilot_file")
             
            if pilot_config_file.lower() == 'default' or pilot_config_file.lower() == 'undefined_pilot_file':
                pilot_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'daredb', 'pilot.cfg')                


            pilot_config_from_db = CfgParser(pilot_config_file)

            info_pilot = pilot_config_from_db.SectionDict(pilot)        


            # create pilot job service and initiate a pilot job
            pilot_compute_description = {
                             "service_url": info_pilot['service_url'],
                             "working_directory": info_pilot['working_directory'],
                             'affinity_datacenter_label': '%s-adl'%pilot,              
                             'affinity_machine_label': '%s-aml'%pilot ,
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

        logger.info("Done preparing Pilot Units ")


                      
       
    def prepare_step_units(self):        
        logger.info("Starting to prepare Step Units ")
        
        #TODO:: check for same names
        
        for step in self.dare_conf_main['steps'].split(','):
            logger.info("Preparing Step Units: %s"%step)

            try:
                step_info_from_main_cfg = self.dare_conf_full.SectionDict(step.strip())
            except:
                logger.info("step description section not found for step %s"%step)  
                sys.exit()    
            start_after_steps = []
            
            if step_info_from_main_cfg.get('start_after_steps'):
               start_after_steps = ["step-%s-%s"%(k.strip(),self.dare_id) for k in step_info_from_main_cfg.get('start_after_steps').split(',')]

            step_unit_uuid = "step-%s-%s"%(step_info_from_main_cfg.get('step_name').strip(), self.dare_id)
            info_steps = {
                      "step_id":step_unit_uuid,
                      "dare_web_id":self.dare_web_id ,
                      "name":step_info_from_main_cfg.get('step_name').strip(),
                      "status": StepUnitStates.New,

                      "pilot": step_info_from_main_cfg.get('pilot'),

                      "start_after_steps":start_after_steps ,
                      "compute_units":[],
                      "transfer_input_data_units":[],
                      "transfer_output_data_units":[]
                      }

            su = StepUnit()
            su.define_param(info_steps)
            self.step_units_repo[step_unit_uuid] = su


        logger.info("Done preparing Step Units ")

        
    def prepare_compute_units(self):

        logger.info("Starting to prepare Compute Units ")

        #add prepare work dir 

        for step in self.dare_conf_main['steps'].split(','):
            logger.info("Preparing compute Units: %s"%step)

            try:
                step_info_from_main_cfg = self.dare_conf_full.SectionDict(step.strip())
            except:
                logger.info("step description section not found for step %s"%step)  
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
                cu_step_id  = "step-%s-%s"%(step_info_from_main_cfg.get('step_name').strip(), self.dare_id)
                # start work unit
               
                compute_unit_description = {
                        "executable": cu_conf["executable"],
                        "arguments": self.prepare_cu_arguments(input_file,cu_conf),
                        "total_core_count": 1,
                        "number_of_processes": 1,
                        #"working_directory": cu_working_directory,
                        "output":"dare-cu-stdout-"+ cu_uuid +".txt",
                        "error": "dare-cu-stderr-"+ cu_uuid +".txt",   
                        "affinity_datacenter_label": "%s-adl"%step_info_from_main_cfg.get('resource', self.dare_conf_main['used_pilots'].split(',')[0]).strip(),              
                        "affinity_machine_label": "%s-aml"%step_info_from_main_cfg.get('resource', self.dare_conf_main['used_pilots'].split(',')[0]).strip() 
                       }    


                self.compute_units_repo[cu_uuid]=compute_unit_description
                # add this cu to step
                self.step_units_repo[cu_step_id].add_cu(cu_uuid)

        logger.info("Done preparing compute Units ")

    def prepare_cu_arguments(self, input_name, cu_conf):                    
        
        arguements = ''            
        
        if cu_conf.get('arguments', '').strip() != '':
           return [input_name]
        # check for mutiple args in different types
        else:
           pass
        return [input_name] 
      

    def prepare_data_units(self):                

        logger.info("Starting to prepare Data Units ")

        for step in self.dare_conf_main['steps'].split(','):
            logger.info("Preparing Data Units: %s"%step)

            try:
                step_info_from_main_cfg = self.dare_conf_full.SectionDict(step.strip())
            except:
                logger.info("step description section not found for step %s"%step)  
                sys.exit()    


            #print step_cfg_file 
            absolute_url_list = step_info_from_main_cfg.get('input_names', '').split(',')
       
            # Create Data Unit Description
            #   base_dir = "/Users/Sharath/workspace/projects/backups"
            #   url_list = os.listdir(base_dir)
            #   absolute_url_list = [os.path.join(base_dir, i) for i in url_list]

            du_uuid = "du-%s"%(uuid.uuid1(),)
            # make absolute paths
            du_step_id  = "step-%s-%s"%(step.strip(), self.dare_id)

            data_unit_description = {
                                      "file_urls":absolute_url_list,
                                      "affinity_datacenter_label": "eu-de-south",              
                                      "affinity_machine_label": "mymachine-1"
                                     }    

                # submit pilot data to a pilot store    

            self.data_units_repo[du_uuid]=data_unit_description
            # add this cu to step
            self.step_units_repo[du_step_id].add_input_du(du_uuid)


    def cancel(self):
        logger.debug("Terminate Pilot Compute/Data Service")
        self.compute_data_service.cancel()

        self.pilot_data_service.cancel()         
        self.pilot_compute_service.cancel() 