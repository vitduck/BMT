#!/usr/bin/env python3 

import re
import logging
import os
import sys

from utils import syscmd

def lscpu(): 
    host  = {} 
    numa  = []
    lscpu = syscmd(['lscpu'])

    for line in lscpu.splitlines(): 
        if re.search('^CPU\(s\)', line): 
            host['CPUs'] = int(line.split()[-1]) 
        if re.search('Model name', line): 
            host['Model'] = ' '.join(line.split()[2:])
        if re.search('Thread\(s\)', line): 
            host['Threads'] = line.split()[-1]
        if re.search('^NUMA node\d+', line): 
            numa.append(line.split()[-1])
        if re.search('Flags', line): 
            avx = re.findall('(avx\w*)\s+', line)
            host['AVXs'] = ', '.join([flag.upper() for flag in avx])

        host['NUMA'] = numa

    return host

def cpu_info(host): 
    logging.basicConfig( 
        stream  = sys.stderr,
        level   = os.environ.get('LOGLEVEL', 'INFO').upper(), 
        format  = '# %(message)s')

    logging.info(f'{"CPU":<7} : {host["Model"]}')
    logging.info(f'{"Cores":<7} : {host["CPUs"]}')
    logging.info(f'{"Threads":<7} : {host["Threads"]}')

    # NUMA domain
    for i in range(0, len(host['NUMA'])): 
        numa = f'NUMA {++i}'
        logging.info(f'{numa:<7} : {host["NUMA"][i]}')

    logging.info(f'{"AVXs":<7} : {host["AVXs"]}')

def cpu_memory():
    mem_kb = syscmd(['grep MemTotal /proc/meminfo']).split()[1]*1

    return int(mem_kb)
