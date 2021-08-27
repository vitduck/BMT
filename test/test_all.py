#!/usr/bin/env python3 

import subprocess 

from utils import syscmd
from env   import module_load, module_unload

bmt = {
    'stream_omp'  : [], 
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

    # load requires module 
    module_load(bmt[code])
    
    # run test
    result = syscmd(f'./test_{code}.py')
    if result: 
        print(f'[{code.upper()}] DONE')
        print(result) 
    else: 
        print(f'[{codeupper} ERROR ]')

    # unload required modules
    module_unload(bmt[code])

    print() 
