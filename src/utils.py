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
    logging.debug(cmd.lstrip())

    pipe = subprocess.run(cmd, shell=True, text=True, capture_output=True)

    # Work around required for QE/6.8
    # https://forums.developer.nvidia.com/t/unusual-behavior/136392/2
    if pipe.returncode == 0 or pipe.returncode == 2:
        # debug message: --report-bindings (stderr) 
        for line in pipe.stderr.splitlines():
            if re.search('^\[.+?\]', line): 
                logging.info(line)

        # redirect to file 
        if output:
            with open(output, "w") as output_fh:
                for line in pipe.stdout.splitlines():
                    # debug message: SHARP_COLL_LOG_LEVEL=3 (stdout)
                    if re.search('^\[.+?\]', line): 
                        logging.info(line)
                    else: 
                        output_fh.write(f'{line}\n')
        else: 
            return pipe.stdout
    else: 
        logging.error(pipe.stderr)
        sys.exit()
