#!/usr/bin/env python3

from stream_omp import StreamOmp

stream = StreamOmp(
    prefix = '../run/STREAM/OMP' )

stream.build()

# scan affinity/thread 
for affinity in ['close', 'spread']: 
    for thread in [1, 2, 4, 8, 16, 24, 32, 40]: 
        stream.affinity = affinity
        stream.thread   = thread 

        stream.run() 

stream.summary() 
