#!/usr/bin/env python
# vi:tabstop=4:expandtab

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
    """
    /

    Main Index

    """
    TEMPLATE="""
<HTML>
<HEAD>
<TITLE>build-api: Index</TITLE>
<LINK REL="stylesheet" type="text/css" href="/style.css" />
</HEAD>
<BODY>
<H1>build-api: Index</H1>
<UL>
<LI>Supported Projects
<LI><A HREF=/builds>Show Builds</A>
</UL>
<P CLASS=footer>build-api v{{ version }}</P>
</BODY>
</HTML>
"""
    return flask.render_template_string(TEMPLATE, version=VERSION)

@app.route('/build/<string:project>', methods=['POST'])
def build(project = ''):
    assert flask.request.method == 'POST'

    # Fetch the payload out of params provided by the HTTP POST
    try:
        payload = flask.request.form['payload']
    except KeyError, err:
        print('Payload wasn\'t in the POST Params\n', file=sys.stderr)
        return "No payload provided\n"

    # Bind to localhost by default if one isn't provided
    redis_host = os.environ.get('REDIS_HOST', '127.0.0.1')
    # Bind on the default redis port if one isn't provided
    redis_port = os.environ.get('REDIS_PORT', '6379')
    # Build the redis server URL
    redis_uri = "{0}:{1}".format(redis_host, redis_port)
    resq = pyres.ResQ(server=redis_uri)

    resq.enqueue(worker.BuildWorker, project)
    return 'Build generated for {0}.\nPayload:\n{1}\n\n'.format(project,
                                                                payload)

@app.route('/builds', methods=['GET'])
def builds():
    """
    /builds

    list recent builds

    """
    TEMPLATE = """
<HTML>
<HEAD>
<TITLE>build-api: Build Logs</TITLE>
<LINK REL="stylesheet" type="text/css" href="/style.css" />
</HEAD>
<BODY>
<H1>build-api: Build Logs</H1>
<TABLE>
<TR><TH>Timestamp<TH>Project Name<TH>Triggered by<TH>Status<TH>Logs
{% for b in builds %}
<TR CLASS={%
    if b.build.return_status == 0
        %}success{%
    else
        %}failure{%
    endif %}>
<TD>{{ b.timestamp }}
<TD>{{ b.project }}
<TD>{{ b.build.triggered_repo }}:{{ b.build.triggered_ref }}
<TD>{%
    if b.build.return_status == 0
        %}Success{%
    else
        %}Failure{%
     endif %}
<TD><A HREF=/log/{{ b.timestamp }}/{{ b.project }}>view log</A>
</TR>
{% endfor %}
</TABLE>
<P CLASS=footer>build-api v{{ version }}</P>
</BODY>
</HTML>
"""
    assert flask.request.method == 'GET'
    out_builds = []
    # populate list of builds
    return flask.render_template_string( TEMPLATE,
                                            builds=out_builds,
                                            version=VERSION
                                        )

@app.route('/log/<string:timestamp>/<string:project>', methods=['GET'])
def log(timestamp = '',project = ''):
    """
    /log/<TIMESTAMP>/PROJECT_NAME>

    show detailed information about build

    """
    TEMPLATE = """
<HTML>
<HEAD>
<TITLE>build-api: {{ state.project }} build @ {{ state.timestamp }}</TITLE>
<LINK REL="stylesheet" type="text/css" href="/style.css" />
</HEAD>
<BODY>
<H1>{{ state.project }} build @ {{ state.timestamp }}</H1>
<H3>Triggered by {{ state.build.triggered_repo }}:{{ state.build.triggered_ref }}</H3>
<TABLE>
<TR><TD>Build Command<TD>{{ state.build.cmd }}
<TR><TD>Build Directory<TD>{{ state.build.cwd }}
{% if state.build.run_error %}
<TR CLASS=failure><TD COLSPAN=2>ERROR executing build command:
<TR CLASS=failure><TD COLSPAN=2>
<PRE>{{ state.build.run_error }}</PRE>
{% else %}
<TR CLASS={%
    if state.build.return_status == 0
        %}success{%
    else
        %}failure{%
    endif %}><TD>Return Status<TD>{{ state.build.return_status }}
</TABLE>
<P>Build Output:</P>
<PRE>{{ state.build.std_out }}</PRE>
{% endif %}
<P CLASS=footer>build-api v{{ version }}</P>
</BODY>
</HTML>
"""
    assert flask.request.method == 'GET'
    return flask.render_template_string(TEMPLATE,
                                            state={},
                                            version=VERSION
                                        )

@app.route("/style.css", methods=['GET'])
def style():
    """
    /style.css

    css style sheet

    """
    TEMPLATE = """
body {
    background-color:#444444;
    color: #F8F8F8;
    font-family: "Lucida Console", Lucida, monospace;
}
a:link{
    color: #AA99FF;
    text-decoration: none;
}
a:visited{
    color: #AA99FF;
    text-decoration: none;
}
a:hover{
    color: #EEDDFF;
    text-decoration: none;
}
a:active{
    color: #FFFFFF;
    text-decoration: none;
}
h1 {
    font-size: 2em;
    color:#999999;
}
h2 {
    font-size: 1.67em;
    color:#999999;
}
h3 {
    font-size: 1.33em;
    color:#999999;
}
h4 {
    font-size: 1.21em;
    color:#999999;
}
h5 {
    font-size: 1.11em;
    color:#999999;
}
h6 {
    font-size: 1.06em;
    color:#999999;
}
p.footer {
    font-size: .67em;
    color:#999999;
}
table {
    background-color:#666666;
    border-collapse:collapse;
}
td, th {
    padding: 3px;
}
table, th, td {
    border: 1px solid black;
}
tr.success {
    background-color:#008800;
}
tr.failure {
    background-color:#880000;
}
"""
    return flask.render_template_string(TEMPLATE)

if __name__ == "__main__":
    # Parse the arguments
    arguments = docopt.docopt(__doc__, version=VERSION)

    # Enable debug mode if specified
    if arguments['--debug']:
        app.debug = True

    # Launch the webservice
    app.run(host=arguments['--flask-host'],
            port=int(arguments['--flask-port']))
