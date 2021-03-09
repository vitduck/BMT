#!/usr/bin/env python 

import os
import json
import subprocess

def list():
    print(os.environ['LOADEDMODULES'].split(os.pathsep))

def purge():
    cmd = subprocess.run(['modulecmd', 'python', 'purge'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    exec(cmd)

def load(module=[]): 
    cmd = subprocess.run(['modulecmd', 'python', 'load'] + module, stdout=subprocess.PIPE).stdout.decode('utf-8')
    exec(cmd)

def env(program):
    module = []

    with open('/home01/optpar01/repo/bmt/env.json') as config:
        env = json.load(config)

    purge()
    load(env[program])
