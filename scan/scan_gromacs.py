#!/usr/bin/env python3

from gromacs import Gromacs

gmx = Gromacs(
    prefix = '../run/GROMACS', 
    input  = '../input/GROMACS/stmv.tpr', 
    nsteps = 4000) 

gmx.build()

for nodes in [1, 2]: 
    for ntasks in [8, 16, 32, 40]:
        omp = 1 
        while omp <= int(40/ntasks): 
            gmx.nodes  = nodes
            gmx.ntasks = ntasks
            gmx.omp    = omp 

            gmx.run()

            omp *= 2 

gmx.summary()
