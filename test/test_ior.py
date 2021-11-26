#!/usr/bin/env python3

from ior import Ior

ior = Ior(
    prefix = '../run/IOR' )

ior.build()
ior.run() 
ior.summary()
