#!/usr/bin/env python

# DocString
'''
build-api wrapper

Usage:
    build-api [options]

    Options:
        --help          show this help message and exit
        --version       show version and exit
        --debug         enable debug mode
        --logs-level LL specify the LL to log at        [default: debug]
        --flask-host FH specify the FH to listen on     [default: localhost]
        --flask-port FP specify the FP to listen on     [default: 5000]
        --redis-host RH specify the RH to connect to    [default: localhost]
        --redis-port RP specify the RP to connect to    [default: 6379]

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
import flask
import pyres

# Local Imports
import worker

# Versioning
VERSION='1.0.0'

# Configure the application
app = flask.Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return "Hello, World!\n"

@app.route('/build/<string:project>', methods=['POST'])
def build(project = ''):
    assert flask.request.method == 'POST'
    try:
        # Fetch the payload out of params provided by the HTTP POST
        payload = flask.request.form['payload']
        # Bind to localhost by default if one isn't provided
        redis_host = os.environ.get('REDIS_HOST', '127.0.0.1')
        # Bind on the default redis port if one isn't provided
        redis_port = os.environ.get('REDIS_PORT', '6379')
        resq = pyres.ResQ(server="{0}:{1}".format(redis_host, redis_port))
        resq.enqueue(worker.BuildWorker, project)
        return 'Build generated for {0}.\nPayload:\n{1}\n\n'.format(project,
                                                                    payload)
    except KeyError, err:
        print('Payload wasn\'t in the POST Params\n', file=sys.stderr)
        return "No payload provided\n"

@app.route('/builds', methods=['GET'])
def builds():
    assert flask.request.method == 'GET'

if __name__ == "__main__":
    # Parse the arguments
    arguments = docopt.docopt(__doc__, version=VERSION)

    # Enable debug mode if specified
    if arguments['--debug']:
        app.debug = True

    # Launch the webservice
    app.run(host=arguments['--flask-host'],
            port=int(arguments['--flask-port']))
