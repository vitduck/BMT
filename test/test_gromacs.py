#!/usr/bin/env python3

from gromacs import Gromacs

gmx = Gromacs(
    prefix = '../run/GROMACS', 
    input  = '../input/GROMACS/water_1536.tpr', 
    nsteps = 4000 ) 

gmx.build()
gmx.run()
gmx.summary()
