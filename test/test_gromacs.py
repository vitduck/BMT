#!/usr/bin/env python3

from gromacs import Gromacs

gmx = Gromacs(
    prefix = '../run/GROMACS', 
    input  = '../input/GROMACS/stmv.tpr', 
    nsteps = 60000 ) 

gmx.info()
gmx.build()
gmx.run()
gmx.summary()
