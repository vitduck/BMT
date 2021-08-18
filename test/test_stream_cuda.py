#!/usr/bin/env python3

from stream_cuda import StreamCuda

stream = StreamCuda(prefix = '../run/STREAM/CUDA')

stream.build()
stream.mkoutdir()
stream.run() 
stream.summary()
