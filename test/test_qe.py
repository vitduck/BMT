#!/usr/bin/env python3

from qe import Qe

qe = Qe(
    prefix = '../run/QE',
    input  = '../input/QE/Si_512.in', 
    mpi    = [ 
        'lib'     : 'impi', 
        'affiniy' : 'scatter', 
        'verbose' : 1 
    ],  
    count = 3 
)

qe.info()
qe.build()
qe.run()
qe.summary()
