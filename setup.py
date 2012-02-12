#!/usr/bin/env python

from distutils.core import setup
from dare import version

setup(name='DARE',
      version=version,
      description='Dynamic Application Runtime Environment',
      author='Sharath Maddineni',
      author_email='smaddineni@cct.lsu.edu',
      maintainer: "Sharath Maddineni",
      maintainer_email: "smaddineni@cct.lsu.edu",
      url='http://dare.cct.lsu.edu/',
      license: "MIT",
      packages=['dare'],
      data_files=['dare.conf'],
      install_requires=['bigjob'],
     )
