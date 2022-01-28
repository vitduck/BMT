#!/usr/bin/env python3

from cpu        import cpu_info
from stream_omp import StreamOmp

stream = StreamOmp(
    prefix = '../run/STREAM/OMP' )

threads = [1, 2]
ncores  = int(stream.cpu['CPUs'])

stream.info() 
stream.build()

for i in range(1, int(ncores/4)+1, 1): 
    threads.append(4*i)

# scan affinity/thread 
for affinity in ['close', 'spread']: 
    for thread in threads: 
        stream.affinity = affinity
        stream.thread   = thread 

        stream.run() 

stream.summary() 
