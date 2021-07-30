#!/usr/bin/env python3

from pprint  import pprint 
from gromacs import Gromacs

gmx = Gromacs(
    prefix = '../run/GROMACS', 
    input  = '../input/GROMACS/stmv.tpr' )

gmx.build()
gmx.make_outdir()
gmx.write_hostfile() 
gmx.run()
