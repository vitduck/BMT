#!/usr/bin/env python3

from gromacs_gpu import GromacsGpu
from tmpi        import tMPI 

gmx = GromacsGpu(
    prefix    = '../run/GROMACS', 
    input     = '../input/GROMACS/stmv.tpr',
    sif       = '../image/gromacs-2021.3.sif',
    gpudirect = True, 
    tunepme   = True,
    nstlist   = 200,
    nsteps    = 40000, 
    mpi       = tMPI(
        task  = 8, 
        omp   = 4 ))

gmx.getopt()
gmx.info()
gmx.run()
gmx.summary()
