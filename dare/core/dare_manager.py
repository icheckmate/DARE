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

from dare.helpers.stepunit import StepUnit, StepUnitStates
from dare.helpers.cfgparser import CfgParser

from dare.helpers.prepareworkflow import PrepareWorkFlow

from dare.helpers.updater import Updater
from dare import COORDINATION_URL

class DareManager(object):
    """DARE manager:
       - reads different configuration files
       - submits compute/data units as that in various steps"""
   
    """Constructor"""
    def __init__(self, conffile="/path/to/conf/file"):
        "" ""
        self.dare_conffile = conffile
        self.workflow = PrepareWorkFlow(self.dare_conffile)
        self.updater = Updater(self.workflow.update_site_db, self.workflow.dare_web_id)
        self.dare_id = "dare-" + str(uuid.uuid1())
        self.compute_pilot_service_repo=[]
        self.data_pilot_service_repo = [] 

        self.start()

    def start(self):         
       # try:
            from pilot import PilotComputeService, PilotDataService, ComputeDataService, State

            darelogger.info("Create Compute Engine service ")

            self.pilot_compute_service = PilotComputeService(coordination_url=COORDINATION_URL)
            self.pilot_data_service = PilotDataService()

            for compute_pilot, desc in self.workflow.compute_pilot_repo.items():
                self.compute_pilot_service_repo.append(self.pilot_compute_service.create_pilot(pilot_compute_description=desc))

            #for data_pilot, desc in self.workflow.data_pilot_repo.items():            
             #   self.data_pilot_service_repo.append(self.pilot_data_service.create_pilot(pilot_data_description=desc))
    
            self.compute_data_service = ComputeDataService()
            self.compute_data_service.add_pilot_compute_service(self.pilot_compute_service)
           # self.compute_data_service.add_pilot_data_service(self.pilot_data_service) 

            self.step_thread= {}

            ### run the steps
            self.step_start_lock=threading.RLock()
            self.step_run_lock=threading.RLock()

            for step_id in self.workflow.step_units_repo.keys():
                    darelogger.info(" Sumitted step %s "%step_id)
                    self.step_start_lock.acquire()
                    self.start_thread_step_id =step_id
                    self.step_start_lock.release()

                    self.step_thread[step_id] = threading.Thread(target=self.start_step)
                    self.step_thread[step_id].start()
                    
            while(1):     
                count_step = [v.is_alive() for k,v in self.step_thread.items()]
                darelogger.info('count_step %s'%count_step)
                if not True in count_step and len(count_step)>0:                      
                    break
                time.sleep(10)
                       

            darelogger.info(" All Steps Done processing")

            self.cancel()
        #except:
         #   self.cancel()


    def check_to_start_step(self, step_id):
        flags = []
        darelogger.info(self.workflow.step_units_repo[step_id].UnitInfo['start_after_steps'])
        if self.workflow.step_units_repo[step_id].get_status() == StepUnitStates.New:  
           for dep_step_id in self.workflow.step_units_repo[step_id].UnitInfo['start_after_steps']:
               if self.workflow.step_units_repo[dep_step_id].get_status() != StepUnitStates.Done:
                  flags.append(False)
               darelogger.info(self.workflow.step_units_repo[dep_step_id].get_status())
        return False if False in flags else True


    def start_step(self):
        self.step_start_lock.acquire()
        step_id = self.start_thread_step_id
        self.step_start_lock.release()

        while(1):
            darelogger.info(" Checking to start step %s "%step_id)
            if self.check_to_start_step(step_id):
                self.run_step(step_id)
                break
            else:
                darelogger.info(" Cannot start this step %s sleeping..."%step_id)
                time.sleep(10)
    
    def run_step(self, step_id):
        #self.step_run_lock.acquire()
        starttime = time.time()

        #job started update status
        this_su = self.workflow.step_units_repo[step_id].UnitInfo
        self.updater.update_status( this_su['dare_web_id'], "%s in step %s"%('Running',  this_su['name']))
    
        p = []
        darelogger.info(" Started running %s "%step_id)
        for du_id in self.workflow.step_units_repo[step_id].UnitInfo['transfer_input_data_units']:
                #data_unit = self.compute_data_service.submit_data_unit(self.workflow.data_units_repo[du_id])
                #darelogger.debug("Pilot Data URL: %s Description: \n%s"%(data_unit, str(self.workflow.data_units_repo[du_id])))
                #data_unit.wait()
        #        self.compute_data_service.wait()
            darelogger.debug(" input tranfer for step %s complete"%step_id)
         
        jobs = []
        job_start_times = {}
        job_states = {}
        NUMBER_JOBS = len(self.workflow.step_units_repo[step_id].UnitInfo['compute_units'])
        for cu_id in self.workflow.step_units_repo[step_id].UnitInfo['compute_units']:                    
                compute_unit = self.compute_data_service.submit_compute_unit(self.workflow.compute_units_repo[cu_id])
                darelogger.info("Compute Unit: Description: \n%s"%(str(self.workflow.compute_units_repo[cu_id])))
                jobs.append(compute_unit)
                job_start_times[compute_unit]=time.time()
                job_states[compute_unit] = compute_unit.get_state()
        

        darelogger.debug("************************ All Jobs submitted ************************")

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
                    darelogger.debug( "Job " + str(jobs[i]) + " changed from: " + old_state + " to " + state)
                if old_state != state and self.has_finished(state)==True:
                    darelogger.info( "%s step Job: "%(self.workflow.step_units_repo[step_id].UnitInfo['name']) + str(jobs[i]) + " Runtime: " + str(time.time()-job_start_times[jobs[i]]) + " s.")
                if self.has_finished(state)==True:
                    finish_counter = finish_counter + 1
                job_states[jobs[i]]=state
                
            darelogger.debug( "Current states: " + str(result_map) )
            time.sleep(5)
            if finish_counter == NUMBER_JOBS:
                break

        #self.compute_data_service.wait() 
        darelogger.debug(" Compute jobs for step %s complete"%step_id)

        
        #for du_id in self.workflow.step_units_repo[step_id].UnitInfo['transfer_output_data_units']:
        #        data_unit = self.compute_data_service.submit_data_unit(self.workflow.data_units_repo[du_id])
        #        darelogger.debug("Pilot Data URL: %s Description: \n%s"%(data_unit, str(pilot_data_description)))
        #        data_unit.wait()
        #darelogger.debug(" Output tranfer for step %s complete"%step_id)

        #        self.compute_data_service.wait()

        #runtime = time.time()-starttime

        #all jobs done update status
         
        self.updater.update_status( this_su['dare_web_id'],"%s is Done" %this_su['name'] )

        #self.step_run_lock.release()


    def has_finished(self, state):
        state = state.lower()
        if state=="done" or state=="failed" or state=="canceled":
            return True
        else:
            return False


    def check_to_start_step(self, step_id):
        flags = []
        print self.workflow.step_units_repo[step_id].UnitInfo['start_after_steps']
        if self.workflow.step_units_repo[step_id].get_status() == StepUnitStates.New:  
           for dep_step_id in self.workflow.step_units_repo[step_id].UnitInfo['start_after_steps']:
               if self.workflow.step_units_repo[dep_step_id].get_status() != StepUnitStates.Done:
                  flags.append(False)
               print self.workflow.step_units_repo[dep_step_id].get_status()
        return False if False in flags else True


    def cancel(self):
        darelogger.debug("Terminate Pilot Compute/Data Service")
        self.compute_data_service.cancel()
        try: 
            self.pilot_data_service.cancel()         
            self.pilot_compute_service.cancel()
        except:
            pass