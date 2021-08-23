#!/usr/bin/env python3

from qe import Qe

qe = Qe(
    prefix = '../run/QE', 
    input  = '../input/QE/Si.in', 
    sif    = '../images/QE-6.7.sif')

qe.build()
qe.run()
qe.summary()
