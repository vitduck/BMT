#!/usr/bin/env python3

from stream_omp import StreamOmp

stream = StreamOmp(
    prefix = '../run/STREAM/OMP' )

stream.getopt() 
stream.info() 
stream.download() 
stream.build()

# scan affinity/thread 
for affinity in ['close', 'spread']: 
    omp = 4

    while omp <= int(stream.host['CPUs']): 
        stream.affinity = affinity
        stream.omp      = omp

        stream.run() 
        omp += 4 

stream.summary() 
