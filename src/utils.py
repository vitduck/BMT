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

    # redirect output to file
    if output:
        # generic debug message: --report-bindings (to stderr) 
        for line in pipe.stderr.splitlines():
            if re.search('^\[.+?\]', line): 
                logging.info(line)

        with open(output, "w") as output_fh:
            for line in pipe.stdout.splitlines():
                #  debug message: SHARP_COLL_LOG_LEVEL=3 (to stdout)
                if re.search('^\[.+?\]', line): 
                    logging.info(line)
                else: 
                    output_fh.write(f'{line}\n')
        
        # GROMACS: tunepme fails -> exit code 1 (fatal) 
        # QE 6.8: STOP message   -> exit code 2 (non fatal)
        # QE 7.0: No issues
        if pipe.returncode == 0 or pipe.returncode == 2:
            return 0

        logging.error(pipe.stderr)
    else: 
        if pipe.returncode != 0: 
            logging.error(pipe.stderr)
            sys.exit()
        else: 
            return pipe.stdout
