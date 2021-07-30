#!/usr/bin/env python3

import collections

from stream_omp import StreamOmp

stream = StreamOmp(
    prefix = '../run/STREAM/OMP' )

stream.build()
stream.make_outdir() 

result = collections.defaultdict(dict)

# scan affinity/thread 
for affinity in ['close', 'spread']: 
    for thread in [1, 2, 4, 8, 16, 24, 32, 40]: 
        stream.affinity = affinity
        stream.thread   = thread 

        stream.run() 
        
        result[affinity][thread] = stream.parse_output('Triad')

# summary 
print('\nBandwidth (MB/s):')
print(f'{"#thread":<12} {"close":<12} {"spread":<12}')
for thread in [1, 2, 4, 8, 16, 24, 32, 40]: 
    print(
        f'{thread:<12d}' 
        f'{result["close" ][thread]:<12.1f}' 
        f'{result["spread"][thread]:<12.1f}' )
