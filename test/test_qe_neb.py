#!/usr/bin/env python3

from qe import Qe

qe = Qe(
    prefix = '../run/QE',
    input  = '../input/QE/Si_neb.in', 
    neb    = True )

qe.build()
qe.run()
qe.summary()
