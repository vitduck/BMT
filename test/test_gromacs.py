#!/usr/bin/env python3

from gromacs import Gromacs

gmx = Gromacs(
    prefix = '../run/GROMACS', 
    input  = '../input/GROMACS/stmv.tpr', 
    nsteps = 20000 ) 

gmx.build()
gmx.run()
gmx.summary()
