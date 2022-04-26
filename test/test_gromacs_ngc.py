#!/usr/bin/env python3

from gromacs_gpu import GromacsGpu
from tmpi        import tMPI 

gmx = GromacsGpu(
    prefix    = '../run/GROMACS', 
    input     = '../input/GROMACS/water_1536.tpr',
    sif       = '../image/gromacs-2021.3.sif',
    gpudirect = True, 
    tunepme   = True,
    nsteps    = 20000, 
    mpi       = tMPI(
        task  = 8, 
        omp   = 4 ))

gmx.info()
gmx.run()
gmx.summary()
