#!/usr/bin/env python3 

import subprocess 

from utils import syscmd
from env   import module_load, module_unload

bmt = {
    'stream_omp/gcc' : [], 
    'stream_omp/icc' : ['intel/18.0.2'],
    'stream_cuda'    : ['cuda/10.1'], 
    'iozone'         : [], 
    'ior'            : ['gcc/8.3.0', 'mpi/openmpi-3.1.5'], 
    'qe'             : ['nvidia_hpc_sdk/21.5'],
    'qe_ngc'         : ['pgi/19.1' , 'mpi/openmpi-3.1.5' , 'singularity/3.6.4'],
    'gromacs'        : ['gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-3.1.5_hwloc'],
    'gromacs_ngc'    : ['gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-3.1.5_hwloc', 'singularity/3.6.4'],
    'hpl'            : ['gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-test_2', 'singularity/3.6.4'], 
    'hpl_ai'         : ['gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-test_2', 'singularity/3.6.4'], 
    'hpcg'           : ['gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-test_2', 'singularity/3.6.4'] }

for case in bmt:
    # load requires module 
    module_load(bmt[case])
    
    # run test
    code   = case.split('/')[0]
    result = syscmd(f'./test_{code}.py')

    print(f'[{case.upper()}]')
    print(result)

    # unload required modules
    module_unload(bmt[case])

    print() 
