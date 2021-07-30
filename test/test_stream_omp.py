#!/usr/bin/env python3

from stream_omp import StreamOmp

stream = StreamOmp(
    prefix  = '../run/STREAM/OMP' )

stream.build()
stream.make_outdir()
stream.run() 

print('\nBandwidth (MB/s):')
for kernel in ['Copy', 'Scale', 'Add', 'Triad']: 
    print(f'{kernel:8s} {stream.parse_output(kernel):.1f}')
