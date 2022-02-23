#!/usr/bin/env python3 

from hpl     import Hpl
from openmpi import OpenMPI

hpl = Hpl(
    prefix = '../run/HPL',
    sif    = '../image/hpc-benchmarks:21.4-hpl.sif', 
    mpi    = OpenMPI(), 
    count  = 3 )

hpl.info()
hpl.run() 
hpl.summary() 
