#!/usr/bin/env python3

from ior import Ior

ior = Ior(
    prefix = '../run/IOR', 
    ntasks = 8 )

ior.info()
ior.build()
ior.run() 
ior.summary()
