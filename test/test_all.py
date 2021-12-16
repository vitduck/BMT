#!/usr/bin/env python3 

import subprocess 

from utils import syscmd
from env   import module_load, module_unload

bmt = [ 
        { 
            'env' : [ ],  
            'cmd' : './test_stream_omp.py' }, 
        { 
            'env' : [ 'intel/18.0.2' ], 
            'cmd' : './test_stream_omp.py' }, 
        { 
            'env' : [ 'cuda/10.1' ], 
            'cmd' : './test_stream_cuda.py' }, 
        { 
            'env' : [ ], 
            'cmd' : './test_iozone.py' }, 
        { 
            'env' : [ 'gcc/8.3.0', 'mpi/openmpi-3.1.5' ],  
            'cmd' : './test_ior.py' }, 
        { 
            'env' : [ 'nvidia_hpc_sdk/21.5' ],  
            'cmd' : './test_qe.py' }, 
        { 
            'env' : [ 'gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-3.1.5_hwloc', 'singularity/3.6.4' ], 
            'cmd' : './test_qe_ngc.py' }, 
        { 
            'env' : [ 'gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-3.1.5_hwloc' ], 
            'cmd' : './test_gromacs.py' }, 
        { 
            'env' : [ ], 
            'cmd' : './test_gromacs_ngc.py' }, 
        { 
            'env' : [ ], 
            'cmd' : './test_gromacs_ngc.py --gpudirect' }, 
        { 
            'env' : [ 'gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-4.0.5', 'singularity/3.6.4'], 
            'cmd' : './test_hpl.py' }, 
        { 
            'env' : [ 'gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-4.0.5', 'singularity/3.6.4'], 
            'cmd' : './test_hpl_ai.py' }, 
        { 
            'env' : [ 'gcc/8.3.0', 'cuda/10.1', 'cudampi/openmpi-4.0.5', 'singularity/3.6.4'], 
            'cmd' : './test_hpcg.py' }, 
    ]

for test in bmt:
    # load requires module 
    module_load(test['env'])
    
    print(syscmd(test['cmd']))

    # unload required modules
    module_unload(test['env'])
