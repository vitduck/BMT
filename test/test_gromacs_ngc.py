#!/usr/bin/env python3

from gromacs import Gromacs

gmx = Gromacs(
    prefix = '../run/GROMACS', 
    input  = '../input/GROMACS/stmv.tpr', 
    sif    = '../image/gromacs-2020_2.sif',
    nsteps = 4000) 

gmx.build()
gmx.run()
gmx.summary()
