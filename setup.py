#!/usr/bin/env python

from setuptools import setup
import os
fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'VERSION')
version = open(fn).read().strip()
    
setup(name='DARE',
        version=version,
        description='Dynamic Application Runtime Environment',
        author='Sharath Maddineni',
        author_email='smaddineni@cct.lsu.edu',
        maintainer= "Sharath Maddineni",
        maintainer_email= "smaddineni@cct.lsu.edu",
        url='http=//dare.cct.lsu.edu/',
        license= "MIT",
        packages=['bin','daresrc', 'daresrc.runtime', 'daresrc.daredb', 'daresrc.utils'],
        data_files=['dare.conf', 'VERSION'],
        package_data = {
            # If any package contains *.txt files, include them:
            '': ['*.cfg'],
            '': ['*.cu'],
            # And include any *.dat files found in the 'data' subdirectory
            # of the 'mypkg' package, also:
            #'daresrc': ['data/*.cfg'],
        },

        install_requires=['bigjob'],

        entry_points = {
            'console_scripts': ['dare-run = bin.darerun:main',]}

     )
