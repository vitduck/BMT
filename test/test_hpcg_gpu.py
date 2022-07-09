#!/usr/bin/env python3 

from hpcg_gpu import HpcgGpu
from openmpi  import OpenMPI

hpcg = HpcgGpu(
    prefix = '../run/HPCG',
    sif    = '../image/hpc-benchmarks:21.4-hpcg.sif', 
    mpi    = OpenMPI( 
        omp  = 4 ))

hpcg.getopt()
hpcg.info()
hpcg.run() 
hpcg.summary()
