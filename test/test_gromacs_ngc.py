#!/usr/bin/env python3

from gromacs import Gromacs

gmx = Gromacs(
    prefix = '../run/GROMACS', 
    input  = '../input/GROMACS/water_1536.tpr',
    sif    = '../image/gromacs-2021.3.sif',
    nsteps = 20000 )  

gmx.info()
gmx.run()
gmx.summary()
