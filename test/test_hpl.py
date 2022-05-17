#!/usr/bin/env python3 

from hpl_gpu import HplGpu
from openmpi import OpenMPI

hpl = HplGpu(
    prefix    = '../run/HPL',
    sif       = '../image/hpc-benchmarks:21.4-hpl.sif',
    blocksize = [288], 
    memory    = ['90%'],
    mpi       = OpenMPI( 
        bind  = 'none',
        omp   = 4 )) 

hpl.getopt()
hpl.info()
hpl.run() 
hpl.summary() 
