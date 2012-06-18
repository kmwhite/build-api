#!/usr/bin/env python

# DocString
'''
build-api wrapper

Usage:
    build-api [options]

    Options:
        --help          show this help message and exit
        --version       show version and exit
        --logs-level LL specify the LL to log at        [default: debug]
        --redis-host RH specify the RH to connect to    [default: localhost]
        --redis-port RP specify the RP to connect to    [default: 6379]
        --redis-db DB   specify the DB to connect to    [default: 0]

'''

# Imports from the FUTURE
from __future__ import print_function

# STL Imports
import json
import logging
import os
import sys

# Third-Party Imports
import docopt
import envoy
import pyres

# Versioning
VERSION='1.0.0'


class BuildWorker(object):
    '''
    '''

    # The 'queue' class variable is used by ResQ to determine where to look
    # for work to do
    queue = 'builds'

    @staticmethod
    def preform(build_path):
        '''
          The preform method is the workhorse of the async worker. It does the
          actual execution of the make script
        '''

        try:
            os.chdir('/data/builds/{0}'.format(project))
            return envoy.run('make install').std_out
        except OSError, err:
            return "Failure to change to build directory!\n"
