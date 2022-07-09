#!/usr/bin/env python3

from gromacs_gpu import GromacsGpu
from tmpi        import tMPI 

gmx = GromacsGpu(
    prefix    = '../run/GROMACS', 
    input     = '../input/GROMACS/stmv.tpr',
    gpudirect = True, 
    tunepme   = True,
    nstlist   = 200,
    nsteps    = 40000, 
    mpi       = tMPI( 
        task  = 8, 
        omp   = 2) )

gmx.getopt()
gmx.info()
gmx.download() 
gmx.build()
gmx.run()
gmx.summary()
