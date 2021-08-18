#!/usr/bin/env python3 

import os
import re
import sys
import logging
import subprocess
import collections

# SLURM_NODELIST
def init_nodelist(): 
    flat = [] 
    name, index = re.search('([a-zA-Z]+)\[?([\d\-]+)\]?', os.environ['SLURM_NODELIST']).group(1,2)

    for node in index.split(','):
        if re.search('-', node):
            node_start, node_end = node.split('-')
                
            flat.extend(range(int(node_start), int(node_end)+1))
        else:
            flat.append(node)

    return [ name+str(item) for item in flat ]

# SLURM_NTASKS_PER_NODE
def init_ntasks(): 
    return int(os.environ['SLURM_NTASKS_PER_NODE'])

# CUDA_VISIBLE_DEVICES due to bugs in slurm 18.
def init_gpu(host):
    nvidia_smi = syscmd(f'ssh {host} "nvidia-smi -L"')

    gpu = re.findall('GPU\s+(\d+)', nvidia_smi)

    return [i for i in gpu]

# hash autovivification
def init_result(): 
    nested_dict = lambda: collections.defaultdict(nested_dict) 

    return nested_dict()

# clear cache on client (root required)
def sync(host=[]): 
    if os.getuid() == 0:
        for hostname in host: 
            syscmd(f'ssh {hostname} "sync; echo 1 > /proc/sys/vm/drop_caches"')
    else:
        logging.warning('Note: Cannot flush cache without root privileges!')

# parse for gpu memory (HPL)
def init_gpu_memory(host): 
    memory = syscmd(f'ssh {host} "nvidia-smi -i 0 --query-gpu=memory.total --format=csv,noheader"').split()[0]

    return int(memory)

# parse for gpu affinity (HPL/HPCG)
def init_gpu_affinity(host):
    affinity = [] 
    topology = syscmd(f'ssh {host} "nvidia-smi topo -m"')

    for line in topology.splitlines():
        if re.search('^GPU\d+', line): 
            affinity.append(line.split()[-1])

    return affinity

# from CUDA SDK 
def device_query(host): 
    homedir = os.environ['HOME']

    syscmd(f'wget https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Samples/deviceQuery/deviceQuery.cpp -O {homedir}/deviceQuery.cpp')
    syscmd(f'wget https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Common/helper_cuda.h -O {homedir}/helper_cuda.h')
    syscmd(f'wget https://raw.githubusercontent.com/NVIDIA/cuda-samples/master/Common/helper_string.h -O {homedir}/helper_string.h')
    syscmd(f'builtin cd; nvcc -I. deviceQuery.cpp -o deviceQuery')

    query = syscmd(f'ssh {host} ./deviceQuery')

    for line in query.splitlines():
        if re.search('\/ Runtime Version', line): 
            runtime = line.split()[-1]

        if re.search('Minor version number', line): 
            cuda_cc = line.split()[-1].replace('.', '')
            break

    # clean up 
    [os.remove(f'{homedir}/{file}') for file in ['deviceQuery.cpp', 'helper_cuda.h', 'helper_string.h', 'deviceQuery']]

    return runtime, cuda_cc

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
