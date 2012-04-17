#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"

import uuid
import os
import sys
import time
import threading

from dare import darelogger

from .stepunit import StepUnit ,StepUnitStates
from .cfgparser import CfgParser

class PrepareWorkFlow(object):
    """DARE prepare WF:
       - reads different configuration files
       - creates work flow, pilot units, step units, compute units, data units."""

    """Constructor"""
    def __init__(self, conffile):
        "" ""
        self.dare_conffile = conffile
        self.dare_id = "dare-" + str(uuid.uuid1())
        self.darecfg = {}
        self.compute_pilot_repo = {}
        self.data_pilot_repo= {}
        self.step_units_repo = {}
        self.compute_units_repo = {}
        self.data_units_repo = {}

        self.create_static_workflow()

        
    def process_config_file(self):
    
        self.dare_conf_full = CfgParser(self.dare_conffile)
        self.dare_conf_main = self.dare_conf_full.SectionDict('main')
        self.update_site_db = self.dare_conf_main.get('update_web_db', False)
        self.dare_web_id = self.dare_conf_main.get('web_id', False)


    def create_static_workflow(self):
        self.process_config_file()
        darelogger.info("Done Reading DARE Config File")

        self.prepare_pilot_units()

        self.prepare_step_units()
        self.prepare_compute_units()

        self.prepare_data_units()


    def prepare_pilot_units(self):        
        darelogger.info("Starting to prepare pilot Units")
              
        pilot_config_file = self.dare_conf_main.get('pilot_config_file', 'default')

        for pilot in self.dare_conf_main['used_pilots'].split(','):
            pilot =  pilot.strip()
            compute_pilot_uuid = "compute-pilot-%s-%s"%(pilot, str(uuid.uuid1()))
            data_pilot_uuid = "compute-pilot-%s-%s"%(pilot, str(uuid.uuid1()))

            pilot_info_from_main_cfg = self.dare_conf_full.SectionDict(pilot)
 
            darelogger.info("Preparing pilot unit for  %s"%pilot)
            
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

        darelogger.info("Done preparing Pilot Units ")


                      
       
    def prepare_step_units(self):        
        darelogger.info("Starting to prepare Step Units ")
        
        #TODO:: check for same names
        
        for step in self.dare_conf_main['steps'].split(','):
            darelogger.info("Preparing Step Units: %s"%step)

            try:
                step_info_from_main_cfg = self.dare_conf_full.SectionDict(step.strip())
            except:
                darelogger.info("step description section not found for step %s"%step)  
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


        darelogger.info("Done preparing Step Units ")

        
    def prepare_compute_units(self):
        """add prepare work dir """

        darelogger.info("Starting to prepare Compute Units ")


        for step in self.dare_conf_main['steps'].split(','):
            darelogger.info("Preparing compute Units: %s"%step)

            try:
                step_info_from_main_cfg = self.dare_conf_full.SectionDict(step.strip())
            except:
                darelogger.info("step description section not found for step %s"%step)  
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

        darelogger.info("Done preparing compute Units ")

    def prepare_cu_arguments(self, input_name, cu_conf):                    
        
        arguements = ''            
        
        if cu_conf.get('arguments', '').strip() != '':
           return [input_name]
        # check for mutiple args in different types
        else:
           pass
        return [input_name] 
      

    def prepare_data_units(self):                

        darelogger.info("Starting to prepare Data Units ")

        for step in self.dare_conf_main['steps'].split(','):
            darelogger.info("Preparing Data Units: %s"%step)

            try:
                step_info_from_main_cfg = self.dare_conf_full.SectionDict(step.strip())
            except:
                darelogger.info("step description section not found for step %s"%step)  
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

    def __repr__(self):
       return  self.dare_id 
