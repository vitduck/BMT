#!/usr/bin/env python3 

import re
import logging
import os
import sys

from utils import syscmd

def lscpu(host): 
    cpu   = {} 
    numa  = []
    lscpu = syscmd(f'ssh {host} lscpu')

    for line in lscpu.splitlines(): 
        if re.search('^CPU\(s\)', line): 
            cpu['CPUs'] = line.split()[-1]
        if re.search('Model name', line): 
            cpu['Model'] = ' '.join(line.split()[2:])
        if re.search('Thread\(s\)', line): 
            cpu['Threads'] = line.split()[-1]
        if re.search('^NUMA node\d+', line): 
            numa.append(line.split()[-1])
        if re.search('Flags', line): 
            avx = re.findall('(avx\w+)\s+', line)
            cpu['AVXs'] = ', '.join([flag.upper() for flag in avx])

        cpu['NUMA'] = numa

    return cpu

def cpu_info(cpu): 
    logging.basicConfig( 
        stream  = sys.stderr,
        level   = os.environ.get('LOGLEVEL', 'INFO').upper(), 
        format  = '# %(message)s')

    logging.info(f'{"CPU":<7} : {cpu["Model"]}')
    logging.info(f'{"Cores":<7} : {cpu["CPUs"]}')
    logging.info(f'{"Threads":<7} : {cpu["Threads"]}')

    # NUMA domain
    for i in range(0, len(cpu['NUMA'])): 
        numa = f'NUMA {++i}'
        logging.info(f'{numa:<7} : {cpu["NUMA"][i]}')

    logging.info(f'{"AVXs":<7} : {cpu["AVXs"]}')
