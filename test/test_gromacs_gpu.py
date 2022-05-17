#!/usr/bin/env python3

from gromacs_gpu import GromacsGpu
from openmpi import OpenMPI 

gmx = GromacsGpu(
    prefix    = '../run/GROMACS', 
    input     = '../input/GROMACS/stmv.tpr',
    tunepme   = True,
    nstlist   = 200,
    nsteps    = 10000, 
    mpi       = OpenMPI(
        task    = 32, 
        omp     = 1, 
        bind    = 'core', 
        map     = 'numa', 
        verbose = True ))

gmx.getopt()
gmx.info()
gmx.download() 
gmx.build()
gmx.run()
gmx.summary()
