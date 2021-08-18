#!/usr/bin/env python3

from gromacs import Gromacs

gmx = Gromacs(
    prefix = '../run/GROMACS', 
    input  = '../input/GROMACS/stmv.tpr', 
    nsteps = 10000 ) 

gmx.build()
gmx.mkoutdir()
gmx.run()
gmx.summary()
