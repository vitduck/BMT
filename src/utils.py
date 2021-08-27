#!/usr/bin/env python3 

import os
import re
import sys
import logging
import subprocess

# clear cache on client (root required)
def sync(host=[]): 
    if os.getuid() == 0:
        for hostname in host: 
            syscmd(f'ssh {hostname} "sync; echo 1 > /proc/sys/vm/drop_caches"')
    else:
        logging.warning('Cannot flush cache without root privileges!')

# wrapper for system commands 
def syscmd(cmd, output=None):
    logging.debug(cmd)

    try: 
        pout = subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True).decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        logging.error(f'{e.stderr.decode("utf-8").strip()}')
        sys.exit()
    else: 
        if output: 
            with open(output, "w") as output_fh:
                output_fh.write(pout)
        else: 
            return pout

# modulecmd wrapper
def module_list():
    print('# Environment: '+' '.join(os.environ['LOADEDMODULES'].split(os.pathsep)))

def module_purge():
    cmd = subprocess.run(['modulecmd', 'python', 'purge'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    exec(cmd)

def module_unload(module=[]):
    cmd = subprocess.run(['modulecmd', 'python', 'unload'] + module, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode('utf-8')
    exec(cmd)
    
def module_load(module=[]):
    cmd = subprocess.run(['modulecmd', 'python', 'load'] + module, stdout=subprocess.PIPE).stdout.decode('utf-8')
    exec(cmd)
