#!/usr/bin/env python3

from stream_cuda import StreamCuda

stream = StreamCuda(
    prefix = '../run/STREAM/CUDA' )

stream.build()
stream.make_outdir() 
stream.run() 

print('\nBandwidth (MB/s):')
for kernel in ['Copy', 'Mul', 'Add', 'Triad']: 
    print(f'{kernel:8s} {stream.parse_output(kernel):.1f}')
