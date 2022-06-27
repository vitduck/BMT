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
        logging.warning('Cannot flush cache without root privileges!')

# wrapper for system commands 
def syscmd(cmd, output=None):
    pipe = subprocess.run(fmt_cmd(cmd), shell=True, text=True, capture_output=True)

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

def fmt_cmd(cmds): 
    level = 0 
    final = [] 

    for i in cmds:
        # compound cmd 
        if type(i) == str:
            final.append(i)

            logging.debug(f'<> {i}')
        # cmd with options
        else: 
            # 1 level deep 
            if type(i[0]) == str: 
                for j in i: 
                    if level == 0:
                        level = level + 1 
                        
                        logging.debug(f'<> {j}')
                    else: 
                        logging.debug(f'{"":<{4*level}} {j}')

                final.append(" ".join(i))
            # 2 level deep
            else: 
                flatten = [] 
                
                for j in i:  
                    for k in j: 
                        flatten.append(k) 

                        if level == 0:  
                            level = level + 1 
                        
                            logging.debug(f'<> {k}')
                        else: 
                            logging.debug(f'{"":<{4*level}} {k}')
                            
                            if k == j[0]: 
                                level = level + 1 

                final.append(" ".join(flatten))
    
    return ';'.join(final)
