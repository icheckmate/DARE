#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"


# file stager for grids and clouds
#TODO: should be SAGA based/pilot store

from subprocess import Popen
import time

class Data(object):
    def __init__(self):
        self.transfers_repo = []

    def submit_filetransfer(self,ft):

        source_url=ft["source_url"]
        dest_url=ft["dest_url"]

        print "[DAREINFO] Tranferring the file %s to %s"%(source_url, dest_url)
        print ft["ft_type"]

        #fgeuca for clouds
        if (ft["ft_type"] == "fgeuca"):
             cmd = "scp  -r -i /path/to/smaddi2.private %s %s"%(source_url, dest_url)

        elif (ft["ft_type"] =="gridftp"):
             cmd = "globus-url-copy  -cd  %s %s"%(source_url, dest_url)

        elif (ft["ft_type"] == "scp"):
             cmd = "scp -r %s %s"%(source_url, dest_url)

        try:
             print "[DAREINFO] command",(cmd)
             self.transfers_repo.append(Popen(cmd, shell=True))
        except:
             error_msg = "File stage in failed : from "+ source_url + " to "+ dest_url


    def wait_for_transfers(self):
        while self.transfers_repo:
            for p in self.transfers_repo:
                print 'file transfer process ID: %s,\nState: %s ' % (p.pid, p.poll())

                if p.poll() < 1:
                    print 'Transfering is done, removing from list'
                    self.transfers_repo.remove(p)

            print 'Application going to sleep'
            time.sleep(5)
