#!/usr/bin/env python3

from nvidia import Nvidia

test = Nvidia(
    prefix         = '.', 
    gpu_per_socket = [1,0] , 
    thread         = 4, 
    sif            = 'hello.sif' )

test.debug() 
