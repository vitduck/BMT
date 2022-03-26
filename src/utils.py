#!/usr/bin/env python3 

import os
import re
import sys
import logging
import subprocess
import collections 

# emulate perl vivificaiton
def autovivification(): 
    return collections.defaultdict(autovivification)

# clear cache on client (root required)
def sync(nodelist=[]): 
    if os.getuid() == 0:
        for node in nodelist: 
            syscmd('sync; echo 1 > /proc/sys/vm/drop_caches')
    else:
        logging.warning(f'{"Warning":7} : Cannot flush cache without root privileges!')

# wrapper for system commands 
def syscmd(cmd, output=None):
    logging.debug(cmd)

    pout = '' 

    try: 
        pout = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode('utf-8').rstrip()
    except subprocess.CalledProcessError as e:
        # Work around required for QE/6.8
        # https://forums.developer.nvidia.com/t/unusual-behavior/136392/2
        if e.returncode == 2:
            if output:
                with open(output, "w") as output_fh:
                    output_fh.write(f'{e.stdout.decode("utf-8").rstrip()}')
        else:
            logging.error(f'{e.stderr.decode("utf-8").rstrip()}')
            sys.exit()
    else: 
        if output: 
            with open(output, "w") as output_fh:
                output_fh.write(pout)
        else: 
            return pout
