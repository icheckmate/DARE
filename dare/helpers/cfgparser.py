#!/usr/bin/env python
__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"

import ConfigParser
import optparse
import os
import sys

class CfgParser(object):

    def __init__(self,conf_file=''):
        
        if conf_file== '' or not os.path.exists(conf_file):
           conf_file = "/default/conf/file/"

        #parse job conf file
        self.config = ConfigParser.ConfigParser()
        self.config.read(conf_file)

    def SectionDict(self, section):

        lst = self.config.items(section)
        dct={}
        for i in range(len(lst)):
            dct[lst[i][0]]=lst[i][1]
        return dct

class CfgWriter(object):
    def __init__(self):
        self.dare_config = ConfigParser.ConfigParser()
        self.resources_used = []
        self.wus = []
        self.step_names = []
        self.num_step_wus = {}
        self.step_types = {}

    def add_section(self,section_params):
        section_name = section_params["name"]
        self.dare_config.add_section(section_name)

        if section_name.startswith("resource_"):
            self.resources_used.append(section_name)
        
        if section_name.startswith("wu_"):
            self.wus.append(section_params)

        for i in section_params:
            self.dare_config.set(section_name, i , section_params[i] )

    def write(self, conffile, jobid, steps_order):
        
        self.prep_conf()
     
       
        DARE_JOB_DIR = os.path.join(os.getenv("HOME"), "dare", "jobs",str(jobid))

        ###################################################################################################
        ##########    finally      define DAREJOB  for dare.py   ##########################################
        ###################################################################################################

        section_param = {}
        section_param["name"] = 'DAREJOB'

        section_param["jobid"]=jobid
        section_param["webupdate"]="false"

        
        section_param["num_resources"]=len(self.resources_used)
        section_param["num_steps"]=len(steps_order)
        section_param["log_filename"]=os.path.join(DARE_JOB_DIR, str(jobid) + "-darelog.txt")
        section_param["num_wus"]= len(self.wus)

        print "[INFO] STEPS ORDER ",steps_order

        #change it to dare_config.append()
        wus_count_2 = 0
        ft_step_string = ""
        steps_order_string = ""
        
        for step in steps_order:
            if (steps_order_string != ""):
                steps_order_string = steps_order_string +',' + step
            else:
                 steps_order_string = step
            
            step_wus_string = ""            
            for x in range (0, int(self.num_step_wus[step])):
                if (step_wus_string != ""):
                    step_wus_string = step_wus_string + "," + "wu_" + str(wus_count_2)
                else:
                    step_wus_string = "wu_" + str(wus_count_2)
                wus_count_2 =  wus_count_2 + 1

            section_param[step] = step_wus_string

            ## making  ft_string to communicate it to dare
        
            if (self.step_types[step] == "data"):
                 if (ft_step_string != ""):
                     ft_step_string = ft_step_string +"," +str(step) 
                 else:
                     ft_step_string = str(step) 
    
        section_param["steps_order"] = steps_order_string
        section_param["ft_steps"]=ft_step_string
        self.add_section(section_param)


        ###############  write the config file for dare.py        #########################################
        try:
            dare_conffile =  conffile
            dare_cfgfile = open(dare_conffile,'w')
            self.dare_config.write(dare_cfgfile)
            dare_cfgfile.close()
        except:
            print "Could not write DARE config file"
            sys.exit(0);


    def prep_conf(self):
        
        for wu in self.wus:
            if wu["step_name"] not in self.step_names:
                self.step_names.append(wu["step_name"])
                self.num_step_wus[wu["step_name"]] = 1                
                self.step_types[wu["step_name"]]  = wu["type"]
                
            else:   
                self.num_step_wus[wu["step_name"]] = self.num_step_wus[wu["step_name"]] + 1 
        


        print "[INFO] num_step_wus", self.num_step_wus
        print "[INFO] step_names", self.step_names
        print "[INFO] step_types", self.step_types
