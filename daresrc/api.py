#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"


class DareManager(object):
    
    def __init__(self):
        pass
    
    def add_wu(self):
        pass
        
    def add_du(self):
        pass
        
    def add_resource(self):
        pass
    
    def add_step(self):
        pass

    def start(self):
        pass


class DareUnit(object):
     
    #used to define multiple units here 
    def __init__(self):          
        self.name = "data"
     
    def define_param(self):
        pass
         
    def get_status(self):
        pass
     
    def get_param(self):
        pass
        
        
class WorkUnitStates(object):
    Unknown = 0
    New = 1
    Running = 2
    Done = 3
    Canceled = 4
    Failed = 5

class ReosourceStates(object):
    Unknown = 0
    New = 1
    Running = 2
    Done = 3
    Canceled = 4
    Failed = 5
    Queue = 6

class StepStates(object):
    Unknown = 0
    New = 1
    Running = 2
    Done = 3
    Canceled = 4
    Failed = 5
    Queue = 6
    
class DataUnitStates(object):
    Unknown = 0
    New = 1
    Running = 2
    Done = 3
    Canceled = 4
    Failed = 5

class Data(object):
    # transferring required data
    def SubmitFiletransfer(ft_descs):
        pass


class Updater(object):
    #To update jobs status to the database for WEB use if necessary
    pass
