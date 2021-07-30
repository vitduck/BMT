#!/usr/bin/env python3

from ior import Ior

io = Ior(
    prefix = '../run/IOR' )

io.build()
io.make_outdir()
io.write_hostfile() 
