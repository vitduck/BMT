#!/usr/bin/env python3 

import os
import logging
import subprocess

def module_list():
    logging.info(f'{"Modules":<7} : {" ".join(os.environ["LOADEDMODULES"].split(os.pathsep))}')

def module_purge():
    cmd = subprocess.run(['modulecmd', 'python', 'purge'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    exec(cmd)

def module_unload(module=[]):
    cmd = subprocess.run(['modulecmd', 'python', 'unload'] + module, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode('utf-8')
    exec(cmd)
    
def module_load(module=[]):
    cmd = subprocess.run(['modulecmd', 'python', 'load'] + module, stdout=subprocess.PIPE).stdout.decode('utf-8')
    exec(cmd)

def get_module(): 
    return os.environ["LOADEDMODULES"].split(os.pathsep)
