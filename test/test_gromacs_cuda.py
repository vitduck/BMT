#!/usr/bin/env python3

from gromacs_cuda import GromacsCuda
from tmpi         import tMPI 

gmx = GromacsCuda(
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
