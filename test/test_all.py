#!/usr/bin/env python3 

import subprocess 

from utils import syscmd, list, load, unload

bmt = {
    'stream_omp'  : ['gcc/8.3.0'], 
    'stream_cuda' : ['cuda/10.1'], 
    'iozone'      : [], 
    'ior'         : ['gcc/8.3.0', 'mpi/openmpi-3.1.5'], 
    'qe'          : ['nvidia_hpc_sdk/21.5'],
    'qe_ngc'      : ['pgi/19.1' , 'cuda/10.0', 'cudampi/openmpi-3.1.5_hwloc', 'singularity/3.6.4'],
    'gromacs'     : ['gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-3.1.5_hwloc'],
    'gromacs_ngc' : ['gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-3.1.5_hwloc', 'singularity/3.6.4'],
    'hpl'         : ['gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-test_2', 'singularity/3.6.4'], 
    'hpl_ai'      : ['gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-test_2', 'singularity/3.6.4'], 
    'hpcg'        : ['gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-test_2', 'singularity/3.6.4']}


for code in bmt:
    print(f'> {code}: ', end='')

    # load requires module 
    load(bmt[code])
    
    # run test
    result = syscmd(f'./test_{code}.py')
    if result: 
        print('PASSED')
        print(result) 
    else: 
        print('FAILED')

    # unload required modules
    unload(bmt[code])

    print() 
