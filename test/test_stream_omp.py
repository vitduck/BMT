#!/usr/bin/env python3

from cpu        import cpu_info
from stream_omp import StreamOmp

stream = StreamOmp(
    prefix = '../run/STREAM/OMP' )

threads = [1, 2]
ncores  = int(stream.host['CPUs'])

stream.info() 
stream.download()
stream.build()

for i in range(1, int(ncores/4)+1, 1): 
    threads.append(4*i)

# scan affinity/thread 
for affinity in ['close', 'spread']: 
    for omp in threads: 
        stream.affinity = affinity
        stream.omp      = omp

        stream.run() 

stream.summary() 
