#!/usr/bin/env python3

from pprint import pprint 
from qe import Qe

qe = Qe(
    prefix = '../run/QE', 
    input  = '../input/QE/Ausurf.in' )

#  qe.debug() 

qe.build()
qe.make_outdir()
qe.write_hostfile() 
qe.run()
